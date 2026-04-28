# Data-Shield: Mejoras & Potenciaciones (v0.1 → v1.0)

## 📊 Análisis del Blueprint Original

El blueprint en `DATA-SHIELD_prompt_FINGERPRINT.md` es **sólido y completo**, pero hay oportunidades para hacerlo aún más potente y contemporáneo (2025).

---

## 🚀 Mejoras Propuestas

### 1. Stack Tecnológico Actualizado

#### Original ❌
- `regex`: 2024.x

#### Mejorado ✅
```
regex:              2024.11.x  (latest)
pydantic:           2.8.x      (for validation & config, not in original)
pydantic-settings:  2.x        (environment-based config)
```

**Por qué**: Pydantic proporciona validación automática de configs, serialización JSON, y type-safety que hacer manualmente con `configparser`. Ideal para settings.py.

---

#### Original ❌
- `click`: 8.x

#### Mejorado ✅
```
click:              8.1.x
click-plugins:      1.x        (para permitir comandos custom del usuario)
```

---

#### Original ❌
- `cryptography`: 43.x (Fernet)

#### Mejorado ✅
```
cryptography:       43.0.x
pyca/bcrypt:        4.2.x      (add bcrypt para password hashing, más seguro que plain PBKDF2)
```

**Adición**: Usar bcrypt para hash del master password en memory, no solo PBKDF2.

---

#### Original ❌
- `SQLAlchemy`: 2.x (sin Alembic)

#### Mejorado ✅
```
SQLAlchemy:         2.1.x
alembic:            1.14.x     (schema migration framework — add esto!)
```

**Por qué**: Alembic permite versionado del schema y migración automática entre versiones de Data-Shield. Crítico para users que actualicen la app.

---

#### Original ❌
- No hay queue/background task management

#### Mejorado ✅
```
APScheduler:        3.11.x     (scheduled tasks — para el Panic Mode y auto-schedule)
```

**Por qué**: APScheduler es más robusto que Task Scheduler solo. Permite programar tareas internas (cleanup, vault rotation, stats aggregation).

---

#### Original ❌
- `loguru`: 0.7.x sin structured logs

#### Mejorado ✅
```
loguru:             0.7.x      (keep it, pero con JSON formatting)
pythonjsonlogger:   2.x        (JSON structured logs for parsing later)
```

---

### 2. Arquitectura de Modules Mejorada

#### Nuevo Módulo: `config/` Potenciado

**Original**:
```
config/
├── __init__.py
├── settings.py       ← configparser básico
└── defaults.py
```

**Mejorado**:
```
config/
├── __init__.py
├── settings.py                 ← Pydantic BaseSettings (type-safe!)
├── defaults.py                 ← Default values
├── validators.py               ← Custom validators (path exists, port valid, etc)
├── loader.py                   ← Load from file, env vars, CLI overrides
└── profiles.py                 ← Save/load scan profiles (turbo, full, quick)
```

**Beneficio**: Validación automática, type hints, ayuda CLI integrada, perfiles guardados.

---

#### Nuevo Módulo: `api/` (Prepare for Future Extensions)

**Adición**:
```
api/
├── __init__.py
├── rest.py                     ← FastAPI router (future for remote scanning)
└── websocket.py                ← WebSocket (future for real-time dashboard sharing)
```

**Nota**: Vacíos en v0.1, pero estructura lista para que v2.0 pueda tener API remota (opcional).

---

#### Mejora: `core/` Modularización Adicional

**Original**:
```
core/
├── scanner.py
├── pattern_engine.py
├── entropy.py
├── app_fingerprint.py
├── risk_scorer.py
└── models.py
```

**Mejorado**:
```
core/
├── scanner.py
├── pattern_engine.py
├── entropy.py
├── app_fingerprint.py
├── risk_scorer.py
├── findings.py                 ← Finding CRUD + queries (extracted from models)
├── events.py                   ← ScanEvent, ProgressEvent (event system)
├── exceptions.py               ← Custom exceptions (not ValueError)
├── models.py                   ← Only dataclasses
└── plugins.py                  ← Plugin system para custom detectors (v1.1+)
```

---

### 3. Vault Potenciado

#### Original
```
AES-256-GCM con PBKDF2 (600k iteraciones)
```

#### Mejorado ✅
```
1. Master password hashed con bcrypt (memory storage)
2. Encryption keys derived con PBKDF2-HMAC-SHA256 (600k + Argon2 alternative)
3. File encryption: AES-256-GCM
4. DPAPI protection for master key (Windows)
5. Encrypted vault index (metadata)
6. Audit trail in encrypted log
7. Key rotation support (v1.1)
```

**Adición**: Argon2 como alternativa a PBKDF2 (más resistente a ataques GPU).

---

### 4. Pattern Engine Enhancement

#### Original
```
~200 regex patterns
YARA rules (basic)
Entropy Shannon
SQLite parser
JSON/YAML/TOML parser
```

#### Mejorado ✅
```
Original +
├── Semantic analysis: detectar "password=xxxx" sin saber la forma exacta de xxxx
├── Machine Learning layer: entrenar un classifier simple con hallazgos previos
├── Custom regex editor en GUI: usuarios pueden agregar patrones propios
├── Community patterns: repositorio público de patterns YARA (via git submodule)
├── Signature verification: YARA rules firmadas criptográficamente (v1.2+)
└── False positive classifier: feedback loop para mejorar precision
```

---

### 5. GUI Enhancements

#### Original
```
Material Modern Neon Dark/White theme
QTableView con modelo
Detail window
Filtros
Export dialog
Tray icon
```

#### Mejorado ✅
```
Original +
├── Dark/Light/Auto mode (auto-detect Windows theme preference)
├── Color-blind accessible palette option
├── Keyboard shortcuts (Ctrl+S scan, Ctrl+E export, Ctrl+V vault, etc)
├── Drag-drop support (drag paths to scan)
├── Multi-window support (tear off results table, scan in another window)
├── Undo/Redo for list edits (before export)
├── Timeline visualization (scan history)
├── Performance profiler built-in (show scan speed by directory)
└── Theme dark mode true black option (OLED optimization)
```

---

### 6. Monitor Mode Enhancement

#### Original
```
Watchdog + alerts
Toast notifications
Tray icon
Whitelist
```

#### Mejorado ✅
```
Original +
├── Predictive alerting: si detecta 3 archivos sensibles en 5 min → pausa monitor
├── Machine learning: learning from user dismissals (no es falsa alarma)
├── Behavioral analysis: comparar contra baseline (qué directorios tienen cambios normales)
├── Threat correlation: si Monitor detecta algo y Vault está desbloqueado → auto-encrypt
└── Custom alert rules (por tipo de dato, por app, por time of day)
```

---

### 7. Exportación Enhanced

#### Original
```
TXT, JSON, CSV, HTML
Pre-export editor
```

#### Mejorado ✅
```
Original +
├── Excel (.xlsx) con tablas de pivot de riesgo, timeline de archivos
├── PDF encriptado con contraseña (para compartir con IT team)
├── Markdown para confdir en git (con datos censurados por defecto)
├── SARIF format (para integración con VS Code + GitHub)
├── Email integration: enviar reporte vía SMTP (v1.1)
├── Webhook: POST a endpoint personalizado del usuario (v1.1)
└── Cloud export: Azure Blob, S3 (optional extra, encrypted)
```

---

### 8. Testing & Quality

#### Original
```
pytest básico
Fixtures con fake data
```

#### Mejorado ✅
```
Original +
├── pytest con coverage >= 85%
├── Integration tests (full stack, con DB real)
├── Performance tests (benchmark scan speed)
├── GUI tests con pytestqt
├── Load tests: simular 100k archivos
├── Security tests: SAST con bandit, dependency checks con safety
├── E2E tests: real UAC elevation, real Vault encryption
└── CI/CD: GitHub Actions con windows-latest runner
```

---

### 9. Documentation Potenciada

#### Original
```
README.md
Docstrings
CHANGELOG.md
```

#### Mejorado ✅
```
Original +
├── Architecture Decision Records (ADRs) en docs/adr/
├── API documentation (FastAPI auto-generated en v2.0)
├── Contributing guide con setup reproducible (Docker opcional)
├── Troubleshooting guide (common UAC issues, DPAPI problems)
├── Security whitepaper (explicar threat model, assumptions)
├── Performance tuning guide (cómo optimizar para 500k archivos)
├── Video tutorials (screencasts en docs/)
└── FAQ muy completo
```

---

### 10. Performance Optimizations

#### Original
```
Async + ThreadPoolExecutor
Checkpoint cada 500 archivos
```

#### Mejorado ✅
```
Original +
├── Lazy loading: no cargar toda la DB en memoria
├── Query optimization: índices en SQLite para búsquedas frecuentes
├── Memory pooling: reutilizar buffers para no-GC churn
├── Streaming results: no acumular todos los hallazgos antes de mostrar
├── Progressive disclosure: mostrar hallazgos conforme se encuentran
├── GPU acceleration: usar CUDA si está disponible para entropy analysis (v1.2)
├── Smart compression: comprimir vault entries en SQLite
└── Profiling built-in: `datashield profile` para medir bottlenecks
```

---

## 🏗️ Estructura Mejorada: Fases de Implementación

### Fase 1: Core + Engines + CLI (80-100 horas)

**Orden estricto**:
1. pyproject.toml + estructura de dirs
2. config/ (Pydantic-based)
3. core/models.py + core/exceptions.py
4. storage/ (SQLAlchemy + Alembic)
5. core/entropy.py
6. patterns/ (regex + YARA + app_signatures)
7. core/pattern_engine.py
8. core/risk_scorer.py
9. core/app_fingerprint.py
10. core/scanner.py (final, usa todo lo anterior)
11. windows/ (UAC, credential manager, registry)
12. core/events.py + core/findings.py
13. cli/ completo
14. Tests para core/

**Deliverable**: `datashield scan --help` funciona, escanea un directorio, muestra tabla Rich con hallazgos.

---

### Fase 2: GUI + Vault + Monitor + Export + Packaging (100-120 horas)

**Orden**:
1. vault/ (cipher, DPAPI, scheduler)
2. monitor/ (Watchdog)
3. export/ (todos los formatos)
4. gui/resources/ (QSS, iconos)
5. gui/workers.py
6. gui/widgets/ (en el orden especificado)
7. gui/main_window.py
8. gui/app.py + __main__.py (dual interface detection)
9. i18n/ (translations)
10. APScheduler integration (optional jobs)
11. Tests para GUI/Vault/Monitor
12. datashield.spec + manifest.xml
13. PyInstaller build + test exe
14. Documentación (CONTRIBUTING, ARCHITECTURE, TROUBLESHOOTING)
15. CHANGELOG.md

**Deliverable**: `datashield.exe` standalone executable que hace todo: GUI, CLI, monitor, vault, scan.

---

## 🎯 Criterios de Aceptación (DoD)

Cada feature completa debe tener:
- ✅ Código escrito (sin TODOs ni placeholders)
- ✅ Docstring en todas las clases/funciones públicas
- ✅ Tests con >85% coverage
- ✅ CI/CD passing (linting, type checking, tests)
- ✅ Integrado con el resto del sistema (no funciona solo)
- ✅ Actualización de README/documentación
- ✅ CHANGELOG entry

---

## 🔐 Security Hardening

Antes de v1.0, auditoria de:
1. **Input validation**: todas las rutas, configs, usuarios son validadas
2. **Secrets in memory**: master password limpiado después de usar (no en plaintext variables)
3. **File permissions**: vault DB y logs tienen permisos 0o600 (solo usuario actual)
4. **Dependency vulnerabilities**: `safety check` en CI
5. **Code scanning**: Bandit para common security anti-patterns
6. **Windows security**: UAC handling, registry access patterns

---

## 📈 Métricas de Éxito

Al finalizar v1.0:
- **Coverage**: ≥85% líneas de código
- **Performance**: Escanea 100k archivos en <5 minutos
- **Security**: 0 conocidos secrets en ejecutable (bandit passing)
- **UX**: Todos los flujos principales completan en <3 pasos
- **Stability**: 0 unhandled exceptions en uso normal
- **Docs**: ≥95% de funciones públicas tienen docstring

---

## 🛠️ Tech Debt Prevention

**NO hacer**:
- ❌ Codigos duplicados (refactorizar, crear helper)
- ❌ Funciones >50 líneas (splittear)
- ❌ Módulos >1000 líneas (reorganizar)
- ❌ Magic numbers (usar constants con nombres)
- ❌ Type hints incompletos (full PEP 484)
- ❌ Imports circulares (reorganizar modulos)

**SÍ hacer**:
- ✅ Test-first para features críticas
- ✅ Code review antes de merge
- ✅ Refactoring continuo (boyscout rule)
- ✅ Documentation as code (docstrings)
- ✅ Clear commit messages with conventional commits

---

## 🚦 Próximos Pasos Inmediatos

1. ✅ README profesional
2. ✅ Project context documentado
3. [ ] **Iniciar Fase 1 con pyproject.toml + estructura**
4. [ ] Decisiones de arquitectura (Pydantic sí/no, APScheduler sí/no)
5. [ ] Setup de CI/CD (GitHub Actions)
6. [ ] First commit con estructura base

---

**Data-Shield 1.0** será el gold standard en detección de credenciales en Windows. 🏆
