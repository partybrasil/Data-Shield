# Data-Shield 🛡️

**Escáner de seguridad de precisión máxima** — Detección y gestión de credenciales dispersas en sistemas Windows 10/11.

> *"La precisión es su punto fuerte"* — Identifica, cataloga y cifra información sensible (credenciales, tokens, cookies, SSH keys, API keys) dispersa en cualquier directorio del sistema.

---

## 🎯 Propuesta de Valor

Después de un día de trabajo usando múltiples herramientas (VS Code, Git, GitHub CLI, Docker, AWS CLI, npm, Kubernetes, etc.), tus archivos de configuración y credenciales están dispersos en decenas de directorios distintos.

**Data-Shield soluciona esto**:
- ✅ Escanea **profundidad ilimitada** incluyendo carpetas y archivos ocultos
- ✅ Detecta información sensible con **6 capas de análisis** (regex + YARA + entropía + parsers JSON/YAML/SQLite + fingerprinting)
- ✅ Identifica **qué aplicación** maneja cada credencial (40+ apps conocidas)
- ✅ Puntúa riesgo **0-100** con matriz CRITICAL/HIGH/MEDIUM/LOW
- ✅ Cifra automáticamente con **AES-256-GCM + PBKDF2** en tu "Vault"
- ✅ Integración con **Windows Task Scheduler** para cifrado automático al apagar / descifrado al iniciar
- ✅ Monitor en **tiempo real** para nuevas credenciales
- ✅ Interfaz dual: **CLI poderosa** (Rich + Colorama) + **GUI moderna** (PySide6 Material Neon Dark/White)
- ✅ Exportación limpia: TXT, JSON, CSV, HTML interactivo

---

## 📋 Especificaciones Técnicas (Stack 2025)

### Core & Runtime
```
Python:             3.13 LTS
Packaging:          PyInstaller 6.x → datashield.exe (standalone, UAC)
Build System:       PEP 621 pyproject.toml + setuptools
Git:                GitHub + Git Hooks para pre-commit checks
```

### Detection Engines
```
Regex:              ~200 patrones compilados (AWS, GCP, Azure, OpenAI, GitHub, etc.)
YARA:               4.5.x — reglas para SSH keys, certificados, formatos binarios
Entropy:            Shannon analysis — detecta secretos cifrados/base64
Parsers:            JSON/YAML/TOML deep scan, SQLite (cookies), INI/CFG
```

### Database & Storage
```
SQLAlchemy:         2.x ORM (type-safe, modern syntax)
SQLite:             Local persistency, encrypted sensitive values (DPAPI)
Migrations:         Schema versioning with checkpoints for scan resume
Compression:        Optional SQLite compression for large scan histories
```

### GUI Framework
```
PySide6:            6.8.x (Qt 6.8) — Material Modern Neon Dark/White theme
Charts:             PySide6-QtCharts — risk distribution, statistics
QSS:                Complete stylesheet with neon accents, smooth animations
Responsive:         Works on 1920x1080 minimum, adaptive layouts
```

### CLI Framework
```
Rich:               14.x — tables, progress bars, Live rendering, syntax highlight
Colorama:           0.4.x — Windows ANSI color compatibility
Click:              8.x — CLI routing, subcommands, argument parsing
```

### Encryption & Security
```
cryptography:       43.x — Fernet, AES-256-GCM, PBKDF2-HMAC-SHA256
pywin32:            310.x — DPAPI for master key protection
ctypes:             UAC elevation, Windows API access
```

### Monitoring & Filesystem
```
watchdog:           5.x — WindowsApiObserver for filesystem events
psutil:             6.x — process enumeration, PID mapping, file handles
winotify:           1.1.x — native Windows 10/11 toast notifications
```

### Utilities
```
platformdirs:       4.x — AppData, LocalAppData paths
humanize:           4.x — human-readable file sizes, dates
loguru:             0.7.x — structured logging with daily rotation
attrs:              24.x — dataclass alternative, validation
regex:              2024.x — advanced regex engine (> re stdlib)
python-dateutil:    2.x — timezone-aware datetime handling
```

---

## 📁 Estructura del Proyecto

```
datashield/
├── pyproject.toml                    ← Build config, dependencies, scripts
├── README.md                          ← This file
├── .gitignore                         ← Sensitive files, venv, build artifacts
├── LICENSE                            ← MIT or Apache 2.0
├── CHANGELOG.md                       ← Version history, feature list
├── manifest.xml                       ← Windows manifest with UAC requireAdministrator
├── datashield.spec                    ← PyInstaller configuration
│
├── src/
│   └── datashield/
│       ├── __init__.py                ← Version, imports
│       ├── __main__.py                ← Entry point: CLI vs GUI detection + UAC elevation
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── scanner.py             ← Scanner Engine (async, progress, pause/resume)
│       │   ├── pattern_engine.py      ← 6-layer detection (regex, YARA, entropy, parsers, fingerprint)
│       │   ├── entropy.py             ← Shannon entropy analysis, high-entropy blob detection
│       │   ├── app_fingerprint.py     ← Identify which app manages credentials (40+ apps)
│       │   ├── risk_scorer.py         ← Score 0-100, map to CRITICAL/HIGH/MEDIUM/LOW
│       │   └── models.py              ← Dataclasses: Finding, ScanSession, VaultEntry, MonitorWhitelist
│       │
│       ├── patterns/
│       │   ├── __init__.py
│       │   ├── regex_patterns.py      ← Compiled regex library (~200 patterns)
│       │   ├── app_signatures.py      ← Path signatures + process names for 40+ apps
│       │   └── yara_rules/
│       │       ├── credentials.yar    ← SSH keys, private keys, certs
│       │       ├── tokens.yar         ← JWT, OAuth, API tokens
│       │       ├── certificates.yar   ← X.509 cert detection
│       │       ├── high_entropy.yar   ← Encrypted blobs
│       │       └── windows_secrets.yar ← Credential Manager, LSA secrets
│       │
│       ├── vault/
│       │   ├── __init__.py
│       │   ├── vault.py               ← AES-256-GCM encrypt/decrypt, integrity verify
│       │   ├── dpapi.py               ← DPAPI master key protection (optional)
│       │   └── scheduler.py           ← Windows Task Scheduler integration (auto-encrypt/decrypt)
│       │
│       ├── monitor/
│       │   ├── __init__.py
│       │   └── watcher.py             ← Watchdog + pattern engine for real-time detection
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── database.py            ← SQLAlchemy ORM, schema definition, session factory
│       │   ├── repository.py          ← CRUD operations: findings, scans, vault entries, whitelist
│       │   └── migrations.py          ← Schema versioning, Alembic integration (future)
│       │
│       ├── export/
│       │   ├── __init__.py
│       │   ├── txt_exporter.py        ← Plain text output
│       │   ├── json_exporter.py       ← Structured JSON with all metadata
│       │   ├── csv_exporter.py        ← Excel-compatible CSV
│       │   └── html_exporter.py       ← Self-contained HTML report with interactivity
│       │
│       ├── windows/
│       │   ├── __init__.py
│       │   ├── elevation.py           ← UAC auto-elevation via ctypes ShellExecute
│       │   ├── credential_manager.py  ← Windows Credential Manager enumeration
│       │   ├── registry_scanner.py    ← HKCU/HKLM scan for stored tokens
│       │   └── notifications.py       ← Toast notifications (winotify)
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py                 ← Click app root, subcommand routing
│       │   ├── display.py             ← Rich table formatting, progress rendering
│       │   └── commands/
│       │       ├── __init__.py
│       │       ├── scan.py            ← datashield scan [PATH] [OPTIONS]
│       │       ├── vault_cmd.py       ← datashield vault [encrypt|decrypt|status|schedule]
│       │       ├── monitor_cmd.py     ← datashield monitor [start|stop|status|whitelist]
│       │       ├── export_cmd.py      ← datashield export [format] [OPTIONS]
│       │       └── history_cmd.py     ← datashield history [list|diff|clear]
│       │
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── app.py                 ← QApplication, event loop, instance check
│       │   ├── main_window.py         ← QMainWindow + QSplitter (controls | results)
│       │   ├── theme.py               ← QSS loader, dark/light toggle
│       │   ├── workers.py             ← QThread workers for scan, vault, monitor (non-blocking)
│       │   ├── widgets/
│       │   │   ├── __init__.py
│       │   │   ├── scan_panel.py      ← Directory picker, depth, mode, exclusions
│       │   │   ├── results_table.py   ← QTableView + custom model (thousands of rows)
│       │   │   ├── progress_widget.py ← QProgressBar + active path label
│       │   │   ├── detail_window.py   ← Modal: full finding details, actions, history
│       │   │   ├── filter_bar.py      ← Real-time filters (risk, app, type, search)
│       │   │   ├── vault_panel.py     ← Encrypt/decrypt controls, batch ops
│       │   │   ├── monitor_panel.py   ← Monitor start/stop, whitelist management
│       │   │   ├── risk_chart.py      ← Pie/bar chart of risk distribution
│       │   │   ├── export_dialog.py   ← Pre-export editor: checkboxes, format picker, clean list
│       │   │   └── tray_icon.py       ← System tray with context menu, status indicator
│       │   └── resources/
│       │       ├── icons/             ← App icons, status icons, risk badges
│       │       └── styles/
│       │           ├── dark_neon.qss  ← Material Modern Neon (cyan, magenta, lime, orange)
│       │           └── light.qss      ← Material Light variant
│       │
│       ├── i18n/
│       │   ├── es.json                ← Spanish strings (default)
│       │   └── en.json                ← English strings
│       │
│       └── config/
│           ├── __init__.py
│           ├── settings.py            ← Global config, platformdirs integration
│           └── defaults.py            ← Built-in defaults for all settings
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   ← Pytest fixtures, temp dirs, fake data
│   ├── test_scanner.py               ← Traversal, pause/resume, checkpoints
│   ├── test_pattern_engine.py        ← All 6 detection layers with synthetic data
│   ├── test_vault.py                 ← Encrypt/decrypt, integrity, master password
│   ├── test_windows_integration.py   ← UAC, Credential Manager, Registry (mock)
│   └── fixtures/
│       └── sample_sensitive_files/   ← Fake but correctly-formatted test data
│
└── docs/
    ├── CONTRIBUTING.md               ← Dev setup, coding standards
    ├── ARCHITECTURE.md               ← Deep dive into each module
    ├── CLI_GUIDE.md                  ← Command reference
    └── GUI_GUIDE.md                  ← Screenshots, walkthrough
```

---

## 🚀 Instalación

### Requisitos Previos
- **Windows 10 (build 1903+) o Windows 11**
- **Python 3.13** (o 3.12 LTS)
- **Visual C++ Runtime** (incluido con Python en Windows)
- **Permisos de Administrador** (la app se auto-eleva via UAC)

### Instalación desde fuente

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/data-shield.git
cd data-shield

# Crear venv
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias + modo desarrollo
pip install -e .

# (Opcional) Instalar extras para desarrollo y tests
pip install -e ".[dev,test]"
```

### Uso

#### CLI Pura
```bash
# Escaneo básico
datashield scan C:\Users\tu-usuario

# Con opciones
datashield scan C:\Users\tu-usuario --mode deep --depth 10 --exclude C:\Users\tu-usuario\AppData\cache

# Exportar directamente a JSON
datashield scan C:\Users\tu-usuario --output json --export-file reporte.json

# Ver vault status
datashield vault status

# Cifrar archivos específicos
datashield vault encrypt C:\Users\tu-usuario\.ssh\id_rsa

# Monitor en tiempo real
datashield monitor start C:\Users\tu-usuario

# Historial de escaneos
datashield history list
datashield history diff scan_20250428_093211 scan_20250428_163515

# UPDATE APP SIGNATURES (NEW!)
datashield-admin update-signatures --source github
datashield-admin update-signatures --source local-registry
datashield-admin update-signatures --dry-run
```

#### GUI (Interfaz Gráfica)
```bash
# Lanzar GUI
datashield

# O simplemente hacer doble clic en datashield.exe
```

---

## 🔍 Capacidades de Detección

### Multi-Layer Detection (6 capas)

| Capa | Mecanismo | Ejemplos |
|------|-----------|----------|
| 1️⃣ **Extensión/Nombre** | Firmas de archivo | `.git-credentials`, `id_rsa`, `hosts.yml`, `credentials` |
| 2️⃣ **Regex Patterns** | ~200 expresiones regulares compiladas | AWS_AKIA, GitHub PAT, OpenAI sk-*, JWT, conexiones DB |
| 3️⃣ **YARA Rules** | Análisis binario | SSH keys en formato PEM/OpenSSH, certs X.509, keystores |
| 4️⃣ **Entropía Shannon** | Blobs de alta entropía (>7.2 bits/byte) | Secretos cifrados, base64 codificados, tokens binarios |
| 5️⃣ **Parsers Estructurados** | JSON/YAML/TOML/SQLite/INI parsing | Claves sospechosas en configs, cookies en Chrome/Edge/Firefox |
| 6️⃣ **Fingerprinting de Apps** | Path matching + process enumeration | Identificar si VS Code, Git, Docker, Kubernetes, etc. usan el archivo |

### Tipos de Secretos Detectados

**Auto-Updatable App Signatures** 🔄
- Data-Shield **automatically discovers** new app credential locations
- Daily updates from GitHub, OWASP, CVE databases, and local registry scans
- Community contributions via GitHub PRs
- See [`APP_SIGNATURES_UPDATE.md`](APP_SIGNATURES_UPDATE.md) for details
- **Command**: `datashield-admin update-signatures`

**Cloud & APIs**
- AWS: access keys, secret keys, session tokens
- GCP: service account JSON, API keys, OAuth tokens
- Azure: storage keys, tenant IDs, connection strings
- OpenAI, Anthropic, Stripe, Twilio, SendGrid, HuggingFace, etc.

**VCS & Collaboration**
- GitHub: PATs (classic + fine-grained), OAuth tokens, app tokens
- GitLab: personal access tokens
- Git: .git-credentials, .netrc, SSH keys, signed commits
- GitHub CLI: hosts.yml with OAuth

**Development Tools**
- VS Code: keytar vault, globalStorage tokens, extension secrets
- JetBrains: passwords.xml, master keys, HTTP client secrets
- Node/npm: .npmrc tokens, .yarnrc, package.json secrets
- Docker: config.json auths, docker-compose secrets
- Kubernetes: ~/.kube/config with cluster tokens

**SSH & TLS**
- SSH: id_rsa, id_ed25519, id_ecdsa, known_hosts
- PEM blocks: private keys, certificates
- PKCS#12, JKS keystores

**Databases**
- Connection strings: PostgreSQL, MySQL, MongoDB, Redis, MSSQL
- Passwords en .env, config files, dockers-compose.yml

**Browsers**
- Cookies SQLite desde Chrome, Edge, Firefox, Brave, Opera
- Saved passwords (encrypted)

**Windows**
- Credential Manager (generic, domain, certificate)
- Registry: tokens de apps Electron, VPN, chat apps
- LSA secrets (requiere SYSTEM)

---

## 🛡️ Sistema de Riesgo (Risk Scoring)

Cada hallazgo recibe un **score 0-100** basado en:

### Base Scores
- SSH Private Key: **95**
- PEM Private Key: **90**
- AWS Secret Key: **92**
- GCP Service Account: **85**
- OpenAI API Key: **82**
- Stripe Secret: **90**
- JWT Token: **75**
- Browser Cookie: **70**
- Generic Password: **65**

### Modificadores (+/-)
- `+10`: Inside .git repo
- `+8`: Plaintext (not encrypted)
- `+7`: Active process has file open
- `+5`: World-readable permissions
- `+3`: Modified in last 24h
- `-5`: In backup directory
- `-15`: Already encrypted (.ds-vault)

### Niveles Resultantes
| Nivel | Rango | Acción |
|-------|-------|--------|
| 🔴 **CRITICAL** | 85-100 | Revocación inmediata recomendada |
| 🟠 **HIGH** | 65-84 | Cifrar en Vault hoy |
| 🟡 **MEDIUM** | 40-64 | Revisar y asegurar |
| 🔵 **LOW** | 0-39 | Monitorear |

---

## 🔐 Vault System

El **Vault** es tu sistema de cifrado local para credenciales sensibles.

### Características
- ✅ **Cifrado**: AES-256-GCM con PBKDF2-HMAC-SHA256 (600k iteraciones)
- ✅ **Master Key**: Tu contraseña maestra (nunca almacenada en plaintext)
- ✅ **DPAPI Protection**: Opcional — el master key hash se cifra con DPAPI de Windows
- ✅ **One-Click Encrypt**: Cifra un archivo, luego lo descifras cuando lo necesites
- ✅ **Batch Operations**: Cifra 100 archivos de una sola vez
- ✅ **Auto-Schedule**: Integración con Windows Task Scheduler
  - Al apagar: cifra automáticamente todos los archivos del Vault
  - Al iniciar: descifra automáticamente (requiere master password una vez al login)
- ✅ **Integrity Check**: Verifica SHA-256 al descifrar

### Flujo Diario
```
Mañana:
1. Inicias sesión
2. Data-Shield descifra automáticamente tus archivos (Task Scheduler)
3. Ingresas master password una vez
4. Trabajas normalmente todo el día

Noche:
1. Al apagar la PC
2. Data-Shield cifra automáticamente todo el Vault
3. Tus credenciales duermen seguras toda la noche
```

---

## 📊 Funcionalidades Principales

### Escaneo
- ✅ Profundidad configurable (0 = ilimitado)
- ✅ **3 Modos de Operación**:
  - **PERFORMANCE**: Máximo CPU/RAM/GPU, ~2-3 min para 100k archivos
  - **SAFE**: Bajo impacto de recursos, ~8-10 min para 100k archivos (default)
  - **INTERACTIVE**: Pausa en cada hallazgo, espera decisión del usuario
- ✅ Modo turbo (solo archivos de riesgo) vs. Modo profundo (análisis byte a byte)
- ✅ Incluir/excluir directorios
- ✅ Pausa y resume (con checkpoint automático cada 500 archivos)
- ✅ Barra de progreso en vivo (CLI: Rich, GUI: QProgressBar)
- ✅ Leyenda activa: path del archivo siendo escaneado en tiempo real

### Resultados
- ✅ Tabla interactiva con Path, Archivo, Tipo, Dato (censurado), App responsable, Riesgo
- ✅ Filtros en tiempo real: búsqueda, riesgo, app, tipo de dato
- ✅ Detalle de hallazgo: preview (censurado/revelable), acciones, historial, sugerencias
- ✅ Ordenamiento por cualquier columna
- ✅ Selección múltiple para operaciones batch

### Exportación
- ✅ Formatos: **TXT** (plano), **JSON** (estructurado), **CSV** (Excel), **HTML** (interactivo)
- ✅ Pre-export editor: elimina filas, marca como ignoradas, limpia lista completa
- ✅ Estadísticas resumidas en cada export

### Vault
- ✅ Encrypt/decrypt individual o batch
- ✅ Auto-schedule en Task Scheduler
- ✅ Master key en DPAPI (opcional)
- ✅ Integrity verification

### Monitor
- ✅ Real-time filesystem watching (Watchdog + Windows API)
- ✅ Toast notifications cuando se detectan nuevas credenciales
- ✅ Whitelist de rutas que nunca alertan
- ✅ System tray icon con indicador de estado
- ✅ Log de eventos en tiempo real

### Historial & Analytics
- ✅ Cada escaneo se guarda con timestamp
- ✅ Diff entre dos escaneos (qué cambió)
- ✅ Estadísticas: hallazgos por nivel de riesgo, apps involucradas, tipos de datos
- ✅ Gráficos de evolución histórica

---

## 🎨 Interfaz de Usuario

### CLI (Rich + Colorama)
```
╔══════════════════════════════════════════════════════════════╗
║  DATA-SHIELD v1.0.0  ●  Modo: PROFUNDO  ●  Admin: ✓         ║
╠══════════════════════════════════════════════════════════════╣
║  Escaneando: C:\Users\Usuario\.ssh\id_rsa                    ║
║  ████████████░░░░░░░░  62%  14,382 / 23,100 archivos         ║
║  Hallazgos: 47  ●  Tiempo: 00:02:34  ●  ETA: 00:01:34       ║
╚══════════════════════════════════════════════════════════════╝
```

Tabla de resultados con colores ANSI:
```
┌─────────────────────────────┬──────────────────┬────────────┬────────────┬──────────┐
│ Ruta                        │ Archivo          │ Tipo       │ App        │ Riesgo   │
├─────────────────────────────┼──────────────────┼────────────┼────────────┼──────────┤
│ C:\Users\…\.ssh\            │ id_rsa           │ SSH Key    │ Git        │ CRITICAL │
│ C:\Users\…\.aws\            │ credentials      │ AWS Creds  │ AWS CLI    │ CRITICAL │
│ C:\Users\…\AppData\GitHub…  │ hosts.yml        │ OAuth      │ GitHub CLI │ HIGH     │
└─────────────────────────────┴──────────────────┴────────────┴────────────┴──────────┘
```

### GUI (PySide6 + Material Modern Neon)
- **Material Modern Neon Dark**: Tema oscuro azulado con acentos neón (cyan, magenta, lima, naranja)
- **Light Mode**: Variante clara para preferencias de usuario
- **Responsive**: Diseño adaptativo, funciona en 1920x1080+
- **Smooth animations**: Transiciones suaves, no jarring
- **Paneles**:
  - Izquierda: Controles (selección de directorio, opciones, botones)
  - Centro: Barra de progreso activa
  - Derecha: Tabla de resultados + filtros
  - Abajo: Barra de estado, contador de hallazgos, ícono de admin

---

## 📦 Construcción & Distribución

### Desarrollo Local
```bash
# Instalar modo editable
pip install -e ".[dev,test]"

# Tests
pytest tests/ -v --cov=src/datashield

# Lint + Format
ruff check src/ tests/
black src/ tests/
mypy src/

# Ejecutar CLI
datashield scan C:\Users

# Ejecutar GUI
datashield
```

### Build para Distribución
```bash
# Generar executable standalone
pip install PyInstaller
pyinstaller datashield.spec

# Resultado: dist\datashield.exe (~120-150 MB con compresión UPX)
# Incluye: Python runtime, todas las dependencias, reglas YARA, temas QSS
```

### Requisitos Build
```
PyInstaller 6.x
UPX (opcional, para compresión)
Visual Studio Build Tools (para dependencias compiladas como pywin32)
```

---

## 🗂️ .gitignore

Siempre excluye:
```
# Virtual environment
venv/
.venv/

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# Data-Shield specific
datashield_audit.log
datashield_audit.*.log
.ds-vault  # Archivos cifrados

# User database & sensitive data
src/datashield/storage/*.db
src/datashield/storage/*.db-shm
src/datashield/storage/*.db-wal

# OS
.DS_Store
Thumbs.db
*.exe

# IDE
.vscode/
.idea/
*.swp
*.swo

# Test artifacts
.coverage
htmlcov/

# Temporary
*.tmp
*.bak
```

---

## 📝 Roadmap & Features (v1.0.0+)

### v0.1 (MVP — Core Prototype)
- [x] Blueprint architecture
- [ ] Scanner Engine (async, pause/resume)
- [ ] Pattern Engine (6 layers)
- [ ] App Fingerprinting (40+ apps)
- [ ] Risk Scorer
- [ ] Vault (AES-256)
- [ ] CLI (Rich + Click)
- [ ] GUI (PySide6 Material Neon)
- [ ] Monitor Mode (Watchdog)
- [ ] Exporters (TXT, JSON, CSV, HTML)
- [ ] Windows integration (UAC, Credential Manager, Registry)
- [ ] Tests + PyInstaller build
- [ ] Documentation

### v1.1 (Polish & Extras)
- [ ] First-run wizard
- [ ] Scan profiles (save/load configurations)
- [ ] Audit logging with loguru
- [ ] Panic Mode hotkey (Ctrl+Shift+Alt+L)
- [ ] Statistics dashboard (graphs, history)
- [ ] Vault profile export
- [ ] Remediation suggestions per secret type
- [ ] Diff scanning (compare sessions)
- [ ] Quick Scan mode (30 seconds)

### v1.2 (Advanced)
- [ ] Multi-language support (i18n full)
- [ ] Cloud sync (optional, encrypted)
- [ ] Integration with password managers (Bitwarden, 1Password)
- [ ] Custom regex patterns editor in GUI
- [ ] Scheduled scans
- [ ] Report sharing (encrypted PDF)

### v2.0 (Platform Expansion)
- [ ] macOS support
- [ ] Linux support
- [ ] Web-based admin dashboard

---

## 🤝 Contributing

Consulta `CONTRIBUTING.md` para setup, coding standards, y PR process.

---

## ⚖️ Licencia

MIT License — eres libre de usar, modificar y distribuir.

---

## 📞 Soporte

**Issues**: [GitHub Issues](https://github.com/tu-usuario/data-shield/issues)  
**Discussions**: [GitHub Discussions](https://github.com/tu-usuario/data-shield/discussions)

---

## 🙏 Agradecimientos

- [OWASP](https://owasp.org/) por referencia en detección de secretos
- [TruffleHog](https://trufflesecurity.com/) por inspiración en patrones de detección
- Comunidad Python por Rich, PySide6, SQLAlchemy, YARA

---

**Data-Shield** · Precisión máxima en detección de credenciales · 100% local, zero telemetría

*Build date: 2026-04-28 · Status: 🟡 Prototype Phase*
