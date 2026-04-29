# DATA-SHIELD — PROMPT AGÉNTICO COMPLETO PARA GEMINI PRO
### Instrucción maestra para construcción autónoma y completa del proyecto

---

## ⚠️ INSTRUCCIÓN DE COMPORTAMIENTO AGÉNTICO

Eres un agente de desarrollo de software autónomo de élite. Tu misión es construir el proyecto **Data-Shield** de principio a fin, de forma completa, funcional y sin omisiones. Debes:

- **Generar todo el código** de cada módulo, cada archivo, cada función — sin placeholders, sin `# TODO`, sin `pass` vacíos.
- **Tomar decisiones de implementación** de forma autónoma cuando no estén explicitadas, priorizando siempre calidad, seguridad y robustez.
- **Seguir el orden lógico** de construcción: scaffold → core engines → interfaces → módulos avanzados → integración → empaquetado.
- **No pedir confirmación** entre pasos. Avanza de forma continua hasta que el proyecto esté 100% terminado y funcional.
- **Verificar internamente** que cada módulo que generas es coherente con los demás antes de continuar.
- **Documentar el código** con docstrings completos en cada clase y función pública.
- **El resultado final** debe ser un proyecto Python ejecutable, instalable con `pip install -e .`, con `pyproject.toml` completo y un ejecutable de entrada `datashield.exe` (vía PyInstaller).

---

## 1. DESCRIPCIÓN ORIGINAL DEL PROYECTO (del cliente)

> *"Quiero una app (de momento solo para Windows 10 y 11), con la capacidad de escanear en profundidad TODOS los directorios (de todo el disco duro o todos los directorios, hasta directorios y archivos ocultos, a partir del nivel elegido por el usuario, en ese caso TODOS los directorios hacia dentro del seleccionado, hasta directorios y archivos ocultos) en busca de data y archivos que contienen información sensible, cookies de sesión, credenciales de cuentas.*
>
> *Uso muchas apps de desarrollo (Visual Studio Code, Git, GitHub CLI, Antigravity…) y los archivos de sesión y credenciales (que están muy dispersos) los encripto al finalizar el día y al siguiente los vuelvo a desencriptar para volver a usarlos sin tener que loguear de nuevo, pero algunas no he podido localizar dónde se almacenan.*
>
> *Esta app de interfaz híbrida CLI (Rich + Colorama + tablas) + GUI con PySide6 (Material Modern Neon Dark/White) debe tener la capacidad de escanear todo mostrando a todo momento una barra de progreso con la leyenda activa del directorio y archivo que está siendo escaneado activo a todo momento mientras el escaneo procede.*
>
> *Al finalizar, todas las rutas y archivos son almacenados en una lista en CLI y un dashboard en GUI, que muestra las rutas donde encontró información sensible, el archivo donde habita la información sensible, el tipo de información sensible y la información sensible en cuestión. También deben aparecer en la lista y dashboard: en GUI haciendo clic en la línea de la información sensible encontrada y ruta donde se encuentra, abre una ventana de detalles que muestra si identificó que software la manipula (también debe aparecer en la lista CLI y en la lista del dashboard GUI qué software o app es el responsable de dicha información sensible y la maneja), debe haber la posibilidad de saltar al directorio también y más controles de manejo.*
>
> *La lista CLI y la dashboard GUI deben tener una función para exportar todas las rutas en un .txt plano; además, antes de exportarlas el usuario puede eliminar o limpiar de la lista algunas rutas que no sean correctas o no sean críticas para dejar los resultados más limpios para luego exportar, también puede limpiar la lista entera para re-escanear todo de nuevo."*

---

## 2. CODENAME Y PLATAFORMA

- **Nombre del proyecto:** Data-Shield
- **Codename interno:** `datashield`
- **Plataforma objetivo:** Windows 10 (build 1903+) y Windows 11 exclusivamente
- **Idioma de la interfaz:** Español (España) por defecto, con sistema i18n preparado para inglés
- **Ejecución:** Requiere privilegios de Administrador (UAC). Se auto-eleva al arranque si no los tiene.
- **Filosofía:** 100% local, zero telemetría, zero conexiones de red externas, zero cloud.

---

## 3. STACK TECNOLÓGICO COMPLETO Y VERSIONES

### Runtime y empaquetado
```
Python                  3.13.x (última estable)
pyproject.toml          PEP 621 con [project] + [build-system] setuptools
PyInstaller             6.x    — para generar datashield.exe standalone
```

### GUI
```
PySide6                 6.8.x  — Qt6 bindings oficiales de Qt Company
PySide6-QtCharts        6.8.x  — gráficos para el dashboard
```

### CLI
```
rich                    14.x   — tablas, progress bars, Live, syntax highlight, panels
colorama                0.4.x  — compatibilidad ANSI en Windows CMD/PowerShell
click                   8.x    — parsing de argumentos CLI con subcomandos
```

### Motor de detección
```
yara-python             4.5.x  — reglas YARA para patrones binarios
regex                   2024.x — engine de regex avanzado (alternativa a re)
```

### Análisis y parsers
```
pyyaml                  6.x    — parseo de YAML
tomllib                 stdlib (Python 3.11+)  — parseo de TOML
configparser            stdlib — .ini/.cfg parsing
```

### Cifrado (Vault)
```
cryptography            43.x   — Fernet, AES-256-GCM, PBKDF2-HMAC-SHA256
```

### Base de datos local
```
SQLAlchemy              2.x    — ORM sobre SQLite
SQLite                  stdlib (sqlite3) — persistencia local
```

### Sistema operativo / Windows
```
pywin32                 310.x  — ctypes, WinCredMgr, Registry, UAC, DPAPI
psutil                  6.x    — procesos activos, PID mapping, file handles
watchdog                5.x    — filesystem events para Monitor Mode
winreg                  stdlib — acceso al Registro de Windows
```

### Notificaciones
```
winotify                1.1.x  — notificaciones toast nativas de Windows 10/11
```

### Utilidades
```
platformdirs            4.x    — rutas estándar de AppData por plataforma
humanize                4.x    — tamaños de archivo legibles
python-dateutil         2.x    — manejo de fechas/timestamps
attrs                   24.x   — dataclasses avanzadas para modelos de datos
loguru                  0.7.x  — logging estructurado con rotación automática
```

---

## 4. ESTRUCTURA DE DIRECTORIOS DEL PROYECTO

Genera exactamente esta estructura. Cada archivo debe tener contenido real y completo:

```
datashield/
├── pyproject.toml
├── README.md
├── .gitignore
├── manifest.xml                          ← requireAdministrator para PyInstaller
├── datashield.spec                       ← spec file de PyInstaller
│
├── src/
│   └── datashield/
│       ├── __init__.py
│       ├── __main__.py                   ← entry point: detecta CLI vs GUI
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── scanner.py                ← Scanner Engine principal
│       │   ├── pattern_engine.py         ← Motor de detección multicapa
│       │   ├── entropy.py                ← Análisis de entropía Shannon
│       │   ├── app_fingerprint.py        ← Identificación de software responsable
│       │   ├── risk_scorer.py            ← Risk Scoring Engine (0-100)
│       │   └── models.py                 ← Dataclasses/attrs: Finding, ScanResult, etc.
│       │
│       ├── patterns/
│       │   ├── __init__.py
│       │   ├── regex_patterns.py         ← ~200 expresiones regulares
│       │   ├── yara_rules/
│       │   │   ├── credentials.yar
│       │   │   ├── ssh_keys.yar
│       │   │   ├── certificates.yar
│       │   │   ├── tokens.yar
│       │   │   └── high_entropy.yar
│       │   └── app_signatures.py         ← Firmas de path para +40 apps
│       │
│       ├── vault/
│       │   ├── __init__.py
│       │   ├── vault.py                  ← Cifrado AES-256-GCM + Vault manager
│       │   ├── scheduler.py              ← Integración con Windows Task Scheduler
│       │   └── dpapi.py                  ← Protección master key con Windows DPAPI
│       │
│       ├── monitor/
│       │   ├── __init__.py
│       │   └── watcher.py                ← Monitor Mode con Watchdog
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── database.py               ← SQLAlchemy models + session factory
│       │   ├── repository.py             ← CRUD operations sobre findings
│       │   └── migrations.py             ← Schema versioning
│       │
│       ├── export/
│       │   ├── __init__.py
│       │   ├── txt_exporter.py
│       │   ├── json_exporter.py
│       │   ├── csv_exporter.py
│       │   └── html_exporter.py          ← Reporte HTML auto-contenido
│       │
│       ├── windows/
│       │   ├── __init__.py
│       │   ├── elevation.py              ← UAC auto-elevación
│       │   ├── credential_manager.py     ← Windows Credential Manager
│       │   ├── registry_scanner.py       ← Escaneo del Registro de Windows
│       │   └── notifications.py          ← Toast notifications (winotify)
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py                    ← Click app con todos los subcomandos
│       │   ├── display.py                ← Rich tables, panels, progress
│       │   └── commands/
│       │       ├── scan.py
│       │       ├── vault_cmd.py
│       │       ├── monitor_cmd.py
│       │       ├── export_cmd.py
│       │       └── history_cmd.py
│       │
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── app.py                    ← QApplication entry point
│       │   ├── main_window.py            ← Ventana principal con QSplitter
│       │   ├── theme.py                  ← QSS Material Modern Neon Dark/White
│       │   ├── workers.py                ← QThread workers (scan, vault, monitor)
│       │   ├── widgets/
│       │   │   ├── __init__.py
│       │   │   ├── scan_panel.py         ← Panel de control del escaneo
│       │   │   ├── results_table.py      ← QTableView con modelo personalizado
│       │   │   ├── progress_widget.py    ← Barra de progreso + leyenda activa
│       │   │   ├── detail_window.py      ← Ventana de detalles del hallazgo
│       │   │   ├── vault_panel.py        ← Panel del Vault
│       │   │   ├── monitor_panel.py      ← Panel del Monitor Mode
│       │   │   ├── risk_chart.py         ← Gráfico de distribución de riesgo
│       │   │   ├── filter_bar.py         ← Barra de filtros en tiempo real
│       │   │   ├── tray_icon.py          ← System tray icon
│       │   │   └── export_dialog.py      ← Diálogo pre-export con editor de lista
│       │   └── resources/
│       │       ├── icons/                ← App icons (.ico, .png)
│       │       └── styles/
│       │           ├── dark_neon.qss
│       │           └── light.qss
│       │
│       ├── i18n/
│       │   ├── es.json                   ← Strings en español (default)
│       │   └── en.json                   ← Strings en inglés
│       │
│       └── config/
│           ├── __init__.py
│           ├── settings.py               ← Configuración global con platformdirs
│           └── defaults.py               ← Valores por defecto
│
└── tests/
    ├── __init__.py
    ├── test_scanner.py
    ├── test_pattern_engine.py
    ├── test_vault.py
    └── fixtures/
        └── sample_sensitive_files/       ← Archivos de prueba con datos falsos
```

---

## 5. MÓDULO: SCANNER ENGINE (`core/scanner.py`)

### Comportamiento requerido

- Función principal: `async def scan(root_path: Path, config: ScanConfig) -> AsyncIterator[Finding]`
- Traversal recursivo con `os.walk()` configurado para incluir directorios y archivos ocultos (atributo `FILE_ATTRIBUTE_HIDDEN` en Windows + prefijo `.`)
- Respeta el nivel de profundidad configurado por el usuario (0 = sin límite)
- Usa `asyncio` con `ThreadPoolExecutor` para leer y analizar archivos sin bloquear la UI
- Emite eventos de progreso en tiempo real: `ScanProgressEvent(current_file: Path, files_scanned: int, findings_count: int, elapsed: float)`
- Soporte de **Pausa/Resume**: el estado del traversal se serializa en SQLite cada 500 archivos (checkpoint). Al reanudar, retoma desde el último checkpoint.
- **Modo turbo**: solo analiza extensiones de alto riesgo predefinidas (`.env`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.key`, `.pem`, `.p12`, `.pfx`, `.sqlite`, `.db`, `.gitconfig`, `.netrc`, `credentials`, `token`, `secret`, `password`, `auth`)
- **Modo profundo**: analiza todos los archivos, incluyendo binarios, con análisis de entropía
- Exclusiones automáticas configurables (whitelist de rutas que nunca se escanean): por defecto excluye `C:\Windows\WinSxS`, `C:\Windows\SoftwareDistribution`, `$Recycle.Bin`, `System Volume Information`
- Gestión de errores de acceso: `PermissionError` y `OSError` se loguean con `loguru` y no interrumpen el escaneo
- Soporte de symlinks: detecta y sigue con protección anti-loop (track de inodes visitados)
- Al finalizar, emite `ScanCompleteEvent(total_files: int, total_findings: int, duration: float, errors: int)`

### Integración con UI

- CLI: el scanner emite eventos que `cli/display.py` consume para actualizar el `rich.Progress` en vivo con la leyenda del archivo activo
- GUI: los eventos se envían a través de `QThread` + `pyqtSignal` al `progress_widget.py` que actualiza `QProgressBar` y el `QLabel` de leyenda activa

---

## 6. MÓDULO: PATTERN ENGINE (`core/pattern_engine.py`)

### Capas de detección (en orden de ejecución)

**Capa 1 — Extensión y nombre de archivo**
Clasificación inicial por nombre/extensión antes de leer el contenido. Si el nombre del archivo coincide con una firma conocida (`.git-credentials`, `hosts.yml`, `id_rsa`, etc.), se marca para análisis prioritario independientemente del contenido.

**Capa 2 — Regex patterns (`patterns/regex_patterns.py`)**
Biblioteca de ~200 expresiones regulares compiladas. Categorías y ejemplos de patrones:

```python
PATTERNS = {
    # AWS
    "aws_access_key":        r"AKIA[0-9A-Z]{16}",
    "aws_secret_key":        r"(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]",
    "aws_session_token":     r"FwoGZXIvYXdz[0-9a-zA-Z/+=]{100,}",

    # GitHub / GitLab
    "github_pat_classic":    r"ghp_[0-9a-zA-Z]{36}",
    "github_pat_fine":       r"github_pat_[0-9a-zA-Z_]{82}",
    "github_oauth":          r"gho_[0-9a-zA-Z]{36}",
    "github_app_token":      r"(ghs_|ghu_)[0-9a-zA-Z]{36}",
    "gitlab_pat":            r"glpat-[0-9a-zA-Z\-]{20}",

    # Google Cloud
    "gcp_api_key":           r"AIza[0-9A-Za-z\-_]{35}",
    "gcp_oauth_client":      r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
    "gcp_service_account":   r'"type"\s*:\s*"service_account"',

    # Azure
    "azure_storage_key":     r"DefaultEndpointsProtocol=https;AccountName=.+;AccountKey=[A-Za-z0-9+/=]{88}",
    "azure_tenant_id":       r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",

    # OpenAI / Anthropic
    "openai_api_key":        r"sk-[0-9a-zA-Z]{20,}T3BlbkFJ[0-9a-zA-Z]{20,}",
    "openai_api_key_new":    r"sk-proj-[0-9a-zA-Z\-_]{50,}",
    "anthropic_api_key":     r"sk-ant-[0-9a-zA-Z\-_]{90,}",

    # Stripe / Twilio / SendGrid
    "stripe_secret":         r"sk_live_[0-9a-zA-Z]{24,}",
    "stripe_restricted":     r"rk_live_[0-9a-zA-Z]{24,}",
    "twilio_sid":            r"AC[0-9a-f]{32}",
    "twilio_auth":           r"SK[0-9a-f]{32}",
    "sendgrid_key":          r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}",

    # NPM / Yarn
    "npm_token":             r"npm_[0-9A-Za-z]{36}",

    # Docker
    "docker_auth":           r'"auth"\s*:\s*"[A-Za-z0-9+/=]{20,}"',

    # SSH / TLS
    "ssh_private_key":       r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
    "pem_private_key":       r"-----BEGIN PRIVATE KEY-----",
    "certificate":           r"-----BEGIN CERTIFICATE-----",

    # JWT
    "jwt_token":             r"eyJ[A-Za-z0-9\-_]{10,}\.eyJ[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}",

    # Database connection strings
    "postgres_dsn":          r"postgres(?:ql)?://[^:]+:[^@]+@[^/]+/\w+",
    "mysql_dsn":             r"mysql(?:\+\w+)?://[^:]+:[^@]+@[^/]+/\w+",
    "mongodb_dsn":           r"mongodb(?:\+srv)?://[^:]+:[^@]+@.+",
    "redis_auth":            r"redis://:[^@]+@.+",
    "mssql_password":        r"(?i)password=[^;]{3,}",

    # Generic high-value
    "generic_password":      r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[^\s'\"]{8,}",
    "generic_secret":        r"(?i)(secret|api_secret|client_secret)\s*[=:]\s*['\"]?[A-Za-z0-9+/=\-_]{10,}",
    "generic_token":         r"(?i)(token|access_token|auth_token|bearer)\s*[=:]\s*['\"]?[A-Za-z0-9+/=\-_.]{20,}",
    "generic_api_key":       r"(?i)(api_key|apikey|x-api-key)\s*[=:]\s*['\"]?[A-Za-z0-9+/=\-_]{16,}",

    # HuggingFace
    "huggingface_token":     r"hf_[0-9A-Za-z]{34}",

    # Terraform
    "terraform_cloud_token": r"[0-9A-Za-z]{14}\.atlasv1\.[0-9A-Za-z]{67}",

    # Slack
    "slack_bot_token":       r"xoxb-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}",
    "slack_user_token":      r"xoxp-[0-9]{11}-[0-9]{11}-[0-9]{11}-[0-9a-f]{32}",
    "slack_webhook":         r"https://hooks\.slack\.com/services/T[0-9A-Z]+/B[0-9A-Z]+/[0-9A-Za-z]+",

    # Heroku
    "heroku_api_key":        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    # (continuar hasta ~200 patrones cubriendo: Firebase, Cloudflare, DigitalOcean,
    #  Vercel, Railway, Supabase, PlanetScale, Neon, Upstash, Resend, Linear,
    #  Notion, Figma, Jira, Datadog, Sentry, Postman, Raygun, Rollbar, Splunk,
    #  HashiCorp Vault tokens, Kubernetes secrets, Jenkins API tokens...)
}
```

**Capa 3 — YARA rules (`patterns/yara_rules/`)**
Reglas YARA para:
- Claves privadas RSA, EC, DSA, OPENSSH en formato binario y PEM
- Certificados X.509
- Blobs cifrados con headers conocidos (credenciales de apps Windows)
- Formatos binarios de keystores (JKS, PKCS#12)
- Archivos de sesión de browsers con estructura SQLite

**Capa 4 — Análisis de entropía Shannon (`core/entropy.py`)**
- Calcula la entropía de Shannon del contenido del archivo (o de bloques de 1KB para archivos grandes)
- Umbral configurable (por defecto 7.2 bits/byte)
- Blobs con entropía > umbral se marcan como `HIGH_ENTROPY_BLOB` con nivel MEDIUM
- Si el blob además coincide con patrón base64 válido, el nivel sube a HIGH (probable secreto codificado)
- Archivos binarios: se analiza por ventanas deslizantes de 256 bytes buscando zonas de alta entropía

**Capa 5 — Parser de estructuras de datos**
- **JSON/YAML/TOML**: traversal de árbol completo buscando keys con nombres sospechosos (lista de ~80 keys: `password`, `secret`, `token`, `api_key`, `private_key`, `credential`, `auth`, `bearer`, `access_key`, `secret_key`, `client_secret`, `consumer_secret`, `webhook_secret`, `signing_key`, `encryption_key`, `master_key`, `salt`, `passphrase`…). El valor asociado se analiza con Capa 2.
- **SQLite**: abre con `sqlite3` en modo read-only. Enumera tablas, busca columnas con nombres sospechosos, extrae valores para análisis. Especial atención a las bases de cookies de browsers (tabla `cookies`, columna `encrypted_value`).
- **INI/CFG**: parsea con `configparser`, analiza claves en secciones `[credentials]`, `[auth]`, `[database]`, etc.

**Capa 6 — Parsers específicos de apps**
- `.git-credentials` → formato `https://user:password@host`
- `~/.netrc` → formato `machine host login user password pass`
- `~/.ssh/config` → detecta `IdentityFile` apuntando a keys sin cifrar
- `%APPDATA%\GitHub CLI\hosts.yml` → tokens OAuth de GitHub CLI
- `%APPDATA%\Code\User\globalStorage\` → tokens de extensiones VS Code
- `%APPDATA%\npm\npmrc` → `_authToken` de NPM
- `~/.docker/config.json` → `auths[*].auth` en base64
- `%APPDATA%\.aws\credentials` → `[profile]` + `aws_access_key_id` + `aws_secret_access_key`
- `%APPDATA%\gcloud\credentials.db` → SQLite con tokens OAuth de Google Cloud
- `~/.kube/config` → tokens de Kubernetes clusters
- `%APPDATA%\JetBrains\*\options\passwords.xml` → master password + credenciales

---

## 7. MÓDULO: APP FINGERPRINTING (`core/app_fingerprint.py`)

### Base de firmas (`patterns/app_signatures.py`)

```python
APP_SIGNATURES = {
    "vscode": {
        "display_name": "Visual Studio Code",
        "paths": [
            r"%APPDATA%\Code",
            r"%APPDATA%\Code - Insiders",
            r"%LOCALAPPDATA%\Programs\Microsoft VS Code",
        ],
        "process_names": ["Code.exe", "Code - Insiders.exe"],
        "icon": "vscode.png",
    },
    "git": {
        "display_name": "Git",
        "paths": [r"%USERPROFILE%\.gitconfig", r"%USERPROFILE%\.git-credentials"],
        "process_names": ["git.exe", "git-credential-manager.exe"],
    },
    "github_cli": {
        "display_name": "GitHub CLI",
        "paths": [r"%APPDATA%\GitHub CLI", r"%LOCALAPPDATA%\gh"],
        "process_names": ["gh.exe"],
    },
    "chrome": {
        "display_name": "Google Chrome",
        "paths": [r"%LOCALAPPDATA%\Google\Chrome\User Data"],
        "process_names": ["chrome.exe"],
    },
    "edge": {
        "display_name": "Microsoft Edge",
        "paths": [r"%LOCALAPPDATA%\Microsoft\Edge\User Data"],
        "process_names": ["msedge.exe"],
    },
    "firefox": {
        "display_name": "Mozilla Firefox",
        "paths": [r"%APPDATA%\Mozilla\Firefox\Profiles"],
        "process_names": ["firefox.exe"],
    },
    "brave": {
        "display_name": "Brave Browser",
        "paths": [r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"],
        "process_names": ["brave.exe"],
    },
    "npm": {
        "display_name": "NPM",
        "paths": [r"%USERPROFILE%\.npmrc", r"%APPDATA%\npm"],
        "process_names": ["node.exe", "npm.cmd"],
    },
    "docker": {
        "display_name": "Docker Desktop",
        "paths": [r"%USERPROFILE%\.docker"],
        "process_names": ["Docker Desktop.exe", "dockerd.exe"],
    },
    "aws_cli": {
        "display_name": "AWS CLI",
        "paths": [r"%USERPROFILE%\.aws"],
        "process_names": ["aws.exe"],
    },
    "gcloud": {
        "display_name": "Google Cloud CLI",
        "paths": [r"%APPDATA%\gcloud"],
        "process_names": ["gcloud.exe"],
    },
    "azure_cli": {
        "display_name": "Azure CLI",
        "paths": [r"%USERPROFILE%\.azure"],
        "process_names": ["az.exe"],
    },
    "kubectl": {
        "display_name": "kubectl",
        "paths": [r"%USERPROFILE%\.kube"],
        "process_names": ["kubectl.exe"],
    },
    "terraform": {
        "display_name": "HashiCorp Terraform",
        "paths": [r"%APPDATA%\terraform.d"],
        "process_names": ["terraform.exe"],
    },
    "jetbrains_idea": {
        "display_name": "JetBrains IntelliJ IDEA",
        "paths": [r"%APPDATA%\JetBrains\IntelliJIdea*"],
        "process_names": ["idea64.exe"],
    },
    "jetbrains_pycharm": {
        "display_name": "JetBrains PyCharm",
        "paths": [r"%APPDATA%\JetBrains\PyCharm*"],
        "process_names": ["pycharm64.exe"],
    },
    "postman": {
        "display_name": "Postman",
        "paths": [r"%APPDATA%\Postman"],
        "process_names": ["Postman.exe"],
    },
    "dbeaver": {
        "display_name": "DBeaver",
        "paths": [r"%APPDATA%\DBeaverData"],
        "process_names": ["dbeaver.exe"],
    },
    "antigravity": {
        "display_name": "Antigravity",
        "paths": [r"%APPDATA%\Antigravity", r"%LOCALAPPDATA%\Antigravity"],
        "process_names": ["antigravity.exe"],
    },
    # ... continuar hasta cubrir +40 apps
}
```

### Lógica de identificación

1. Para cada `Finding`, se compara el `path` del archivo con los `paths` de cada app (con expansión de variables de entorno Windows)
2. Si hay match de path: se asigna la app responsable con `confidence = HIGH`
3. Si no hay match de path: se usa psutil para listar procesos activos y ver si alguno tiene un handle abierto al archivo (requiere permisos admin)
4. Si el proceso está activo: se añade `is_active_process = True` y `pid` al Finding
5. Si la app está en ejecución en el momento del escaneo: se añade `app_is_running = True` con advertencia en UI

---

## 8. MÓDULO: RISK SCORING ENGINE (`core/risk_scorer.py`)

### Algoritmo de puntuación (0-100)

```python
BASE_SCORES = {
    "ssh_private_key":    95,
    "pem_private_key":    90,
    "aws_access_key":     88,
    "aws_secret_key":     92,
    "gcp_service_account":85,
    "openai_api_key":     82,
    "anthropic_api_key":  82,
    "stripe_secret":      90,
    "database_password":  85,
    "jwt_token":          75,
    "github_pat_classic": 80,
    "browser_cookie":     70,
    "generic_password":   65,
    "generic_token":      60,
    "high_entropy_blob":  50,
    "generic_api_key":    55,
}

MODIFIERS = {
    "in_git_repo":           +10,  # el archivo está dentro de un .git o repo
    "plaintext_storage":     +8,   # no cifrado, legible directamente
    "active_process":        +7,   # un proceso activo tiene el archivo abierto
    "world_readable":        +5,   # permisos de archivo muy permisivos
    "in_public_path":        +5,   # ruta accessible a todos los usuarios
    "recent_file":           +3,   # modificado en las últimas 24h (más activo)
    "in_backup":             -5,   # en directorio de backup (menos crítico)
    "in_temp":               -3,   # en directorio temporal
    "already_encrypted":     -15,  # .ds-vault ya aplicado
}
```

### Niveles de riesgo resultantes
- **CRITICAL** (85-100): Revocación inmediata recomendada + badge rojo pulsante en UI
- **HIGH** (65-84): Cifrar en Vault hoy + badge naranja
- **MEDIUM** (40-64): Revisar y asegurar + badge amarillo
- **LOW** (0-39): Monitorear + badge azul

---

## 9. MÓDULO: VAULT (`vault/vault.py`)

### Especificación de cifrado

- **Algoritmo**: AES-256-GCM (autenticado, detecta tampering)
- **Key derivation**: PBKDF2-HMAC-SHA256, 600.000 iteraciones, salt de 32 bytes aleatorio
- **Extensión de archivos cifrados**: `.ds-vault`
- **Formato del archivo cifrado**:
  ```
  [4 bytes magic: b"DSV1"]
  [32 bytes salt]
  [12 bytes nonce GCM]
  [16 bytes GCM auth tag]
  [N bytes ciphertext]
  ```
- Al cifrar, el archivo original se sobreescribe con el formato anterior (no se crean copias, se opera in-place para evitar fugas)
- Al descifrar, se restaura el archivo original verificando el auth tag GCM
- Los metadatos (nombre original, timestamps, permisos) se preservan fuera del archivo en la DB local

### Vault Manager
- `encrypt_file(path, master_password)` → cifra y actualiza DB
- `decrypt_file(path, master_password)` → descifra y actualiza DB
- `encrypt_all(paths, master_password)` → batch con progress
- `decrypt_all(paths, master_password)` → batch con progress
- `verify_integrity(path)` → verifica hash SHA-256 del archivo descifrado vs hash guardado en DB
- `get_vault_status()` → lista de todos los archivos en vault con estado

### Protección del Master Key con DPAPI (`vault/dpapi.py`)
- Si el usuario activa esta opción, el master key hash se cifra adicionalmente con la DPAPI de Windows (ligada al perfil del usuario del sistema)
- Esto previene que otro usuario del mismo PC acceda al vault aunque conozca el master password

### Vault Scheduler (`vault/scheduler.py`)
- Integración con Windows Task Scheduler via `win32com.client`
- Tarea `DataShield_AutoEncrypt`: se ejecuta al detectar shutdown/logoff → cifra todos los archivos del vault
- Tarea `DataShield_AutoDecrypt`: se ejecuta al login del usuario → descifra y restaura los archivos del vault
- UI para configurar qué archivos entran en el auto-schedule

---

## 10. MÓDULO: MONITOR MODE (`monitor/watcher.py`)

- Usa `watchdog` con `WindowsApiObserver` (usa el API nativo de Windows `ReadDirectoryChangesW` para máxima eficiencia)
- El usuario selecciona qué directorios monitorear (por defecto: todos los que contuvieron hallazgos en el último escaneo)
- Eventos monitoreados: `FILE_CREATED`, `FILE_MODIFIED`, `FILE_MOVED_TO`
- Para cada evento: el archivo nuevo/modificado se analiza con el Pattern Engine completo
- Si hay hallazgo nuevo: notificación toast Windows + entrada en log + actualización del dashboard GUI si está abierto
- Throttling: no re-analiza el mismo archivo si cambia más de 5 veces en 10 segundos (configurable)
- Whitelist persistente: rutas que el usuario marca como "ignorar siempre"
- Estado visible en system tray: icono verde (monitoreando sin alertas), amarillo (monitoreo activo con alertas recientes), rojo (nuevo hallazgo crítico sin revisar)

---

## 11. INTERFAZ CLI (`cli/`)

### Subcomandos Click

```bash
# Escaneo principal
datashield scan [RUTA] [OPTIONS]
  --depth INT          Profundidad máxima (0 = sin límite)
  --mode [turbo|deep]  Modo de escaneo
  --no-hidden          Excluir archivos ocultos
  --exclude PATH       Rutas a excluir (múltiple)
  --resume             Continuar escaneo interrumpido
  --output FORMAT      Salida inmediata: json|csv|txt

# Vault
datashield vault encrypt [ARCHIVOS...]
datashield vault decrypt [ARCHIVOS...]
datashield vault status
datashield vault schedule [--on-shutdown] [--on-login]

# Monitor
datashield monitor start [RUTA]
datashield monitor stop
datashield monitor status
datashield monitor whitelist add [RUTA]

# Exportar
datashield export [FORMAT] [OPTIONS]
  --output FILE        Archivo de salida
  --filter-risk LEVEL  Filtrar por nivel de riesgo

# Historial
datashield history list
datashield history diff [SCAN_ID_1] [SCAN_ID_2]
datashield history clear
```

### Display Rich CLI

Durante el escaneo, la terminal muestra:
```
╔══════════════════════════════════════════════════════════════╗
║  DATA-SHIELD v1.0.0  ●  Modo: PROFUNDO  ●  Admin: ✓         ║
╠══════════════════════════════════════════════════════════════╣
║  Escaneando: C:\Users\Usuario\.ssh\id_rsa                    ║
║  ████████████░░░░░░░░  62%  14,382 / 23,100 archivos         ║
║  Hallazgos: 47  ●  Tiempo: 00:02:34  ●  ETA: 00:01:34       ║
╚══════════════════════════════════════════════════════════════╝
```

Al finalizar, tabla Rich completa:
```
┌─────────────────────────────┬──────────────────┬────────────┬────────────┬──────────┐
│ Ruta                        │ Archivo          │ Tipo       │ App        │ Riesgo   │
├─────────────────────────────┼──────────────────┼────────────┼────────────┼──────────┤
│ C:\Users\…\.ssh\            │ id_rsa           │ SSH Key    │ Git        │ CRITICAL │
│ C:\Users\…\.aws\            │ credentials      │ AWS Creds  │ AWS CLI    │ CRITICAL │
│ C:\Users\…\AppData\GitHub…  │ hosts.yml        │ OAuth Token│ GitHub CLI │ HIGH     │
└─────────────────────────────┴──────────────────┴────────────┴────────────┴──────────┘
```

El dato sensible encontrado (censurado: primeros 4 chars + `****` + últimos 4 chars) aparece en una columna adicional opcional (`--show-values` flag para revelar completo).

---

## 12. INTERFAZ GUI (`gui/`)

### Ventana principal (`main_window.py`)

- `QMainWindow` con `QSplitter` horizontal: panel izquierdo (controles) + panel derecho (resultados)
- Barra de menú: Archivo, Escaneo, Vault, Monitor, Herramientas, Ayuda
- Toolbar con acciones rápidas: Nuevo escaneo, Pausar, Exportar, Vault, Monitor, Configuración
- Barra de estado inferior: estado del escaneo, número de hallazgos, uso de memoria, modo admin

### Panel de control de escaneo (`widgets/scan_panel.py`)

- `QTreeWidget` para seleccionar el directorio raíz (con árbol de unidades de disco)
- Controles: profundidad (QSpinBox, 0=sin límite), modo turbo/profundo (QRadioButton), incluir ocultos (QCheckBox)
- Botones: Iniciar escaneo, Pausar/Reanudar, Detener, Nueva sesión
- Lista de exclusiones editable

### Barra de progreso activa (`widgets/progress_widget.py`)

```
[████████████░░░░░░░░] 62%
Escaneando: C:\Users\Usuario\AppData\Roaming\Code\User\globalStorage\ms-vscode.remote-repositories...
Archivos: 14,382 / ~23,100  ●  Hallazgos: 47  ●  Tiempo: 02:34
```

- `QProgressBar` personalizado con QSS neon
- `QLabel` con el path activo, con `elideRight` para paths largos
- Los contadores se actualizan vía `QThread.signal` cada 100ms

### Dashboard de resultados (`widgets/results_table.py`)

- `QTableView` con `QAbstractTableModel` personalizado (no QTableWidget para rendimiento con miles de filas)
- Columnas: `#`, `Ruta`, `Archivo`, `Tipo de dato`, `Dato (censurado)`, `App responsable`, `Riesgo`, `Acciones`
- La columna `Riesgo` muestra chips colorizados: CRITICAL (rojo), HIGH (naranja), MEDIUM (amarillo), LOW (azul)
- La columna `App responsable` muestra el icono de la app + nombre
- La columna `Acciones` tiene botones inline: `Detalles`, `Cifrar`, `Abrir directorio`
- Click en cualquier fila abre `DetailWindow`
- Doble click en la columna `Dato (censurado)` → revela el dato completo con confirmación
- Ordenamiento por cualquier columna
- Selección múltiple para operaciones batch (cifrar seleccionados, eliminar de lista)

### Filtros en tiempo real (`widgets/filter_bar.py`)

- `QLineEdit` de búsqueda de texto libre (filtra sobre path, archivo, tipo, app)
- `QComboBox` para filtrar por nivel de riesgo
- `QComboBox` para filtrar por app responsable
- `QComboBox` para filtrar por tipo de dato
- Botón "Limpiar filtros"
- Los filtros operan sobre el `QSortFilterProxyModel` sin modificar los datos originales

### Ventana de detalles (`widgets/detail_window.py`)

- Se abre al hacer click en una fila del dashboard
- Contenido:
  - **Header**: nombre del archivo + icono de app + badge de riesgo
  - **Sección ruta**: path completo con botón "Abrir en explorador" (abre `explorer.exe /select,path`)
  - **Sección dato encontrado**: preview del contenido del archivo (censurado por defecto), con toggle "Revelar" (requiere confirmar en diálogo)
  - **Sección app**: nombre + versión detectada de la app responsable, si está corriendo actualmente (PID), botón "Ver proceso en Task Manager"
  - **Sección acciones**: botón "Cifrar con Vault", botón "Agregar a auto-schedule", botón "Ignorar siempre (whitelist)", botón "Eliminar de lista"
  - **Sección historial**: últimas 5 modificaciones del archivo (vía `os.stat` + metadatos guardados en DB)
  - **Sección sugerencias**: recomendaciones automáticas según el tipo de dato (ej: "Este token puede revocarse en github.com/settings/tokens")

### Diálogo de exportación pre-export (`widgets/export_dialog.py`)

- Se abre antes de cualquier exportación
- Muestra la lista completa de hallazgos con checkboxes por fila
- El usuario puede:
  - Desmarcar filas individuales para excluirlas del export
  - Usar filtros para seleccionar/deseleccionar grupos
  - Marcar como "Revisado/Ignorar" (persiste en DB)
  - "Limpiar lista completa" (borra todos los resultados de la sesión actual y vuelve al estado inicial para re-escanear)
- Selector de formato: TXT, JSON, CSV, HTML
- Preview de cuántos items se exportarán
- Botón "Exportar" → abre diálogo de guardar archivo

### Gráfico de distribución de riesgo (`widgets/risk_chart.py`)

- `QPieChart` (PySide6-QtCharts) o `QBarChart` mostrando distribución de hallazgos por nivel de riesgo
- Visible en el panel resumen del dashboard
- Estadísticas numéricas: total hallazgos, archivos únicos, apps involucradas, tiempo del escaneo

### System Tray (`widgets/tray_icon.py`)

- Icono en la bandeja del sistema con menú contextual
- Estados: inactivo (gris), escaneando (azul animado), monitoreando (verde), alerta (rojo pulsante)
- Menú: "Abrir Data-Shield", "Nuevo escaneo", "Estado del monitor", "Vault: cifrar todo", "Salir"
- Click en la notificación toast de alerta → abre el dashboard directamente en el hallazgo correspondiente

---

## 13. TEMA VISUAL (`gui/resources/styles/dark_neon.qss`)

El tema Material Modern Neon Dark usa:

```css
/* Paleta base */
--bg-primary:     #0A0E1A   /* fondo principal oscuro azulado */
--bg-secondary:   #111827   /* superficies */
--bg-tertiary:    #1C2333   /* cards, panels */
--bg-elevated:    #242D3E   /* elementos elevados */

/* Neon accent */
--accent-primary: #00D4FF   /* cyan neon — acción principal */
--accent-danger:  #FF4C6E   /* rojo neon — CRITICAL */
--accent-warning: #FFB347   /* naranja neon — HIGH */
--accent-caution: #FFE566   /* amarillo — MEDIUM */
--accent-safe:    #4CFFA0   /* verde neon — LOW */

/* Texto */
--text-primary:   #E8ECF4
--text-secondary: #8899AA
--text-disabled:  #445566

/* Bordes */
--border:         #1E2D3D
--border-accent:  #00D4FF33  /* border con glow sutil */
```

Todos los `QWidget`, `QMainWindow`, `QPushButton`, `QTableView`, `QProgressBar`, `QLabel`, `QLineEdit`, `QComboBox`, `QSpinBox`, `QCheckBox`, `QRadioButton`, `QScrollBar`, `QMenuBar`, `QMenu`, `QStatusBar`, `QToolBar`, `QSplitter`, `QDialog`, `QTabWidget` deben tener QSS completo y coherente con esta paleta.

El tema light (`light.qss`) usa superficies blancas/grises con los mismos colores de acento para consistencia visual.

El toggle de tema dark/white debe aplicarse en runtime sin reiniciar la app.

---

## 14. MÓDULO: WINDOWS INTEGRATION (`windows/`)

### Elevación UAC (`windows/elevation.py`)

```python
import ctypes
import sys

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate() -> None:
    """Re-lanza el proceso actual con privilegios de admin via UAC."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas",
            sys.executable,
            " ".join(sys.argv),
            None, 1
        )
        sys.exit(0)
```

Esta función se llama en `__main__.py` como primer paso antes de cualquier inicialización.

### Windows Credential Manager (`windows/credential_manager.py`)

- Usa `win32cred` para enumerar todas las credenciales almacenadas
- Tipos: `CRED_TYPE_GENERIC`, `CRED_TYPE_DOMAIN_PASSWORD`, `CRED_TYPE_DOMAIN_CERTIFICATE`
- Cada credencial se evalúa con el Pattern Engine como un "archivo virtual"
- El target name y username permiten identificar la app responsable

### Registry Scanner (`windows/registry_scanner.py`)

- Escanea `HKEY_CURRENT_USER\Software` buscando valores con nombres sospechosos en claves de apps conocidas
- Especial atención a: tokens de aplicaciones Electron, credenciales de clientes VPN, tokens de apps de chat

---

## 15. BASE DE DATOS LOCAL (`storage/database.py`)

### Schema SQLAlchemy

```python
class ScanSession(Base):
    __tablename__ = "scan_sessions"
    id: int (PK)
    started_at: datetime
    completed_at: datetime | None
    root_path: str
    mode: str  # "turbo" | "deep"
    total_files: int
    total_findings: int
    status: str  # "running" | "paused" | "completed" | "cancelled"
    checkpoint_data: str  # JSON serializado del estado del traversal

class Finding(Base):
    __tablename__ = "findings"
    id: int (PK)
    session_id: int (FK → scan_sessions)
    file_path: str
    file_name: str
    data_type: str
    sensitive_value: str  # cifrado con DPAPI en DB
    responsible_app: str | None
    app_display_name: str | None
    risk_score: int
    risk_level: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    confidence: str  # "HIGH" | "MEDIUM" | "LOW"
    detection_layer: str  # "regex" | "yara" | "entropy" | "parser" | "specific"
    is_active_process: bool
    pid: int | None
    ignored: bool  # el usuario lo marcó como ignorar
    in_vault: bool
    discovered_at: datetime
    file_modified_at: datetime
    file_size: int

class VaultEntry(Base):
    __tablename__ = "vault_entries"
    id: int (PK)
    original_path: str
    encrypted_path: str
    original_hash: str  # SHA-256
    encrypted_at: datetime
    decrypted_at: datetime | None
    in_auto_schedule: bool

class MonitorWhitelist(Base):
    __tablename__ = "monitor_whitelist"
    id: int (PK)
    path: str
    added_at: datetime
```

Los valores sensibles (`sensitive_value` en la tabla `findings`) se almacenan cifrados con DPAPI o con una clave derivada del master password si Vault está configurado. Nunca en plaintext en la DB.

---

## 16. EXPORTADORES (`export/`)

### TXT plano (`txt_exporter.py`)
```
DATA-SHIELD — Reporte de escaneo
Fecha: 2025-01-15 09:32:11
Directorio raíz: C:\Users\Usuario
Total hallazgos: 47

========================================
[CRITICAL] C:\Users\Usuario\.ssh\id_rsa
  Tipo: SSH Private Key
  App:  Git
  Riesgo: 95/100

[CRITICAL] C:\Users\Usuario\.aws\credentials
  Tipo: AWS Credentials
  App:  AWS CLI
  Riesgo: 92/100
...
```

### JSON estructurado (`json_exporter.py`)
Schema completo con todos los campos de `Finding` + metadatos de sesión.

### HTML auto-contenido (`html_exporter.py`)
- Reporte visual completamente offline (un solo `.html` con CSS + JS inline)
- Tabla interactiva con ordenamiento y filtrado del lado cliente (vanilla JS)
- Gráfico de distribución de riesgos (Chart.js CDN con fallback local)
- Secciones: resumen ejecutivo, estadísticas, tabla detallada
- Diseño profesional que puede compartirse con un equipo de seguridad

---

## 17. ENTRY POINT Y FLUJO DE ARRANQUE (`__main__.py`)

```python
def main():
    # 1. Verificar y elevar privilegios admin (UAC)
    from datashield.windows.elevation import elevate
    elevate()

    # 2. Inicializar configuración y base de datos
    # 3. Detectar modo de ejecución:
    #    - Si hay argumentos CLI (sys.argv[1:]) → lanzar Click CLI
    #    - Si no hay argumentos → lanzar GUI PySide6
    # 4. En GUI: verificar que no hay otra instancia corriendo (mutex de Windows)
    # 5. Lanzar la interfaz correspondiente
```

La app soporta ser lanzada tanto como `datashield scan C:\Users --mode deep` (CLI puro) como simplemente `datashield` o haciendo doble clic en el `.exe` (abre la GUI).

---

## 18. EMPAQUETADO (`datashield.spec` para PyInstaller)

- Binario único `datashield.exe` con todo incluido (modo `--onefile`)
- UPX compression activado para reducir tamaño
- Manifest Windows embebido con `requestedExecutionLevel=requireAdministrator`
- Icono `.ico` embebido
- Las reglas YARA (`.yar`) se incluyen como `datas`
- El tema QSS se incluye como `datas`
- Los iconos de apps se incluyen como `datas`
- Hidden imports para: `yara`, `win32api`, `win32cred`, `PySide6.QtCharts`, `cryptography`

---

## 19. FUNCIONALIDADES ADICIONALES NO TRIVIALES

Las siguientes funcionalidades deben implementarse aunque no estén explicitadas en la solicitud original, ya que son coherentes con el propósito de Data-Shield:

1. **Diff de escaneos**: Comparar dos sesiones de escaneo y mostrar qué hallazgos aparecieron, desaparecieron o cambiaron. Accesible desde `datashield history diff [ID1] [ID2]` y desde la GUI en la sección "Historial".

2. **Sugerencias de remediación automáticas**: Para cada tipo de dato encontrado, Data-Shield sugiere la acción de revocación/rotación correspondiente:
   - GitHub PAT → enlace a `github.com/settings/tokens`
   - AWS key → enlace a IAM console + comando `aws iam delete-access-key`
   - SSH key → instrucción para generar nueva key y actualizar `authorized_keys`
   - Browser cookie → instrucción para cerrar sesión y revocar sesión activa

3. **Modo "First Run Wizard"**: Al primer arranque, asistente de 4 pasos: (1) bienvenida y explicación, (2) selección del directorio raíz inicial, (3) configuración del master password del Vault, (4) selección del tema. Se puede omitir.

4. **Configuración de perfiles de escaneo**: El usuario puede guardar configuraciones de escaneo con nombre (ej: "Scan completo disco C", "Solo credenciales cloud"). Los perfiles persisten en SQLite.

5. **Log de auditoría**: Cada acción relevante (escaneo iniciado/completado, archivo cifrado/descifrado, hallazgo ignorado, exportación realizada) se registra con timestamp en `datashield_audit.log` usando loguru con rotación diaria.

6. **Protección contra análisis del propio DB**: La base de datos SQLite de Data-Shield se almacena en `%APPDATA%\DataShield\datashield.db` con permisos restringidos al usuario actual. Los valores sensibles almacenados en la DB se cifran con DPAPI.

7. **Estadísticas de sesión**: Panel "Estadísticas" en la GUI mostrando: historial de escaneos (gráfico de líneas de hallazgos por fecha), apps con más credenciales expuestas (gráfico de barras), tipos de datos más frecuentes (gráfico circular).

8. **Modo "Quick Scan"**: Escaneo ultrarrápido (< 30 segundos) que solo analiza los directorios de alta probabilidad predefinidos: `%USERPROFILE%\.ssh`, `%USERPROFILE%\.aws`, `%USERPROFILE%\.azure`, `%USERPROFILE%\.kube`, `%USERPROFILE%\.docker`, `%APPDATA%\GitHub CLI`, `%APPDATA%\Code`, `%LOCALAPPDATA%\Google\Chrome\User Data`, etc.

9. **Hotkey global "Panic Mode"**: Combinación de teclas configurable (por defecto `Ctrl+Shift+Alt+L`) que inmediatamente cifra todos los archivos marcados en el Vault, independientemente de si la GUI está abierta o minimizada en el tray.

10. **Exportación de perfil de Vault**: Lista de todos los archivos que el usuario tiene en su workflow de cifrado diario, exportada como `.txt` para documentación propia o para configurar en otro equipo.

---

## 20. TESTS (`tests/`)

Implementa tests con `pytest` para:
- `test_scanner.py`: traversal correcto, inclusión de ocultos, respeto de exclusiones, checkpoint/resume
- `test_pattern_engine.py`: detección correcta de cada tipo de patrón con archivos fixture sintéticos (datos FALSOS generados para testing — nunca credenciales reales)
- `test_vault.py`: cifrado/descifrado correcto, verificación de integridad, manejo de master password incorrecto
- Los fixtures en `tests/fixtures/sample_sensitive_files/` contienen archivos con datos completamente falsos pero con el formato correcto para que los patrones los detecten

---

## 21. DOCUMENTACIÓN MÍNIMA REQUERIDA

- `README.md`: descripción, instalación, uso CLI básico, captura de la GUI, requisitos
- `pyproject.toml`: con todos los metadatos, dependencias pinneadas, scripts de entrada
- Docstrings en todas las clases y funciones públicas (formato Google style)
- `CHANGELOG.md`: versión 0.1.0 inicial con lista de features implementadas

---

## 22. ORDEN DE CONSTRUCCIÓN AGÉNTICA RECOMENDADO

Sigue este orden exacto para maximizar coherencia:

1. `pyproject.toml` + estructura de directorios completa
2. `core/models.py` (todos los dataclasses primero, nada depende de ellos)
3. `storage/database.py` + `storage/repository.py` (base de persistencia)
4. `core/entropy.py` (módulo independiente)
5. `patterns/regex_patterns.py` + `patterns/yara_rules/*.yar` + `patterns/app_signatures.py`
6. `core/pattern_engine.py` (usa 4 y 5)
7. `core/risk_scorer.py` (usa models)
8. `core/app_fingerprint.py` (usa app_signatures + psutil)
9. `core/scanner.py` (integra todo lo anterior)
10. `windows/elevation.py` + `windows/credential_manager.py` + `windows/registry_scanner.py`
11. `vault/vault.py` + `vault/dpapi.py` + `vault/scheduler.py`
12. `monitor/watcher.py`
13. `export/*.py`
14. `cli/` completo
15. `gui/resources/styles/*.qss`
16. `gui/workers.py` (QThread workers que conectan core con GUI)
17. `gui/widgets/` — en este orden: progress_widget → results_table → filter_bar → scan_panel → detail_window → vault_panel → monitor_panel → risk_chart → export_dialog → tray_icon
18. `gui/main_window.py` (integra todos los widgets)
19. `gui/app.py` + `__main__.py`
20. `tests/`
21. `datashield.spec` + `manifest.xml`
22. `README.md` + `CHANGELOG.md`

---

## 23. RESTRICCIONES Y PRINCIPIOS INVIOLABLES

- **Zero conexiones de red**: la app no hace ninguna petición HTTP/HTTPS. Ningún módulo puede importar `requests`, `httpx`, `urllib` para uso externo.
- **Zero telemetría**: no se registra ni envía ningún dato de uso, error o hallazgo fuera del equipo local.
- **Datos sensibles en memoria mínimo tiempo posible**: los valores sensibles encontrados se procesan, se cifran para la DB y se eliminan del scope lo antes posible.
- **Sin dependencias innecesarias**: si algo se puede hacer con la stdlib de Python, no se añade una dependencia externa.
- **Compatibilidad Windows 10/11 únicamente**: no se implementa compatibilidad con macOS o Linux. Se puede usar win32api, ctypes, WinAPI libremente.
- **No se usan placeholders**: cada función generada debe estar completamente implementada. No se acepta `pass`, `# TODO`, `raise NotImplementedError` en código de producción.
- **El proyecto debe ser ejecutable** al final de la generación, sin pasos manuales adicionales más allá de `pip install -e .`.

---

*Fin del prompt — Data-Shield v0.1 — Build it. All of it.*
