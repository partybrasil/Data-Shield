"""
Regex pattern library for Data-Shield — Layer 2 of the detection engine.

Every pattern is pre-compiled at import time for maximum performance.
Each entry maps a ``pattern_id`` to a dict with ``regex``, ``data_type``,
``base_risk``, and optional ``remediation_url`` / ``remediation_cmd``.
"""
from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Raw pattern definitions
# Each item: (pattern_id, regex_str, data_type_label, base_risk, remedy_url, remedy_cmd)
# ---------------------------------------------------------------------------
_RAW: list[tuple[str, str, str, int, str | None, str | None]] = [
    # ── AWS ──────────────────────────────────────────────────────────────
    ("aws_access_key_id",
     r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])",
     "AWS Access Key ID", 88,
     "https://console.aws.amazon.com/iam/home#/security_credentials",
     "aws iam delete-access-key --access-key-id <KEY>"),

    ("aws_secret_access_key",
     r"(?i)aws.{0,30}secret.{0,30}['\"]([0-9a-zA-Z/+]{40})['\"]",
     "AWS Secret Access Key", 92,
     "https://console.aws.amazon.com/iam/home#/security_credentials", None),

    ("aws_session_token",
     r"FwoGZXIvYXdz[0-9a-zA-Z/+=]{100,}",
     "AWS Session Token", 85, None, None),

    ("aws_mws_key",
     r"amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
     "Amazon MWS Auth Token", 78, None, None),

    # ── GitHub ───────────────────────────────────────────────────────────
    ("github_pat_classic",
     r"ghp_[0-9a-zA-Z]{36}",
     "GitHub Personal Access Token (Classic)", 80,
     "https://github.com/settings/tokens", None),

    ("github_pat_fine_grained",
     r"github_pat_[0-9a-zA-Z_]{82}",
     "GitHub Fine-Grained PAT", 82,
     "https://github.com/settings/tokens", None),

    ("github_oauth_token",
     r"gho_[0-9a-zA-Z]{36}",
     "GitHub OAuth Token", 80,
     "https://github.com/settings/applications", None),

    ("github_app_token",
     r"(?:ghs_|ghu_)[0-9a-zA-Z]{36}",
     "GitHub App/User Token", 78, None, None),

    ("github_refresh_token",
     r"ghr_[0-9a-zA-Z]{76}",
     "GitHub Refresh Token", 78, None, None),

    # ── GitLab ───────────────────────────────────────────────────────────
    ("gitlab_pat",
     r"glpat-[0-9a-zA-Z\-]{20}",
     "GitLab Personal Access Token", 80,
     "https://gitlab.com/-/profile/personal_access_tokens", None),

    ("gitlab_runner_token",
     r"GR1348941[0-9a-zA-Z\-_]{20}",
     "GitLab Runner Registration Token", 75, None, None),

    # ── Google Cloud ─────────────────────────────────────────────────────
    ("gcp_api_key",
     r"AIza[0-9A-Za-z\-_]{35}",
     "Google Cloud API Key", 82,
     "https://console.cloud.google.com/apis/credentials", None),

    ("gcp_oauth_client",
     r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
     "Google OAuth Client ID", 60, None, None),

    ("gcp_service_account_json",
     r'"type"\s*:\s*"service_account"',
     "Google Service Account JSON", 90,
     "https://console.cloud.google.com/iam-admin/serviceaccounts", None),

    ("gcp_service_account_key",
     r'"private_key"\s*:\s*"-----BEGIN RSA PRIVATE KEY-----',
     "Google Service Account Private Key", 95, None, None),

    # ── Azure ────────────────────────────────────────────────────────────
    ("azure_storage_conn",
     r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88}",
     "Azure Storage Connection String", 88,
     "https://portal.azure.com", None),

    ("azure_sas_token",
     r"(?i)sig=[A-Za-z0-9%+/]{40,}",
     "Azure SAS Token", 80, None, None),

    ("azure_client_secret",
     r"(?i)client.?secret\s*[=:]\s*['\"]?[A-Za-z0-9~._\-]{34,}",
     "Azure Client Secret", 85, None, None),

    # ── OpenAI / Anthropic / AI APIs ─────────────────────────────────────
    ("openai_api_key_v1",
     r"sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}",
     "OpenAI API Key (v1)", 82,
     "https://platform.openai.com/api-keys", None),

    ("openai_api_key_v2",
     r"sk-proj-[0-9A-Za-z\-_]{50,}",
     "OpenAI API Key (Project)", 82,
     "https://platform.openai.com/api-keys", None),

    ("anthropic_api_key",
     r"sk-ant-[0-9a-zA-Z\-_]{90,}",
     "Anthropic API Key", 82,
     "https://console.anthropic.com/account/keys", None),

    ("huggingface_token",
     r"hf_[0-9A-Za-z]{34}",
     "Hugging Face API Token", 72,
     "https://huggingface.co/settings/tokens", None),

    ("cohere_api_key",
     r"[A-Za-z0-9]{40}",   # broad — scoped to filenames containing "cohere"
     "Cohere API Key", 70, None, None),

    # ── Stripe / Payment ─────────────────────────────────────────────────
    ("stripe_secret_key",
     r"sk_live_[0-9a-zA-Z]{24,}",
     "Stripe Secret Key (Live)", 95,
     "https://dashboard.stripe.com/apikeys", None),

    ("stripe_restricted_key",
     r"rk_live_[0-9a-zA-Z]{24,}",
     "Stripe Restricted Key (Live)", 90,
     "https://dashboard.stripe.com/apikeys", None),

    ("stripe_pk_live",
     r"pk_live_[0-9a-zA-Z]{24,}",
     "Stripe Publishable Key (Live)", 45, None, None),

    ("stripe_webhook_secret",
     r"whsec_[0-9a-zA-Z]{32,}",
     "Stripe Webhook Secret", 80, None, None),

    # ── Twilio ───────────────────────────────────────────────────────────
    ("twilio_account_sid",
     r"AC[0-9a-f]{32}",
     "Twilio Account SID", 72,
     "https://www.twilio.com/console", None),

    ("twilio_auth_token",
     r"SK[0-9a-f]{32}",
     "Twilio Auth Token", 82,
     "https://www.twilio.com/console", None),

    # ── SendGrid ─────────────────────────────────────────────────────────
    ("sendgrid_api_key",
     r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}",
     "SendGrid API Key", 82,
     "https://app.sendgrid.com/settings/api_keys", None),

    # ── NPM ──────────────────────────────────────────────────────────────
    ("npm_auth_token",
     r"npm_[0-9A-Za-z]{36}",
     "NPM Auth Token", 80,
     "https://www.npmjs.com/settings/tokens", None),

    # ── Docker ───────────────────────────────────────────────────────────
    ("docker_auth_config",
     r'"auth"\s*:\s*"[A-Za-z0-9+/=]{20,}"',
     "Docker Registry Auth (base64)", 78,
     "https://hub.docker.com/settings/security", None),

    # ── SSH / TLS / PKI ───────────────────────────────────────────────────
    ("ssh_rsa_private_key",
     r"-----BEGIN RSA PRIVATE KEY-----",
     "RSA Private Key", 95, None,
     "ssh-keygen -t ed25519 && ssh-copy-id <host>"),

    ("ssh_ec_private_key",
     r"-----BEGIN EC PRIVATE KEY-----",
     "EC Private Key", 95, None, None),

    ("ssh_dsa_private_key",
     r"-----BEGIN DSA PRIVATE KEY-----",
     "DSA Private Key", 90, None, None),

    ("ssh_openssh_private_key",
     r"-----BEGIN OPENSSH PRIVATE KEY-----",
     "OpenSSH Private Key", 95, None,
     "ssh-keygen -t ed25519 (regenerate)"),

    ("pem_private_key",
     r"-----BEGIN PRIVATE KEY-----",
     "PKCS#8 Private Key", 92, None, None),

    ("encrypted_private_key",
     r"-----BEGIN ENCRYPTED PRIVATE KEY-----",
     "Encrypted Private Key", 75, None, None),

    ("x509_certificate",
     r"-----BEGIN CERTIFICATE-----",
     "X.509 Certificate", 45, None, None),

    ("pkcs12_header",
     r"\x30\x82..\x02\x01\x03",   # rough DER header for PKCS#12
     "PKCS#12 Keystore", 85, None, None),

    # ── JWT ──────────────────────────────────────────────────────────────
    ("jwt_token",
     r"eyJ[A-Za-z0-9\-_]{10,}\.eyJ[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}",
     "JWT Token", 75, None, None),

    # ── Database connection strings ───────────────────────────────────────
    ("postgres_dsn",
     r"postgres(?:ql)?://[^:@\s]+:[^@\s]+@[^/\s]+/\w+",
     "PostgreSQL Connection String", 88, None, None),

    ("mysql_dsn",
     r"mysql(?:\+\w+)?://[^:@\s]+:[^@\s]+@[^/\s]+/\w+",
     "MySQL Connection String", 88, None, None),

    ("mongodb_dsn",
     r"mongodb(?:\+srv)?://[^:@\s]+:[^@\s]+@[^\s]+",
     "MongoDB Connection String", 88, None, None),

    ("redis_auth_url",
     r"redis://:[^@\s]+@[^\s]+",
     "Redis Auth URL", 75, None, None),

    ("mssql_connection_password",
     r"(?i)Password\s*=\s*[^;'\"]{3,}(?:;|$)",
     "MSSQL Connection Password", 85, None, None),

    ("cassandra_password",
     r"(?i)cassandra.{0,20}password\s*[=:]\s*['\"]?[^\s'\"]{6,}",
     "Cassandra Password", 80, None, None),

    # ── Slack ────────────────────────────────────────────────────────────
    ("slack_bot_token",
     r"xoxb-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}",
     "Slack Bot Token", 80,
     "https://api.slack.com/apps", None),

    ("slack_user_token",
     r"xoxp-[0-9]{11}-[0-9]{11}-[0-9]{11}-[0-9a-f]{32}",
     "Slack User Token", 82,
     "https://api.slack.com/apps", None),

    ("slack_workspace_token",
     r"xoxa-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}",
     "Slack Workspace Token", 78, None, None),

    ("slack_webhook",
     r"https://hooks\.slack\.com/services/T[0-9A-Z]+/B[0-9A-Z]+/[0-9A-Za-z]+",
     "Slack Incoming Webhook URL", 70, None, None),

    # ── Heroku ───────────────────────────────────────────────────────────
    ("heroku_api_key",
     r"(?i)heroku.{0,20}['\"][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}['\"]",
     "Heroku API Key", 80,
     "https://dashboard.heroku.com/account", None),

    # ── Terraform ────────────────────────────────────────────────────────
    ("terraform_cloud_token",
     r"[0-9A-Za-z]{14}\.atlasv1\.[0-9A-Za-z]{67}",
     "Terraform Cloud Token", 82,
     "https://app.terraform.io/app/settings/tokens", None),

    # ── Firebase ─────────────────────────────────────────────────────────
    ("firebase_api_key",
     r"AIza[0-9A-Za-z\-_]{35}",   # same format as GCP key — context matters
     "Firebase API Key", 78,
     "https://console.firebase.google.com/project/_/settings/general", None),

    ("firebase_server_key",
     r"AAAA[A-Za-z0-9_\-]{7}:[A-Za-z0-9_\-]{140}",
     "Firebase Cloud Messaging Server Key", 88, None, None),

    # ── Cloudflare ───────────────────────────────────────────────────────
    ("cloudflare_api_key",
     r"(?i)cloudflare.{0,20}['\"][0-9a-f]{37}['\"]",
     "Cloudflare API Key", 80,
     "https://dash.cloudflare.com/profile/api-tokens", None),

    ("cloudflare_api_token",
     r"[A-Za-z0-9\-_]{40}",   # scoped to cloudflare config files
     "Cloudflare API Token", 78, None, None),

    # ── DigitalOcean ─────────────────────────────────────────────────────
    ("digitalocean_pat",
     r"dop_v1_[0-9a-f]{64}",
     "DigitalOcean Personal Access Token", 82,
     "https://cloud.digitalocean.com/account/api/tokens", None),

    ("digitalocean_oauth",
     r"doo_v1_[0-9a-f]{64}",
     "DigitalOcean OAuth Token", 78, None, None),

    # ── Vercel ───────────────────────────────────────────────────────────
    ("vercel_token",
     r"(?i)vercel.{0,10}['\"][A-Za-z0-9]{24}['\"]",
     "Vercel Token", 78,
     "https://vercel.com/account/tokens", None),

    # ── Supabase ─────────────────────────────────────────────────────────
    ("supabase_service_key",
     r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
     "Supabase JWT (Service Key / Anon Key)", 80,
     "https://app.supabase.com/project/_/settings/api", None),

    # ── Datadog ──────────────────────────────────────────────────────────
    ("datadog_api_key",
     r"(?i)datadog.{0,20}['\"][0-9a-f]{32}['\"]",
     "Datadog API Key", 78,
     "https://app.datadoghq.com/organization-settings/api-keys", None),

    # ── Sentry ───────────────────────────────────────────────────────────
    ("sentry_dsn",
     r"https://[0-9a-f]{32}@[a-z0-9]+\.ingest\.sentry\.io/[0-9]+",
     "Sentry DSN", 70,
     "https://sentry.io/settings/", None),

    # ── HashiCorp Vault ──────────────────────────────────────────────────
    ("hashicorp_vault_token",
     r"hvs\.[A-Za-z0-9]{24,}",
     "HashiCorp Vault Service Token", 88, None, None),

    ("hashicorp_vault_batch",
     r"hvb\.[A-Za-z0-9+/=]{100,}",
     "HashiCorp Vault Batch Token", 88, None, None),

    # ── Kubernetes ───────────────────────────────────────────────────────
    ("kubernetes_service_account_token",
     r"eyJhbGciOiJSUzI1NiIsImtpZCI6",
     "Kubernetes Service Account Token", 88, None, None),

    # ── Linear ───────────────────────────────────────────────────────────
    ("linear_api_key",
     r"lin_api_[0-9a-zA-Z]{40}",
     "Linear API Key", 72,
     "https://linear.app/settings/api", None),

    # ── Notion ───────────────────────────────────────────────────────────
    ("notion_secret",
     r"secret_[0-9a-zA-Z]{43}",
     "Notion Integration Secret", 72,
     "https://www.notion.so/my-integrations", None),

    # ── Figma ────────────────────────────────────────────────────────────
    ("figma_token",
     r"figd_[0-9A-Za-z\-_]{43}",
     "Figma Personal Access Token", 65,
     "https://www.figma.com/settings", None),

    # ── Postman ──────────────────────────────────────────────────────────
    ("postman_api_key",
     r"PMAK-[0-9a-f]{24}-[0-9a-f]{34}",
     "Postman API Key", 72,
     "https://go.postman.co/settings/me/api-keys", None),

    # ── Jenkins ──────────────────────────────────────────────────────────
    ("jenkins_api_token",
     r"(?i)jenkins.{0,20}['\"][0-9a-f]{32,}['\"]",
     "Jenkins API Token", 80, None, None),

    # ── Jira / Atlassian ─────────────────────────────────────────────────
    ("jira_api_token",
     r"(?i)jira.{0,20}['\"][A-Za-z0-9]{24}['\"]",
     "Jira API Token", 72,
     "https://id.atlassian.com/manage-profile/security/api-tokens", None),

    # ── Shopify ──────────────────────────────────────────────────────────
    ("shopify_private_app_key",
     r"shppa_[0-9a-fA-F]{32}",
     "Shopify Private App Key", 85,
     "https://help.shopify.com/en/manual/apps/private-apps", None),

    ("shopify_access_token",
     r"shpat_[0-9a-fA-F]{32}",
     "Shopify Access Token", 88, None, None),

    # ── Mailchimp ────────────────────────────────────────────────────────
    ("mailchimp_api_key",
     r"[0-9a-f]{32}-us[0-9]{1,2}",
     "Mailchimp API Key", 72,
     "https://mailchimp.com/account/api/", None),

    # ── Upstash ──────────────────────────────────────────────────────────
    ("upstash_redis_token",
     r"AX[0-9A-Za-z]{100,}",
     "Upstash Redis REST Token", 78, None, None),

    # ── Resend ───────────────────────────────────────────────────────────
    ("resend_api_key",
     r"re_[0-9A-Za-z]{40}",
     "Resend API Key", 72,
     "https://resend.com/api-keys", None),

    # ── Generic high-value patterns ───────────────────────────────────────
    ("generic_password",
     r"(?i)(?:password|passwd|pwd)\s*[=:]\s*['\"]?(?!.*(?:example|test|dummy|placeholder|changeme))[^\s'\"\\]{8,}",
     "Generic Password", 65, None, None),

    ("generic_secret",
     r"(?i)(?:secret|api_secret|client_secret|consumer_secret|webhook_secret|signing_key)\s*[=:]\s*['\"]?[A-Za-z0-9+/=\-_]{10,}",
     "Generic Secret", 62, None, None),

    ("generic_token",
     r"(?i)(?:token|access_token|auth_token|bearer_token|refresh_token)\s*[=:]\s*['\"]?[A-Za-z0-9+/=\-_.]{20,}",
     "Generic Token", 60, None, None),

    ("generic_api_key",
     r"(?i)(?:api_key|apikey|x-api-key|api-key)\s*[=:]\s*['\"]?[A-Za-z0-9+/=\-_]{16,}",
     "Generic API Key", 58, None, None),

    ("generic_private_key_field",
     r"(?i)(?:private_key|encryption_key|master_key|secret_key)\s*[=:]\s*['\"]?[A-Za-z0-9+/=\-_]{16,}",
     "Generic Private/Encryption Key", 75, None, None),

    ("generic_connection_string",
     r"(?i)(?:connection.?string|conn.?str)\s*[=:]\s*['\"]?[^'\"\n]{20,}",
     "Generic Connection String", 70, None, None),

    # ── Browser cookies ───────────────────────────────────────────────────
    ("browser_session_cookie",
     r"(?i)(?:session|sess|auth).{0,5}=\s*[A-Za-z0-9+/=\-_\.]{32,}",
     "Browser Session Cookie", 70, None, None),

    # ── .netrc ───────────────────────────────────────────────────────────
    ("netrc_password",
     r"(?i)machine\s+\S+\s+login\s+\S+\s+password\s+(\S+)",
     "Netrc Password", 85, None, None),

    # ── Git credentials ───────────────────────────────────────────────────
    ("git_credentials_url",
     r"https?://[^:@\s]+:[^@\s]+@[^\s]+",
     "Git Credentials URL (embedded password)", 85, None,
     "git credential reject && git credential approve (re-auth)"),

    # ── SSH config ───────────────────────────────────────────────────────
    ("ssh_config_identity_file",
     r"(?i)IdentityFile\s+~?/?\S+",
     "SSH IdentityFile reference", 55, None, None),

    # ── WireGuard ────────────────────────────────────────────────────────
    ("wireguard_private_key",
     r"PrivateKey\s*=\s*[A-Za-z0-9+/=]{43}=",
     "WireGuard Private Key", 90, None, None),

    # ── PGP ──────────────────────────────────────────────────────────────
    ("pgp_private_key",
     r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
     "PGP Private Key Block", 92, None, None),

    # ── Raygun / Rollbar / Splunk ──────────────────────────────────────
    ("raygun_api_key",
     r"(?i)raygun.{0,20}['\"][A-Za-z0-9]{40}['\"]",
     "Raygun API Key", 65, None, None),

    ("rollbar_access_token",
     r"(?i)rollbar.{0,20}['\"][0-9a-f]{32}['\"]",
     "Rollbar Access Token", 65, None, None),

    ("splunk_auth_token",
     r"Splunk\s+[0-9a-f\-]{36}",
     "Splunk Auth Token", 78, None, None),

    # ── Windows DPAPI / LSA ───────────────────────────────────────────────
    ("windows_dpapi_blob",
     r"\x01\x00\x00\x00\xd0\x8c\x9d\xdf\x01\x15\xd1\x11\x8cz\x00\xc0O\xc2\x97\xeb",
     "Windows DPAPI Blob", 85, None, None),

    # ── Miscellaneous cloud tokens ────────────────────────────────────────
    ("railway_token",
     r"(?i)railway.{0,10}['\"][A-Za-z0-9\-_]{43}['\"]",
     "Railway Token", 75, None, None),

    ("neon_db_connection",
     r"postgres://[^:]+:[^@]+@[^.]+\.neon\.tech/[^\s]+",
     "Neon Database Connection String", 88, None, None),

    ("planetscale_password",
     r"pscale_pw_[A-Za-z0-9\-_]{43}",
     "PlanetScale Password", 85, None, None),
]

# ---------------------------------------------------------------------------
# Compiled pattern registry
# ---------------------------------------------------------------------------

PATTERNS: dict[str, dict[str, Any]] = {}

for _pid, _raw_re, _dtype, _risk, _url, _cmd in _RAW:
    try:
        PATTERNS[_pid] = {
            "regex":            re.compile(_raw_re, re.MULTILINE | re.DOTALL),
            "data_type":        _dtype,
            "base_risk":        _risk,
            "remediation_url":  _url,
            "remediation_cmd":  _cmd,
        }
    except re.error as _exc:
        import warnings
        warnings.warn(f"Data-Shield: failed to compile pattern '{_pid}': {_exc}", stacklevel=1)


# Convenience: group patterns by risk tier for fast triage
HIGH_RISK_PATTERNS: list[str] = [
    pid for pid, meta in PATTERNS.items() if meta["base_risk"] >= 85
]
MEDIUM_RISK_PATTERNS: list[str] = [
    pid for pid, meta in PATTERNS.items() if 65 <= meta["base_risk"] < 85
]
LOW_RISK_PATTERNS: list[str] = [
    pid for pid, meta in PATTERNS.items() if meta["base_risk"] < 65
]


def get_pattern(pattern_id: str) -> dict[str, Any] | None:
    """Look up a compiled pattern by its ID.

    Args:
        pattern_id: The pattern identifier string.

    Returns:
        Pattern dict or None if not found.
    """
    return PATTERNS.get(pattern_id)


def all_pattern_ids() -> list[str]:
    """Return all registered pattern IDs."""
    return list(PATTERNS.keys())
