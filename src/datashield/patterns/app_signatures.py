"""
App Signatures Database for Data-Shield.

Maps file paths back to the software that owns them, providing the
"responsible app" column in scan results.  This is the data layer; the
matching logic lives in ``core/app_fingerprint.py``.
"""
from __future__ import annotations

from datetime import datetime

from datashield.core.models import AppSignature, AppSignaturesDB, Confidence

# ---------------------------------------------------------------------------
# Signature definitions
# ---------------------------------------------------------------------------
_SIGS: list[dict] = [
    # ── IDEs & Code Editors ──────────────────────────────────────────────
    {
        "id": "vscode",
        "display_name": "Visual Studio Code",
        "category": "ide",
        "icon": "vscode.png",
        "paths": [
            r"%APPDATA%\Code",
            r"%APPDATA%\Code - Insiders",
            r"%LOCALAPPDATA%\Programs\Microsoft VS Code",
        ],
        "process_names": ["Code.exe", "Code - Insiders.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Code\User\globalStorage", "file_patterns": ["*.json", "*.state"],
             "secret_type": "extension_tokens", "how_stored": "plaintext"},
            {"path": r"%APPDATA%\Code\User\settings.json",
             "secret_type": "user_settings_secrets", "how_stored": "plaintext"},
        ],
        "reference_urls": ["https://code.visualstudio.com/docs/editor/settings"],
    },
    {
        "id": "cursor",
        "display_name": "Cursor (AI IDE)",
        "category": "ide",
        "paths": [
            r"%APPDATA%\Cursor",
            r"%LOCALAPPDATA%\Programs\cursor",
        ],
        "process_names": ["Cursor.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Cursor\User\globalStorage",
             "secret_type": "extension_tokens", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "android_studio",
        "display_name": "Android Studio",
        "category": "ide",
        "paths": [
            r"%APPDATA%\Google\AndroidStudio*",
            r"%LOCALAPPDATA%\Google\AndroidStudio*",
        ],
        "process_names": ["studio64.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Google\AndroidStudio*\options\github.xml",
             "secret_type": "github_token", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "jetbrains_idea",
        "display_name": "JetBrains IntelliJ IDEA",
        "category": "ide",
        "paths": [r"%APPDATA%\JetBrains\IntelliJIdea*"],
        "process_names": ["idea64.exe", "idea.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\JetBrains\IntelliJIdea*\options\passwords.xml",
             "secret_type": "master_password_hash", "how_stored": "encrypted"},
        ],
    },
    {
        "id": "jetbrains_pycharm",
        "display_name": "JetBrains PyCharm",
        "category": "ide",
        "paths": [r"%APPDATA%\JetBrains\PyCharm*"],
        "process_names": ["pycharm64.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\JetBrains\PyCharm*\options\passwords.xml",
             "secret_type": "master_password_hash", "how_stored": "encrypted"},
        ],
    },
    {
        "id": "jetbrains_webstorm",
        "display_name": "JetBrains WebStorm",
        "category": "ide",
        "paths": [r"%APPDATA%\JetBrains\WebStorm*"],
        "process_names": ["webstorm64.exe"],
    },
    {
        "id": "jetbrains_rider",
        "display_name": "JetBrains Rider",
        "category": "ide",
        "paths": [r"%APPDATA%\JetBrains\Rider*"],
        "process_names": ["rider64.exe"],
    },
    # ── Version Control ───────────────────────────────────────────────────
    {
        "id": "git",
        "display_name": "Git",
        "category": "vcs",
        "paths": [
            r"%USERPROFILE%\.gitconfig",
            r"%USERPROFILE%\.git-credentials",
            r"%APPDATA%\Git",
        ],
        "process_names": ["git.exe", "git-credential-manager.exe", "git-credential-wincred.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.git-credentials",
             "secret_type": "git_credentials", "how_stored": "plaintext"},
            {"path": r"%USERPROFILE%\.gitconfig",
             "secret_type": "git_config_tokens", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "github_cli",
        "display_name": "GitHub CLI",
        "category": "vcs",
        "paths": [
            r"%APPDATA%\gh",
            r"%LOCALAPPDATA%\gh",
        ],
        "process_names": ["gh.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\gh\hosts.yml",
             "secret_type": "github_oauth_token", "how_stored": "plaintext"},
        ],
        "reference_urls": ["https://cli.github.com/manual/gh_auth"],
    },
    {
        "id": "github_desktop",
        "display_name": "GitHub Desktop",
        "category": "vcs",
        "paths": [
            r"%APPDATA%\GitHub Desktop",
            r"%LOCALAPPDATA%\GitHubDesktop",
        ],
        "process_names": ["GitHubDesktop.exe"],
    },
    {
        "id": "gitlab_cli",
        "display_name": "GitLab CLI (glab)",
        "category": "vcs",
        "paths": [r"%APPDATA%\glab-cli"],
        "process_names": ["glab.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\glab-cli\config.yml",
             "secret_type": "gitlab_pat", "how_stored": "plaintext"},
        ],
    },
    # ── Cloud CLIs ────────────────────────────────────────────────────────
    {
        "id": "aws_cli",
        "display_name": "AWS CLI",
        "category": "cloud",
        "paths": [r"%USERPROFILE%\.aws"],
        "process_names": ["aws.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.aws\credentials",
             "secret_type": "aws_credentials", "how_stored": "plaintext"},
            {"path": r"%USERPROFILE%\.aws\config",
             "secret_type": "aws_config", "how_stored": "plaintext"},
        ],
        "reference_urls": ["https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html"],
    },
    {
        "id": "gcloud",
        "display_name": "Google Cloud CLI (gcloud)",
        "category": "cloud",
        "paths": [r"%APPDATA%\gcloud"],
        "process_names": ["gcloud.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\gcloud\credentials.db",
             "secret_type": "gcp_oauth_tokens", "how_stored": "sqlite"},
            {"path": r"%APPDATA%\gcloud\application_default_credentials.json",
             "secret_type": "gcp_adc", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "azure_cli",
        "display_name": "Azure CLI (az)",
        "category": "cloud",
        "paths": [r"%USERPROFILE%\.azure"],
        "process_names": ["az.exe", "az.cmd"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.azure\accessTokens.json",
             "secret_type": "azure_access_tokens", "how_stored": "plaintext"},
            {"path": r"%USERPROFILE%\.azure\msal_token_cache.json",
             "secret_type": "azure_msal_tokens", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "kubectl",
        "display_name": "kubectl (Kubernetes CLI)",
        "category": "cloud",
        "paths": [r"%USERPROFILE%\.kube"],
        "process_names": ["kubectl.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.kube\config",
             "secret_type": "k8s_cluster_tokens", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "terraform",
        "display_name": "HashiCorp Terraform",
        "category": "devops",
        "paths": [r"%APPDATA%\terraform.d", r"%USERPROFILE%\.terraform.d"],
        "process_names": ["terraform.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\terraform.d\credentials.tfrc.json",
             "secret_type": "terraform_cloud_tokens", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "ansible",
        "display_name": "Ansible",
        "category": "devops",
        "paths": [r"%USERPROFILE%\.ansible"],
        "process_names": ["ansible.exe", "ansible-playbook.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.ansible\vault_pass",
             "secret_type": "ansible_vault_password", "how_stored": "plaintext"},
        ],
    },
    # ── Containers ────────────────────────────────────────────────────────
    {
        "id": "docker",
        "display_name": "Docker Desktop",
        "category": "container",
        "paths": [r"%USERPROFILE%\.docker"],
        "process_names": ["Docker Desktop.exe", "dockerd.exe", "com.docker.backend.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.docker\config.json",
             "secret_type": "docker_registry_auth", "how_stored": "base64"},
        ],
        "reference_urls": ["https://docs.docker.com/reference/cli/docker/login/"],
    },
    # ── Browsers ──────────────────────────────────────────────────────────
    {
        "id": "chrome",
        "display_name": "Google Chrome",
        "category": "browser",
        "paths": [r"%LOCALAPPDATA%\Google\Chrome\User Data"],
        "process_names": ["chrome.exe"],
        "credential_locations": [
            {"path": r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data",
             "secret_type": "saved_passwords", "how_stored": "sqlite+dpapi"},
            {"path": r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies",
             "secret_type": "session_cookies", "how_stored": "sqlite+dpapi"},
            {"path": r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State",
             "secret_type": "encryption_key", "how_stored": "dpapi"},
        ],
    },
    {
        "id": "edge",
        "display_name": "Microsoft Edge",
        "category": "browser",
        "paths": [r"%LOCALAPPDATA%\Microsoft\Edge\User Data"],
        "process_names": ["msedge.exe"],
        "credential_locations": [
            {"path": r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data",
             "secret_type": "saved_passwords", "how_stored": "sqlite+dpapi"},
            {"path": r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cookies",
             "secret_type": "session_cookies", "how_stored": "sqlite+dpapi"},
        ],
    },
    {
        "id": "firefox",
        "display_name": "Mozilla Firefox",
        "category": "browser",
        "paths": [r"%APPDATA%\Mozilla\Firefox\Profiles"],
        "process_names": ["firefox.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Mozilla\Firefox\Profiles\*\logins.json",
             "secret_type": "saved_passwords", "how_stored": "nss_encrypted"},
            {"path": r"%APPDATA%\Mozilla\Firefox\Profiles\*\cookies.sqlite",
             "secret_type": "session_cookies", "how_stored": "sqlite"},
        ],
    },
    {
        "id": "brave",
        "display_name": "Brave Browser",
        "category": "browser",
        "paths": [r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"],
        "process_names": ["brave.exe"],
        "credential_locations": [
            {"path": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Login Data",
             "secret_type": "saved_passwords", "how_stored": "sqlite+dpapi"},
        ],
    },
    {
        "id": "opera",
        "display_name": "Opera",
        "category": "browser",
        "paths": [r"%APPDATA%\Opera Software\Opera Stable"],
        "process_names": ["opera.exe"],
    },
    {
        "id": "vivaldi",
        "display_name": "Vivaldi",
        "category": "browser",
        "paths": [r"%LOCALAPPDATA%\Vivaldi\User Data"],
        "process_names": ["vivaldi.exe"],
    },
    {
        "id": "comet_browser",
        "display_name": "Comet Browser (Perplexity)",
        "category": "browser",
        "paths": [r"%LOCALAPPDATA%\Comet\User Data"],
        "process_names": ["comet.exe"],
        "credential_locations": [
            {"path": r"%LOCALAPPDATA%\Comet\User Data\Default\Cookies",
             "secret_type": "session_cookies", "how_stored": "sqlite+dpapi"},
        ],
    },
    # ── Package Managers ─────────────────────────────────────────────────
    {
        "id": "npm",
        "display_name": "NPM / Node.js",
        "category": "package_manager",
        "paths": [r"%USERPROFILE%\.npmrc", r"%APPDATA%\npm"],
        "process_names": ["node.exe", "npm.cmd", "npx.cmd"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.npmrc",
             "secret_type": "npm_auth_token", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "pip_pypi",
        "display_name": "pip / PyPI",
        "category": "package_manager",
        "paths": [r"%APPDATA%\pip", r"%USERPROFILE%\.pypirc"],
        "process_names": ["pip.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.pypirc",
             "secret_type": "pypi_token", "how_stored": "plaintext"},
        ],
    },
    # ── SSH ───────────────────────────────────────────────────────────────
    {
        "id": "openssh",
        "display_name": "OpenSSH",
        "category": "network",
        "paths": [r"%USERPROFILE%\.ssh"],
        "process_names": ["ssh.exe", "sshd.exe", "ssh-agent.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.ssh", "file_patterns": ["id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"],
             "secret_type": "ssh_private_key", "how_stored": "plaintext_or_passphrase"},
            {"path": r"%USERPROFILE%\.ssh\known_hosts",
             "secret_type": "ssh_host_keys", "how_stored": "plaintext"},
        ],
    },
    # ── API Testing / Development ─────────────────────────────────────────
    {
        "id": "postman",
        "display_name": "Postman",
        "category": "api_tool",
        "paths": [r"%APPDATA%\Postman"],
        "process_names": ["Postman.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Postman\files", "file_patterns": ["*.json"],
             "secret_type": "api_keys_env_vars", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "insomnia",
        "display_name": "Insomnia",
        "category": "api_tool",
        "paths": [r"%APPDATA%\Insomnia"],
        "process_names": ["Insomnia.exe"],
    },
    # ── Databases ─────────────────────────────────────────────────────────
    {
        "id": "dbeaver",
        "display_name": "DBeaver",
        "category": "database",
        "paths": [r"%APPDATA%\DBeaverData"],
        "process_names": ["dbeaver.exe", "dbeaver-ce.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\DBeaverData\workspace6\.metadata\.plugins\org.jkiss.dbeaver.core",
             "file_patterns": ["data-sources.json"],
             "secret_type": "database_credentials", "how_stored": "blowfish_encrypted"},
        ],
    },
    {
        "id": "tableplus",
        "display_name": "TablePlus",
        "category": "database",
        "paths": [r"%APPDATA%\TablePlus"],
        "process_names": ["TablePlus.exe"],
    },
    # ── AI / LLM Tools ────────────────────────────────────────────────────
    {
        "id": "antigravity",
        "display_name": "Antigravity",
        "category": "ai_tool",
        "paths": [
            r"%APPDATA%\Antigravity",
            r"%LOCALAPPDATA%\Antigravity",
            r"%USERPROFILE%\.gemini",
            r"%APPDATA%\.gemini",
        ],
        "process_names": ["antigravity.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Antigravity", "file_patterns": ["*.json", "*.db"],
             "secret_type": "ai_session_tokens", "how_stored": "encrypted"},
            {"path": r"%USERPROFILE%\.gemini\antigravity\brain", "file_patterns": ["*.md", "*.json"],
             "secret_type": "session_context", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "gemini_ai",
        "display_name": "Gemini CLI / Desktop",
        "category": "ai_tool",
        "paths": [
            r"%APPDATA%\Gemini",
            r"%LOCALAPPDATA%\Google\Gemini",
            r"%USERPROFILE%\.gemini",
        ],
        "process_names": ["gemini.exe", "Gemini.exe"],
    },
    {
        "id": "claude_ai",
        "display_name": "Claude AI CLI / Desktop",
        "category": "ai_tool",
        "paths": [
            r"%APPDATA%\Claude",
            r"%USERPROFILE%\.claude",
        ],
        "process_names": ["claude.exe", "Claude.exe"],
    },
    {
        "id": "ollama",
        "display_name": "Ollama",
        "category": "ai_tool",
        "paths": [r"%USERPROFILE%\.ollama"],
        "process_names": ["ollama.exe"],
    },
    {
        "id": "lm_studio",
        "display_name": "LM Studio",
        "category": "ai_tool",
        "paths": [r"%USERPROFILE%\.cache\lm-studio"],
        "process_names": ["LM Studio.exe"],
    },
    {
        "id": "claude_desktop",
        "display_name": "Claude Desktop (Anthropic)",
        "category": "ai_tool",
        "paths": [r"%APPDATA%\Claude"],
        "process_names": ["Claude.exe"],
    },
    {
        "id": "openai_cli",
        "display_name": "OpenAI CLI / SDK",
        "category": "ai_tool",
        "paths": [r"%USERPROFILE%\.openai"],
        "process_names": [],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.openai", "file_patterns": ["*.json", "credentials"],
             "secret_type": "openai_api_key", "how_stored": "plaintext"},
        ],
    },
    # ── VPN / Network ─────────────────────────────────────────────────────
    {
        "id": "openvpn",
        "display_name": "OpenVPN",
        "category": "network",
        "paths": [
            r"C:\Program Files\OpenVPN\config",
            r"%USERPROFILE%\OpenVPN\config",
        ],
        "process_names": ["openvpn.exe", "openvpn-gui.exe"],
        "credential_locations": [
            {"path": r"C:\Program Files\OpenVPN\config", "file_patterns": ["*.ovpn", "*.conf"],
             "secret_type": "vpn_credentials", "how_stored": "plaintext"},
        ],
    },
    {
        "id": "wireguard",
        "display_name": "WireGuard",
        "category": "network",
        "paths": [r"C:\Program Files\WireGuard"],
        "process_names": ["wireguard.exe", "wg.exe"],
        "credential_locations": [
            {"path": r"C:\Program Files\WireGuard", "file_patterns": ["*.conf"],
             "secret_type": "wireguard_private_key", "how_stored": "plaintext"},
        ],
    },
    # ── Email Clients ─────────────────────────────────────────────────────
    {
        "id": "thunderbird",
        "display_name": "Mozilla Thunderbird",
        "category": "email",
        "paths": [r"%APPDATA%\Thunderbird\Profiles"],
        "process_names": ["thunderbird.exe"],
    },
    # ── Password Managers ─────────────────────────────────────────────────
    {
        "id": "bitwarden",
        "display_name": "Bitwarden",
        "category": "password_manager",
        "paths": [r"%APPDATA%\Bitwarden"],
        "process_names": ["Bitwarden.exe"],
    },
    {
        "id": "keepass",
        "display_name": "KeePass",
        "category": "password_manager",
        "paths": [
            r"%APPDATA%\KeePass",
            r"%USERPROFILE%\Documents",
        ],
        "process_names": ["KeePass.exe", "KeePassXC.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\KeePass", "file_patterns": ["*.kdbx"],
             "secret_type": "keepass_database", "how_stored": "encrypted"},
        ],
    },
    # ── CI/CD ─────────────────────────────────────────────────────────────
    {
        "id": "github_actions",
        "display_name": "GitHub Actions Runner",
        "category": "cicd",
        "paths": [r"%USERPROFILE%\actions-runner"],
        "process_names": ["Runner.Listener.exe"],
    },
    {
        "id": "gitlab_runner",
        "display_name": "GitLab Runner",
        "category": "cicd",
        "paths": [r"C:\GitLab-Runner"],
        "process_names": ["gitlab-runner.exe"],
        "credential_locations": [
            {"path": r"C:\GitLab-Runner\config.toml",
             "secret_type": "gitlab_runner_token", "how_stored": "plaintext"},
        ],
    },
    # ── Communication ─────────────────────────────────────────────────────
    {
        "id": "slack",
        "display_name": "Slack",
        "category": "communication",
        "paths": [r"%APPDATA%\Slack"],
        "process_names": ["slack.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Slack\storage", "file_patterns": ["*.json"],
             "secret_type": "slack_tokens", "how_stored": "electron_storage"},
        ],
    },
    {
        "id": "discord",
        "display_name": "Discord",
        "category": "communication",
        "paths": [r"%APPDATA%\discord"],
        "process_names": ["Discord.exe", "DiscordCanary.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\discord\Local Storage\leveldb",
             "secret_type": "discord_token", "how_stored": "leveldb"},
        ],
    },
    {
        "id": "teams",
        "display_name": "Microsoft Teams",
        "category": "communication",
        "paths": [r"%APPDATA%\Microsoft\Teams"],
        "process_names": ["Teams.exe"],
        "credential_locations": [
            {"path": r"%APPDATA%\Microsoft\Teams\Local Storage\leveldb",
             "secret_type": "teams_tokens", "how_stored": "leveldb"},
        ],
    },
    # ── Infrastructure ────────────────────────────────────────────────────
    {
        "id": "helm",
        "display_name": "Helm (Kubernetes)",
        "category": "devops",
        "paths": [r"%APPDATA%\helm"],
        "process_names": ["helm.exe"],
    },
    {
        "id": "pulumi",
        "display_name": "Pulumi",
        "category": "devops",
        "paths": [r"%USERPROFILE%\.pulumi"],
        "process_names": ["pulumi.exe"],
        "credential_locations": [
            {"path": r"%USERPROFILE%\.pulumi\credentials.json",
             "secret_type": "pulumi_access_token", "how_stored": "plaintext"},
        ],
    },
    # ── Windows Native ───────────────────────────────────────────────────
    {
        "id": "windows_credential_manager",
        "display_name": "Windows Credential Manager",
        "category": "windows",
        "paths": [],
        "process_names": [],
        "credential_locations": [
            {"path": "HKCU\\Software\\Microsoft\\Internet Explorer\\IntelliForms",
             "secret_type": "ie_saved_passwords", "how_stored": "dpapi"},
        ],
    },
    {
        "id": "wsl",
        "display_name": "Windows Subsystem for Linux",
        "category": "windows",
        "paths": [r"%LOCALAPPDATA%\Packages\CanonicalGroupLimited*"],
        "process_names": ["wsl.exe", "bash.exe"],
    },
]

# ---------------------------------------------------------------------------
# Build the AppSignaturesDB singleton
# ---------------------------------------------------------------------------

_app_signatures_list: list[AppSignature] = []
for _s in _SIGS:
    _app_signatures_list.append(AppSignature(
        id                  = _s["id"],
        display_name        = _s["display_name"],
        category            = _s.get("category", "other"),
        paths               = _s.get("paths", []),
        process_names       = _s.get("process_names", []),
        registry_keys       = _s.get("registry_keys", []),
        credential_locations= _s.get("credential_locations", []),
        icon                = _s.get("icon"),
        confidence          = Confidence.HIGH,
        notes               = _s.get("notes"),
        reference_urls      = _s.get("reference_urls", []),
        first_seen          = datetime(2026, 4, 28),
        last_updated        = datetime(2026, 4, 28),
        last_updated_source = "manual",
    ))

APP_SIGNATURES_DB = AppSignaturesDB(
    version           = "1.0.0",
    timestamp         = datetime(2026, 4, 28),
    apps              = _app_signatures_list,
    total_apps        = len(_app_signatures_list),
    last_update_check = datetime(2026, 4, 28),
)


def get_db() -> AppSignaturesDB:
    """Return the active AppSignaturesDB instance."""
    return APP_SIGNATURES_DB


def get_signature(app_id: str) -> AppSignature | None:
    """Look up a single AppSignature by app ID."""
    return APP_SIGNATURES_DB.find_by_id(app_id)
