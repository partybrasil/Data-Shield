# App Signatures Update System — Automatic Pattern & Credential Location Discovery

**Purpose**: Mantener `patterns/app_signatures.py` actualizado automáticamente con nuevas apps, nuevas ubicaciones de credenciales, y nuevos secretos sin intervención manual.

**Philosophy**: Data-Shield es un *living document* de credenciales dispersas. Las apps evolucionan, cambian ubicaciones, agregan nuevas formas de almacenar secretos. Nuestra BD de firmas debe evolucionar con ellas.

---

## 🎯 Requisito

> El módulo `app_signatures.py` que almacena y tiene los conocimientos de apps y sus secretos donde se almacenan **sea actualizable con un script automatizado que consulta varias fuentes fiables y actualizadas** para mantener actualizado el conocimiento de secretos de más apps y softwares.

---

## 🏗️ Arquitectura del Sistema de Actualización

### Componentes

#### 1. **`patterns/app_signatures.py`** (Dataclass-based, no strings)

**Cambio de paradigma**: En lugar de diccionarios anidados (original), usar Pydantic dataclasses para poder validar, serializar y versionear.

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class AppSignature(BaseModel):
    """Single application signature with metadata."""
    
    # Identification
    id: str                          # Unique ID: "vscode", "aws_cli", etc
    display_name: str                # "Visual Studio Code"
    category: str                    # "ide", "vcs", "cloud", "browser", etc
    
    # Signature sources
    paths: List[str]                 # Path patterns (env vars allowed)
    process_names: List[str]         # .exe names to match active processes
    registry_keys: Optional[List[str]] = None  # Registry paths (new!)
    
    # Credential locations
    credential_locations: List[Dict[str, str]] = Field(default_factory=list)
    # [
    #   {
    #     "path": "%APPDATA%/Code/User/globalStorage",
    #     "file_patterns": ["*.state", "*.json"],
    #     "secret_type": "extension_tokens",
    #     "how_stored": "plaintext|encrypted|sqlite"
    #   }
    # ]
    
    # Metadata for tracking updates
    first_seen: datetime             # When this app was added
    last_updated: datetime           # Last time signature was verified
    last_updated_source: str         # "manual" | "github" | "reddit" | "osint_scan"
    
    # Version & credibility
    confidence: str                  # "high" | "medium" | "low"
    notes: Optional[str] = None      # Human-readable notes
    reference_urls: List[str] = Field(default_factory=list)  # Sources
    
    @validator('id')
    def id_lowercase(cls, v):
        return v.lower().replace(" ", "_")

class AppSignaturesDB(BaseModel):
    """Complete signatures database with versioning."""
    
    version: str                     # "1.0.0", "1.0.1", etc
    timestamp: datetime              # When this DB was generated
    data_source: str                 # "hybrid" (merged from multiple sources)
    apps: List[AppSignature]
    
    total_apps: int
    last_update_check: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

#### 2. **`patterns/updater/`** (New module)

```
patterns/updater/
├── __init__.py
├── orchestrator.py          # Main update coordinator
├── sources/
│   ├── __init__.py
│   ├── github_source.py     # GitHub repos (TruffleHog, Shhgit, etc)
│   ├── reddit_source.py     # Reddit r/learnprogramming, r/devops threads
│   ├── osint_source.py      # OSINT (public databases, CVEs)
│   ├── windows_registry.py  # Live registry scan
│   └── local_installed.py   # Detect installed apps locally
├── extractors/
│   ├── __init__.py
│   ├── github_extractor.py  # Parse GitHub issue/wiki content
│   ├── path_extractor.py    # Extract env paths from code
│   └── credential_extractor.py
├── validators/
│   ├── __init__.py
│   ├── path_validator.py    # Verify paths exist (requires admin)
│   ├── schema_validator.py  # Validate Pydantic model
│   └── dedup_validator.py   # Remove duplicates
├── storage/
│   ├── __init__.py
│   ├── backup.py            # Backup current signatures
│   └── version_control.py   # Git commit + diff tracking
└── cli.py                    # CLI tool for manual/automated updates
```

---

## 📡 Fuentes Fiables de Actualización

### Tier 1: Official & Verified (HIGH CONFIDENCE)

| Fuente | Método | Frecuencia | Confianza |
|--------|--------|-----------|-----------|
| **GitHub: zaproxy/community-scripts** | Scrape curated list | Mensual | 🟢 HIGH |
| **GitHub: gremlin/leaky-repo** | Regex patterns de credenciales reales | Diario | 🟢 HIGH |
| **GitHub: TruffleHog/truffleHog** | Sus reglas YARA + regex | Diario | 🟢 HIGH |
| **Microsoft Docs: App Store paths** | Crawl official docs | Trimestral | 🟢 HIGH |
| **OWASP: Secrets in Code** | Community submissions | Mensual | 🟢 HIGH |

### Tier 2: Community & OSINT (MEDIUM CONFIDENCE)

| Fuente | Método | Frecuencia | Confianza |
|--------|--------|-----------|-----------|
| **Reddit: r/devops, r/learnprogramming** | Parse .env examples en posts | Semanal | 🟡 MEDIUM |
| **Stack Overflow: common config locations** | Parse accepted answers | Semanal | 🟡 MEDIUM |
| **CVE Database: credential storage flaws** | Parse CVE descriptions | Trimestral | 🟡 MEDIUM |
| **GitHub Issues: "where does X store creds?"** | Full-text search | Semanal | 🟡 MEDIUM |

### Tier 3: Local Discovery (DYNAMIC)

| Método | Trigger | Confianza |
|--------|---------|-----------|
| **Local registry scan** | `datashield-admin scan-registry` | 🟢 HIGH (verified) |
| **Installed apps analysis** | Detect `HKCU/Software` patterns | 🟡 MEDIUM (heuristic) |
| **User feedback loop** | Users report new locations found | 🔵 CONTEXT (user-verified) |

---

## 🔄 Flujo de Actualización Automatizado

### Paso 1: Fetch Data (Parallel)

```python
# patterns/updater/orchestrator.py

async def fetch_all_sources():
    """Fetch from all sources in parallel."""
    
    sources = [
        GitHubSource(repo="zaproxy/community-scripts"),
        GitHubSource(repo="trufflesecurity/truffleHog"),
        GitHubSource(query="where does X store secrets"),
        MicrosoftDocsSource(product="vs-code"),
        MicrosoftDocsSource(product="azure-cli"),
        CVEDatabaseSource(),
        WindowsRegistrySource(),  # Requires admin
    ]
    
    results = await asyncio.gather(*[s.fetch() for s in sources])
    # Combina datos de múltiples fuentes
    return merge_results(results)
```

### Paso 2: Extract Patterns

```python
# patterns/updater/extractors/github_extractor.py

def extract_app_signatures_from_github(raw_data: str) -> List[Dict]:
    """
    Parse GitHub issue/wiki content like:
    
    "VS Code stores tokens in %APPDATA%\Code\User\globalStorage\*.json"
    "AWS CLI credentials at %USERPROFILE%\.aws\credentials"
    
    Returns structured AppSignature-ready dicts.
    """
    
    # NLP + regex extraction
    patterns = extract_path_patterns(raw_data)  # %APPDATA%, %USERPROFILE%
    app_mentions = extract_app_names(raw_data)   # VS Code, AWS CLI
    secret_types = extract_secret_types(raw_data)  # "token", "credentials", "key"
    
    return combine_into_signatures(patterns, app_mentions, secret_types)
```

### Paso 3: Validate & Deduplicate

```python
# patterns/updater/validators/

async def validate_signatures(candidates: List[Dict]) -> List[AppSignature]:
    """
    1. Deduplicate by (app_id, path)
    2. Verify paths exist (if admin)
    3. Validate Pydantic model
    4. Assign confidence scores
    5. Check against existing DB (diff)
    """
    
    # Dedup
    candidates = deduplicate_by_key(candidates, key=lambda x: (x['id'], x['path']))
    
    # Validate paths (requires admin on Windows)
    for candidate in candidates:
        for path in candidate['paths']:
            expanded = expand_env_vars(path)
            if path_exists(expanded):
                candidate['confidence'] = 'high'
            else:
                candidate['confidence'] = 'medium'
    
    # Validate schema
    validated = [AppSignature(**c) for c in candidates]
    
    return validated
```

### Paso 4: Merge & Version

```python
# patterns/updater/storage/version_control.py

def merge_signatures(
    existing_db: AppSignaturesDB,
    new_candidates: List[AppSignature],
    strategy: str = "union"  # "union" | "replace" | "conservative"
) -> AppSignaturesDB:
    """
    Merge new discoveries with existing DB.
    
    Strategy "conservative": Keep high-confidence existing, add high-confidence new
    Strategy "union": Merge all, keep best confidence per app/path
    Strategy "replace": Replace entire DB (risky!)
    """
    
    merged = existing_db.copy()
    
    for new_sig in new_candidates:
        existing = next((s for s in merged.apps if s.id == new_sig.id), None)
        
        if not existing:
            # New app
            merged.apps.append(new_sig)
        else:
            # Merge with existing
            merged_sig = merge_app_signatures(existing, new_sig, strategy)
            merged.apps = [s for s in merged.apps if s.id != new_sig.id] + [merged_sig]
    
    # Increment version
    merged.version = increment_semantic_version(merged.version)
    merged.timestamp = datetime.now()
    
    return merged
```

### Paso 5: Test & Commit

```python
# patterns/updater/cli.py

async def update_signatures(
    run_local_scan: bool = False,
    test_before_commit: bool = True,
    auto_commit: bool = False
):
    """
    1. Fetch from all sources
    2. Extract & validate
    3. Merge with existing
    4. Test: Run pattern_engine against fixture files with new sigs
    5. Create git commit with diff
    6. (Optional) Push to repo
    """
    
    # 1-3
    new_db = await fetch_extract_validate()
    
    # 4: Test with fixtures
    if test_before_commit:
        test_results = run_pattern_tests(new_db)
        if test_results.failed > 0:
            print(f"❌ {test_results.failed} tests failed. Aborting.")
            return False
    
    # 5: Commit
    diff_summary = generate_diff(existing_db, new_db)
    
    commit_message = f"""
    feat(app-signatures): Update app signatures database
    
    Sources:
    - GitHub: 42 new apps/patterns extracted
    - Windows Registry: 15 local apps detected
    - OWASP: 8 new CVE-based patterns
    
    Summary:
    - Total apps: {len(new_db.apps)}
    - New apps: {diff_summary['new_apps']}
    - Updated apps: {diff_summary['updated_apps']}
    - Confidence distribution: {diff_summary['confidence_dist']}
    
    Test results: {test_results.passed}/{test_results.total} passed
    """
    
    git.add("patterns/app_signatures.py")
    git.commit(commit_message)
    
    if auto_commit:
        git.push()
    
    return True
```

---

## 📅 Programación de Actualizaciones

### Automated Schedule (GitHub Actions)

```yaml
# .github/workflows/update-app-signatures.yml

name: Update App Signatures

on:
  schedule:
    # Diario a las 3 AM UTC (no interfiere con dev hours)
    - cron: '0 3 * * *'
  
  # Manual trigger
  workflow_dispatch:
    inputs:
      run_local_scan:
        description: 'Also scan local Windows registry (requires admin)'
        required: false
        default: false

jobs:
  update-signatures:
    runs-on: windows-latest  # Necesita Windows para registry scan
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install deps
        run: pip install -e ".[dev]"
      
      - name: Run update
        run: |
          python -m datashield.patterns.updater.cli \
            --fetch-github \
            --fetch-cvd \
            --test-before-commit \
            --dry-run  # First run as dry-run
      
      - name: Create Pull Request
        if: success()
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: Auto-update app signatures'
          title: '[AUTO] Update App Signatures'
          body: 'Automated update from GitHub/OWASP/CVE sources'
          branch: auto/update-app-signatures
```

### Manual Update (Command)

```bash
# Update from GitHub sources
datashield-admin update-signatures --source github

# Update from registry (requires admin)
datashield-admin update-signatures --source local-registry

# Interactive review before commit
datashield-admin update-signatures --interactive

# Test without committing
datashield-admin update-signatures --dry-run
```

---

## 🎯 Integration con Data-Shield Core

### En `core/scanner.py`

```python
class Scanner:
    
    async def __init__(self):
        # Load app signatures — siempre la versión más reciente
        self.app_sigs = AppSignaturesDB.load_latest()
        
        # Si hay una actualización disponible, notificar
        if self.app_sigs.needs_update():
            logger.warning(
                f"App signatures outdated (v{self.app_sigs.version}). "
                f"Latest is v{self.app_sigs.latest_available}. "
                f"Run: datashield-admin update-signatures"
            )
```

### En `core/app_fingerprint.py`

```python
class AppFingerprinter:
    
    def __init__(self, app_sigs: AppSignaturesDB):
        self.app_sigs = app_sigs
        self.signature_version = app_sigs.version
        
        # En cada Finding, incluir la versión del DB
        # Así sabemos con qué DB fue identificada cada credencial
    
    def identify_app(self, file_path: str) -> Optional[AppSignature]:
        """Use latest signature DB."""
        # This automatically uses self.app_sigs
        ...
```

### En `storage/models.py`

```python
class Finding(Base):
    # ... existing fields ...
    
    # NEW: Metadata sobre qué DB de firmas identificó esta credencial
    app_signature_version: str  # "1.0.5"
    identified_by_source: str   # "github_path_match" | "registry_scan" | "local_scan"
    confidence_score: float     # 0.0-1.0
```

---

## 📊 Monitoreo de Calidad

### Metrics Dashboard (para el equipo)

```
datashield-admin signatures-report

╔════════════════════════════════════════╗
║ App Signatures Database Report         ║
╠════════════════════════════════════════╣
║                                        ║
║ Version:              1.2.3            ║
║ Total Apps:           47               ║
║                                        ║
║ Confidence Distribution:               ║
║   🟢 HIGH:            35 apps (74%)   ║
║   🟡 MEDIUM:          10 apps (21%)   ║
║   🔵 LOW:             2 apps  (4%)    ║
║                                        ║
║ Last Updated:         2026-04-28 03:00 ║
║ Sources Last Fetched: GitHub, OWASP    ║
║                                        ║
║ Recent Additions (v1.2.3):             ║
║   + Cursor (AI IDE)                    ║
║   + Anthropic CLI                      ║
║   + LM Studio                          ║
║   + Ollama                             ║
║                                        ║
║ Test Coverage:        98% pass rate    ║
║                                        ║
╚════════════════════════════════════════╝
```

---

## 🔐 Consideraciones de Seguridad

1. **No expongas datos reales**: Los extractores never extraen credenciales reales, solo patrones
2. **Valida antes de usar**: Cada signature pasa por Pydantic validation
3. **Versionea todo**: Git tracks all changes, revertible si hay errores
4. **Test fixtures**: Usa fake credentials en tests, nunca reales
5. **Rate limiting**: No bombardear GitHub/OWASP APIs (respectful scraping)

---

## 📋 Roadmap de Implementación

### v1.0.0 (MVP)
- ✅ Manual `datashield-admin update-signatures` from GitHub
- ✅ Pydantic-based AppSignature model
- ✅ Basic extractor para GitHub issues
- ✅ Validation + dedup

### v1.1
- ✅ Automated GitHub Actions (diario)
- ✅ CVE database integration
- ✅ Local registry scanning
- ✅ Pull request automation

### v1.2
- ✅ Machine learning para detectar nuevas apps automáticamente
- ✅ User feedback loop (cuando user encuentra credencial no en DB)
- ✅ Community contributions via GitHub PRs

### v2.0
- ✅ Webhook para alertas de nuevas apps críticas
- ✅ API pública para queries (que apps usan secreto X)

---

## 📄 Ejemplo: Flujo Completo

**Escenario**: GitHub issue en r/learnprogramming pregunta "¿Dónde almacena credenciales X?"

```
1. GitHub Actions scheduler dispara diario
2. Fetch Reddit + GitHub + CVE
3. Extract: "App X stores at %LOCALAPPDATA%\Y\config.json"
4. Parse: AppSignature(id="x", paths=["%LOCALAPPDATA%\Y\config.json"])
5. Validate: Path exists en test fixture ✓
6. Deduplicate: No existe, es nuevo ✓
7. Merge: Agregar a DB
8. Test: Run pattern engine con new sig ✓
9. Commit: "Auto: Add App X signature"
10. PR: Create + auto-merge (si todo green)
11. Build: PyInstaller picks up new DB
12. Release: New datashield.exe con App X support

Total time: < 30 minutos
Human intervention: 0

Resultado: Data-Shield siempre está al día con nuevas apps.
```

---

## 🎯 Conclusión

**Sin este sistema**, app_signatures.py se vuelve obsoleto en 3 meses.

**Con este sistema**, Data-Shield evoluciona automáticamente, manteniéndose al día con:
- Nuevas apps emergentes
- Nuevas ubicaciones de credenciales
- Nuevas formas de almacenar secretos
- Cambios en versiones existentes

Es un **living document** que crece con el ecosistema de Windows/dev tools. 🚀
