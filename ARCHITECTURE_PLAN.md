# Data-Shield: Architectural Implementation Plan

**Status**: 🟡 Planning Phase  
**Version**: v0.1 Prototype  
**Last Updated**: 2026-04-28  
**Target**: 📅 v1.0.0 Release (Q3 2025)

---

## 📐 Overview

This document coordinates the complete architectural blueprint for Data-Shield with refined technologies, potent design decisions, and a two-phase implementation strategy that respects the 200k token context limit.

**Three key files define the project**:
1. `README.md` — User-facing features & installation
2. `IMPROVEMENTS.md` — Enhanced tech stack & architectural refinements
3. `DATA-SHIELD_prompt_FINGERPRINT.md` — Complete technical blueprint
4. `data_shield_blueprint.html` — Visual architecture diagram

**This file** orchestrates the implementation phases and coordinates all modules.

---

## 🎯 Core Mission (Refined)

**Problem**: Miguel Diaz uses 20+ development tools (VS Code, Git, GitHub CLI, Docker, AWS CLI, npm, Kubernetes, etc.) with credentials dispersed across his system. He manually encrypts them at EOD and decrypts at start-of-day. Some locations he hasn't found yet.

**Solution**: Data-Shield → one-click discovery + categorization + encryption vault + real-time monitoring.

**Success Metric**: Scan 500k files in <5 min, identify 100% of known credential patterns, provide 0 false positives via fingerprinting, encrypt with AES-256-GCM, integrate with Windows Task Scheduler for automation.

---

## 🏗️ Architectural Layers

```
┌────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                            │
│  ┌─────────────────────┐            ┌──────────────────────┐  │
│  │    CLI (Rich)       │            │   GUI (PySide6)      │  │
│  │ (display.py, cmd/)  │            │  (main_window, etc)  │  │
│  └──────────┬──────────┘            └──────────┬───────────┘  │
│             └────────────────┬───────────────────┘             │
├────────────────────────────────────────────────────────────────┤
│  APPLICATION LAYER                                             │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  workers.py (QThread)  ·  events.py (AsyncIO events)  │   │
│  │  Coordinate async ops without blocking UI              │   │
│  └────────┬─────────────────────────────────────┬─────────┘   │
├────────────────────────────────────────────────────────────────┤
│  BUSINESS LOGIC LAYER                                          │
│  ┌────────────┐ ┌─────────────┐ ┌──────────┐ ┌────────────┐  │
│  │  scanner   │ │   pattern   │ │  vault   │ │  monitor   │  │
│  │  .py       │ │  _engine.py │ │ .py      │ │ .py        │  │
│  └─────┬──────┘ └──────┬──────┘ └────┬─────┘ └─────┬──────┘  │
│        ├─────────────────────────────────────────────┤        │
│  ┌─────────────────────────┬─────────────────────────┐        │
│  │ app_fingerprint.py      │ risk_scorer.py          │        │
│  │ entropy.py              │                         │        │
│  └─────────────────────────┴─────────────────────────┘        │
├────────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                    │
│  ┌──────────────────┐    ┌──────────────────┐               │
│  │   storage/       │    │   patterns/      │               │
│  │  (database,      │    │  (regex, YARA,   │               │
│  │   repository)    │    │   app_sigs)      │               │
│  └────────┬─────────┘    └────────┬─────────┘               │
├────────────────────────────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │   windows/   │ │   config/    │ │   export/            │  │
│  │  (UAC, cred) │ │  (settings)  │ │  (formats)           │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Two-Phase Implementation Strategy

### Phase 1: Core + Engines + CLI (Sections 1-13 of Blueprint)

**Timeline**: 80-100 hours  
**Goal**: Standalone scanner with powerful CLI  
**Deliverable**: `datashield scan` fully functional with all 6 detection layers

#### Phase 1 Module Order (Strict Dependency Order)

```
1. pyproject.toml + Directory Structure
   └─ Defines all metadata, entry points, dependencies

2. core/models.py
   └─ All dataclasses (Finding, ScanSession, etc)
   └─ No dependencies on other modules

3. core/exceptions.py
   └─ Custom exception classes
   └─ Zero dependencies

4. config/ (pydantic-based)
   ├─ settings.py
   ├─ defaults.py
   ├─ validators.py
   ├─ loader.py
   └─ profiles.py

5. storage/ (Database layer)
   ├─ database.py (SQLAlchemy models + session factory)
   ├─ repository.py (CRUD operations)
   └─ migrations.py (Alembic integration)

6. core/entropy.py
   └─ Shannon entropy analysis
   └─ Independent module

7. patterns/ (Detection patterns)
   ├─ regex_patterns.py (~200 compiled patterns)
   ├─ yara_rules/ (.yar files)
   └─ app_signatures.py (40+ app definitions)

8. core/pattern_engine.py
   └─ 6-layer detection coordination
   └─ Depends on: entropy, regex_patterns, yara, app_signatures

9. core/risk_scorer.py
   └─ Score calculation
   └─ Depends on: models

10. core/app_fingerprint.py
    └─ App identification
    └─ Depends on: app_signatures, psutil

11. core/events.py
    └─ Event definitions
    └─ Depends on: models

12. core/findings.py
    └─ Finding CRUD + queries
    └─ Depends on: repository, models

13. core/scanner.py (FINAL CORE MODULE)
    └─ Main scanning engine
    └─ Depends on: ALL of above + asyncio

14. windows/ (Windows integration)
    ├─ elevation.py (UAC)
    ├─ credential_manager.py
    ├─ registry_scanner.py
    └─ notifications.py

15. cli/ (Command-line interface)
    ├─ app.py (Click root + routing)
    ├─ display.py (Rich formatting)
    └─ commands/ (scan, vault, monitor, export, history)

16. tests/ (Unit + integration tests)
    ├─ test_scanner.py
    ├─ test_pattern_engine.py
    ├─ test_vault.py (basic)
    └─ fixtures/

**Phase 1 Exit Criteria**:
- ✅ `datashield scan C:\Users --mode deep` works
- ✅ Shows Rich table with all findings
- ✅ Supports pause/resume
- ✅ Exports to JSON/CSV/TXT
- ✅ History tracking in SQLite
- ✅ All tests pass (>85% coverage)
- ✅ README + IMPROVEMENTS documented

---

### Phase 2: GUI + Vault + Monitor + Export + Packaging (Sections 14-23 of Blueprint)

**Timeline**: 100-120 hours  
**Goal**: Complete production application  
**Deliverable**: `datashield.exe` standalone that does everything

#### Phase 2 Module Order (GUI-Last Strategy)

```
1. vault/ (Encryption)
   ├─ vault.py (AES-256-GCM + PBKDF2 + bcrypt)
   ├─ dpapi.py (DPAPI master key)
   └─ scheduler.py (Task Scheduler integration)

2. monitor/ (Real-time watching)
   └─ watcher.py (Watchdog + pattern engine)

3. export/ (Output formats)
   ├─ txt_exporter.py
   ├─ json_exporter.py
   ├─ csv_exporter.py
   └─ html_exporter.py

4. gui/resources/ (Visual assets)
   ├─ icons/ (app icons, status icons)
   └─ styles/
       ├─ dark_neon.qss
       └─ light.qss

5. gui/theme.py
   └─ QSS loader + dark/light toggle

6. gui/workers.py
   └─ QThread workers for scan, vault, monitor

7. gui/widgets/ (In order, each can be tested independently)
   ├─ progress_widget.py (QProgressBar + label)
   ├─ results_table.py (QTableView + custom model)
   ├─ filter_bar.py (QLineEdit + QComboBox filters)
   ├─ scan_panel.py (Directory picker, options)
   ├─ detail_window.py (Finding detail modal)
   ├─ vault_panel.py (Encrypt/decrypt UI)
   ├─ monitor_panel.py (Monitoring controls)
   ├─ risk_chart.py (QPieChart / QBarChart)
   ├─ export_dialog.py (Pre-export editor)
   └─ tray_icon.py (System tray)

8. gui/main_window.py
   └─ QMainWindow + QSplitter
   └─ Integrates all widgets

9. gui/app.py
   └─ QApplication setup
   └─ Instance check (single app)

10. i18n/ (Internationalization)
    ├─ es.json (Spanish — default)
    └─ en.json (English)

11. __main__.py (Entry point)
    └─ Detects CLI vs GUI mode
    └─ UAC elevation

12. Tests for Phase 2
    ├─ test_gui_widgets.py (pytestqt)
    ├─ test_vault.py (complete)
    ├─ test_monitor.py
    ├─ test_export.py
    └─ integration_tests/

13. Documentation
    ├─ CONTRIBUTING.md (setup, coding standards)
    ├─ ARCHITECTURE.md (deep dive)
    ├─ CLI_GUIDE.md (command reference)
    ├─ GUI_GUIDE.md (screenshots, walkthrough)
    ├─ TROUBLESHOOTING.md (common issues)
    └─ CHANGELOG.md (features, fixes, breaking changes)

14. datashield.spec
    └─ PyInstaller spec file

15. manifest.xml
    └─ Windows UAC manifest

16. Build & Test
    └─ PyInstaller → datashield.exe
    └─ Test executable functionality

**Phase 2 Exit Criteria**:
- ✅ GUI starts with Material Modern Neon Dark theme
- ✅ Scan button works, shows live progress
- ✅ Results table populated, clickable for details
- ✅ Vault encryption/decryption works
- ✅ Monitor mode detects new files
- ✅ All export formats generate correct output
- ✅ Task Scheduler integration working
- ✅ datashield.exe runs standalone (no Python required)
- ✅ All tests pass (>85% coverage)
- ✅ Full documentation
- ✅ Ready for v1.0.0 release

---

## 🔀 Bridging Strategy: Phase 1 → Phase 2

**Section 22** in the original blueprint is the **hinge**:

- Modules built in Phase 1: `scanner`, `pattern_engine`, `risk_scorer`, `app_fingerprint`, `storage`, `windows`, `cli`
- Modules built in Phase 2: `gui`, `vault`, `monitor`, `export`
- **Bridge point**: Both phases write to the same `storage/` (SQLite database)

**This means**:
- Phase 1 can complete independently: full CLI scanner + DB
- Phase 2 reads from Phase 1's DB: same data, different UI
- No refactoring needed when moving from Phase 1 → Phase 2
- Features can be developed in parallel after Phase 1 checkpoint

**Checkpoint Strategy**:
- After Phase 1, commit with tag `v0.1.0-cli-alpha`
- Phase 2 branches from `v0.1.0-cli-alpha`, not blocking Phase 1 completion
- Both phases can be tested independently

---

## 📊 Module Dependencies (Directed Acyclic Graph)

```
                          models.py
                              ↑
                    ┌─────────┼─────────┐
                    ↑         ↑         ↑
            exceptions.py  storage/  patterns/
                            ↑         ↑
                    ┌───────┼─────────┘
                    ↑       ↑
                entropy  pattern_engine
                    ↑       ↑
                    └───┬───┘
                        ↑
                  risk_scorer
                        ↑
    ┌───────────┬───────┼───────┬──────────┐
    ↑           ↑       ↑       ↑          ↑
app_     findings    scanner   vault    monitor
fingerprint.py                  ↑
    ↑           ↑       ↑       ↑          ↑
    └───────────┼───────┼───────┼──────────┘
                ↑       ↑       ↑
              cli/    windows/ export/
              (Phase 1)         (Phase 2)
```

**Key**: No circular dependencies. Strict layering.

---

## 🚦 Quality Gates

### Per-Module Exit Checklist

Each module completes only when:
- ✅ Code written (no TODOs, no placeholders)
- ✅ 100% coverage of public API documented (docstrings)
- ✅ Unit tests written (>85% line coverage)
- ✅ Integration test (if applicable)
- ✅ No linting errors (ruff)
- ✅ Type hints complete (mypy passing)
- ✅ Security check (bandit, dependency safety)
- ✅ README updated

### Per-Phase Exit Checklist

**Phase 1**:
- ✅ `datashield scan` fully functional
- ✅ All CLI commands working
- ✅ SQLite DB persists findings
- ✅ Tests >85% coverage
- ✅ Tag `v0.1.0-cli-alpha` committed

**Phase 2**:
- ✅ GUI launches, no crashes
- ✅ All widgets render correctly
- ✅ Theme dark/light toggles work
- ✅ Vault encryption/decryption works
- ✅ Monitor detects changes
- ✅ Export formats correct
- ✅ `datashield.exe` runs standalone
- ✅ Tests >85% coverage
- ✅ Full documentation
- ✅ Tag `v1.0.0` released

---

## 🛠️ Development Environment Setup

### Required Tools
- Python 3.13 (or 3.12 LTS)
- Git + GitHub account
- Visual Studio Build Tools (for pywin32)
- PyCharm Professional OR VS Code + Python extension

### Repository Setup
```bash
git clone https://github.com/usuario/data-shield.git
cd data-shield
python -m venv venv
.\venv\Scripts\activate
pip install -e ".[dev,test]"
```

### CI/CD Pipeline (GitHub Actions)
- **On push**: linting (ruff), type check (mypy), tests (pytest), security (bandit)
- **On PR**: all above + coverage report + code review
- **On release**: PyInstaller build → upload to releases

### Development Branches
- `main`: stable, tagged releases only
- `develop`: integration branch, Phase 1 + Phase 2 in progress
- `phase-1/*`: feature branches for Phase 1
- `phase-2/*`: feature branches for Phase 2

---

## 📈 Success Metrics (v1.0.0)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Coverage | ≥85% | `pytest --cov` |
| Performance | 100k files < 5 min | Benchmark suite |
| Security | 0 CVE | Bandit + safety |
| Stability | 0 unhandled exceptions | E2E testing |
| UX Fluency | All flows < 3 steps | User walkthrough |
| Documentation | 95% functions documented | Docstring check |
| Platform Support | Windows 10/11 | CI testing |

---

## 🎬 Next Immediate Steps

1. ✅ Create README.md (done)
2. ✅ Create IMPROVEMENTS.md (done)
3. ✅ Create requirements.txt (done)
4. ✅ Create .gitignore (done)
5. ✅ Create this ARCHITECTURE_PLAN.md (done)
6. ⬜ **Initialize Phase 1**: Create pyproject.toml + directory structure
7. ⬜ Verify all dependencies resolve without conflicts
8. ⬜ Set up CI/CD pipeline (GitHub Actions)
9. ⬜ Create first module: `core/models.py`
10. ⬜ Implement in strict dependency order per Phase 1 plan

---

## 📞 Implementation Contact Points

- **Architecture decisions**: Refer to this file + IMPROVEMENTS.md
- **Technical specifications**: Refer to DATA-SHIELD_prompt_FINGERPRINT.md
- **Visual reference**: data_shield_blueprint.html
- **User documentation**: README.md
- **Code style**: CONTRIBUTING.md (TBD)
- **Project status**: CHANGELOG.md (TBD)

---

**Data-Shield v1.0.0** — Precision-focused credential discovery & encryption for Windows developers.

🛡️ **"Protege tus secretos. Automáticamente."**
