"""
Risk Scoring Engine for Data-Shield.

Computes a 0-100 risk score for each Finding based on the pattern's base
risk plus contextual modifiers (location, file permissions, active process,
etc.).  The score maps to a RiskLevel enum used throughout the UI.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

from loguru import logger

from datashield.core.models import Finding, RiskLevel

# ---------------------------------------------------------------------------
# Base scores by pattern_id
# Anything not listed defaults to 50.
# ---------------------------------------------------------------------------
BASE_SCORES: dict[str, int] = {
    "ssh_rsa_private_key":           95,
    "ssh_openssh_private_key":       95,
    "ssh_ec_private_key":            95,
    "ssh_dsa_private_key":           90,
    "pem_private_key":               92,
    "pgp_private_key":               92,
    "wireguard_private_key":         90,
    "pkcs12_keystore":               88,
    "java_keystore":                 85,
    "aws_access_key_id":             88,
    "aws_secret_access_key":         92,
    "aws_session_token":             85,
    "gcp_service_account_json":      90,
    "gcp_service_account_key":       95,
    "azure_storage_conn":            88,
    "azure_client_secret":           85,
    "stripe_secret_key":             95,
    "stripe_restricted_key":         90,
    "stripe_webhook_secret":         80,
    "openai_api_key_v1":             82,
    "openai_api_key_v2":             82,
    "anthropic_api_key":             82,
    "hashicorp_vault_token":         88,
    "hashicorp_vault_batch":         88,
    "kubernetes_service_account_token": 88,
    "database_password":             85,
    "postgres_dsn":                  88,
    "mysql_dsn":                     88,
    "mongodb_dsn":                   88,
    "mssql_connection_password":     85,
    "github_pat_classic":            80,
    "github_pat_fine_grained":       82,
    "github_oauth_token":            80,
    "github_app_token":              78,
    "gitlab_pat":                    80,
    "gitlab_runner_token":           75,
    "jwt_token":                     75,
    "slack_bot_token":               80,
    "slack_user_token":              82,
    "sendgrid_api_key":              82,
    "twilio_auth_token":             82,
    "shopify_access_token":          88,
    "shopify_private_app_key":       85,
    "firebase_server_key":           88,
    "npm_auth_token":                78,
    "docker_auth_config":            78,
    "terraform_cloud_token":         82,
    "digitalocean_pat":              82,
    "planetscale_password":          85,
    "neon_db_connection":            88,
    "netrc_password":                85,
    "git_credentials_url":           85,
    "generic_private_key_field":     75,
    "generic_connection_string":     70,
    "browser_session_cookie":        70,
    "generic_password":              65,
    "generic_secret":                62,
    "generic_token":                 60,
    "generic_api_key":               58,
    "gcp_api_key":                   78,
    "huggingface_token":             72,
    "postman_api_key":               72,
    "jenkins_api_token":             80,
    "datadog_api_key":               78,
    "heroku_api_key":                80,
    "vercel_token":                  78,
    "supabase_service_key":          80,
    "upstash_redis_token":           78,
    "linear_api_key":                72,
    "notion_secret":                 72,
    "figma_token":                   65,
    "mailchimp_api_key":             72,
    "resend_api_key":                72,
    "railway_token":                 75,
    "rollbar_access_token":          65,
    "raygun_api_key":                65,
    "splunk_auth_token":             78,
    "slack_webhook":                 70,
    "gcp_oauth_client":              60,
    "x509_certificate":              45,
    "high_entropy_blob":             50,
    "high_entropy_hex":              48,
}

# ---------------------------------------------------------------------------
# Contextual modifier keys and their point values
# ---------------------------------------------------------------------------
MODIFIERS: dict[str, int] = {
    "in_git_repo":          +10,  # inside a .git directory or tracked repo
    "plaintext_storage":    +8,   # file is readable without decryption
    "active_process":       +7,   # a running process has the file open
    "world_readable":       +5,   # file has permissive ACL / mode bits
    "in_public_path":       +5,   # path accessible to all local users
    "recent_file":          +3,   # modified in the last 24 h
    "in_backup":            -5,   # inside a backup directory
    "in_temp":              -3,   # inside a temp/cache directory
    "already_encrypted":    -15,  # .ds-vault extension present
    "encrypted_extension":  -10,  # file extension suggests encryption
}

# Paths / substrings that indicate the modifiers above
_GIT_MARKERS:    list[str] = ["\\.git\\", "/.git/", "\\.git-credentials"]
_BACKUP_MARKERS: list[str] = ["backup", "\\bak\\", ".bak", "archive"]
_TEMP_MARKERS:   list[str] = ["\\temp\\", "\\tmp\\", "\\cache\\", "\\temporary"]
_PUBLIC_MARKERS: list[str] = ["\\public\\", "\\shared\\", "\\all users\\"]


def _path_contains(path_lower: str, markers: list[str]) -> bool:
    return any(m.lower() in path_lower for m in markers)


def _is_world_readable(path: Path) -> bool:
    """Return True if the file has permissive permissions (world-readable)."""
    try:
        st = os.stat(path)
        # On Windows, check if the file is not hidden/system (simplified check)
        return bool(st.st_mode & stat.S_IROTH)
    except OSError:
        return False


def _is_recent(path: Path, hours: int = 24) -> bool:
    """Return True if the file was modified within *hours* hours."""
    try:
        import time
        mtime = os.path.getmtime(path)
        return (time.time() - mtime) < hours * 3600
    except OSError:
        return False


def compute_risk_score(
    pattern_id: str,
    file_path: str,
    *,
    is_active_process: bool = False,
    already_encrypted: bool = False,
    detection_layer: str = "regex",
) -> tuple[int, RiskLevel]:
    """
    Compute the risk score for a finding.

    Args:
        pattern_id:        The fired pattern identifier.
        file_path:         Absolute path to the file.
        is_active_process: Whether a process currently has the file open.
        already_encrypted: Whether the file is already vault-encrypted.
        detection_layer:   Which detection layer produced this finding.

    Returns:
        Tuple of ``(score: int, level: RiskLevel)`` where score is clamped 0-100.
    """
    base = BASE_SCORES.get(pattern_id, 50)
    path_lower = file_path.lower()
    path_obj   = Path(file_path)

    modifiers_applied: dict[str, int] = {}

    # ── Positive modifiers ────────────────────────────────────────────────
    if _path_contains(path_lower, _GIT_MARKERS):
        modifiers_applied["in_git_repo"] = MODIFIERS["in_git_repo"]

    if not path_lower.endswith(".ds-vault"):
        modifiers_applied["plaintext_storage"] = MODIFIERS["plaintext_storage"]

    if is_active_process:
        modifiers_applied["active_process"] = MODIFIERS["active_process"]

    if _is_world_readable(path_obj):
        modifiers_applied["world_readable"] = MODIFIERS["world_readable"]

    if _path_contains(path_lower, _PUBLIC_MARKERS):
        modifiers_applied["in_public_path"] = MODIFIERS["in_public_path"]

    if _is_recent(path_obj):
        modifiers_applied["recent_file"] = MODIFIERS["recent_file"]

    # ── Negative modifiers ────────────────────────────────────────────────
    if _path_contains(path_lower, _BACKUP_MARKERS):
        modifiers_applied["in_backup"] = MODIFIERS["in_backup"]

    if _path_contains(path_lower, _TEMP_MARKERS):
        modifiers_applied["in_temp"] = MODIFIERS["in_temp"]

    if already_encrypted or path_lower.endswith(".ds-vault"):
        modifiers_applied["already_encrypted"] = MODIFIERS["already_encrypted"]

    # ── Final score ───────────────────────────────────────────────────────
    adjustment = sum(modifiers_applied.values())
    score      = max(0, min(100, base + adjustment))
    level      = score_to_level(score)

    logger.debug(
        f"RiskScorer: {pattern_id} → base={base} adj={adjustment:+d} "
        f"final={score} ({level.value}) | mods={list(modifiers_applied.keys())}"
    )
    return score, level


def score_to_level(score: int) -> RiskLevel:
    """Map a numeric score (0-100) to a RiskLevel.

    Args:
        score: Integer risk score clamped to 0-100.

    Returns:
        Corresponding RiskLevel enum value.
    """
    if score >= 85:
        return RiskLevel.CRITICAL
    if score >= 65:
        return RiskLevel.HIGH
    if score >= 40:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def remediation_for(pattern_id: str) -> tuple[str | None, str | None]:
    """Return (remediation_url, remediation_cmd) for a pattern_id.

    Looks up from the compiled regex_patterns registry.

    Args:
        pattern_id: Pattern identifier string.

    Returns:
        Tuple ``(url, command)`` — either may be None.
    """
    from datashield.patterns.regex_patterns import PATTERNS
    meta = PATTERNS.get(pattern_id, {})
    return meta.get("remediation_url"), meta.get("remediation_cmd")
