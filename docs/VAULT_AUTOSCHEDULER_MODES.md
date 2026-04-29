# Vault Auto-Schedule System & Operation Modes

**Purpose**: Flexible encryption/decryption scheduling and three operation modes for different user needs.

---

## Part 1: Vault Auto-Schedule System

### Overview

The Vault auto-schedule system allows Data-Shield to automatically encrypt/decrypt files at specific times (e.g., daily at shutdown/startup). **CRITICALLY: This is OFF by default** — user must explicitly enable it.

### Feature Flags

```yaml
vault:
  auto_schedule:
    enabled: false                    # DEFAULT: OFF (user must enable)
    mode: "manual"                    # "manual" | "auto_encrypt_daily" | "auto_decrypt_on_login"
    
    # If mode == "auto_encrypt_daily"
    encrypt_at_time: null            # e.g., "22:00" (10 PM daily)
    encrypt_on_event: "shutdown"     # "shutdown" | "logoff" | "timer"
    
    # If mode == "auto_decrypt_on_login"
    decrypt_on_startup: false        # Decrypt when Windows starts
    decrypt_on_user_login: false     # Decrypt when user logs in
    
    # Windows Task Scheduler integration
    task_scheduler:
      enabled: false
      auto_create: false             # Don't auto-create tasks
      task_names:
        encrypt: "DataShield_AutoEncrypt"
        decrypt: "DataShield_AutoDecrypt"
```

### Workflows

#### Workflow 1: Manual Encrypt/Decrypt (Always Available)

```
User clicks: "Vault → Encrypt Selected Files"
  ↓
Dialog: Enter master password
  ↓
Encrypt (using mode: performance/safe/interactive)
  ↓
Result: Files .ds-vault'd, originals deleted
```

#### Workflow 2: Auto-Encrypt at Shutdown (Optional, User Enables)

**Setup** (one-time):
```
User: Settings → Vault → Auto-Encrypt Daily
  ├─ Toggle: [OFF] ← default
  └─ If clicks [ON]:
      ├─ Ask: "Time to encrypt?" → 22:00 (10 PM)
      ├─ Ask: "Master password?" → ••••••
      ├─ Create Windows Task Scheduler task
      └─ Save preference to config
```

**Daily execution** (if enabled):
```
10 PM (22:00)
  ↓
Task Scheduler triggers
  ↓
datashield-vault encrypt-all --mode [performance|safe] --master-password-hash [cached]
  ↓
All files in Vault encrypted to .ds-vault
  ↓
Notification: "Vault encrypted successfully"
```

#### Workflow 3: Auto-Decrypt on Login (Optional, User Enables)

**Setup** (one-time):
```
User: Settings → Vault → Auto-Decrypt on Startup
  ├─ Toggle: [OFF] ← default
  └─ If clicks [ON]:
      ├─ Ask: "Auto-decrypt on startup?" (Yes/No)
      ├─ Create Windows Task Scheduler task (RunOnce at startup)
      ├─ **IMPORTANT**: Task asks for master password interactively
      │  (encrypted with DPAPI, only current user can access)
      └─ Save preference to config
```

**On Windows startup** (if enabled):
```
User logs in
  ↓
Task Scheduler triggers (runs as SYSTEM or user session)
  ↓
Dialog: "Enter Vault Master Password"
  ↓
User enters password
  ↓
datashield-vault decrypt-all --mode [performance|safe] --master-password [input]
  ↓
All .ds-vault files restored to original location/filename
  ↓
Notification: "Vault decrypted successfully"
```

### Implementation Details (`vault/scheduler.py`)

```python
class VaultAutoScheduler:
    """Windows Task Scheduler integration for auto encrypt/decrypt."""
    
    def __init__(self, config: VaultConfig):
        self.config = config
        self.enabled = config.auto_schedule.enabled
    
    def enable_auto_encrypt(self, time_of_day: str = "22:00", master_password: str = None):
        """
        Enable daily auto-encryption at specified time.
        
        Args:
            time_of_day: "HH:MM" format, e.g., "22:00"
            master_password: User's vault master password (never stored, only hashed)
        
        Process:
            1. Hash master password with bcrypt (store hash in secure location)
            2. Create Windows Task Scheduler task:
               - Trigger: Daily at 22:00
               - Action: datashield-vault encrypt-all --mode [config] --password-hash [hash]
               - Run as: Current user
            3. Save enabled state to config (DPAPI protected)
        """
        
        if not master_password:
            raise ValueError("Master password required")
        
        # Hash password with bcrypt (one-way)
        password_hash = bcrypt.hashpw(master_password.encode(), bcrypt.gensalt())
        
        # Create task
        task = create_task_scheduler_task(
            task_name="DataShield_AutoEncrypt",
            trigger="daily",
            trigger_time=time_of_day,
            action=f'datashield-vault encrypt-all --password-hash "{password_hash}"',
            run_as="current_user",
            run_level="highest"  # Require admin
        )
        
        # Save config
        self.config.auto_schedule.enabled = True
        self.config.auto_schedule.encrypt_at_time = time_of_day
        self.config.save()  # DPAPI protected
        
        logger.info(f"Auto-encryption enabled: {time_of_day} daily")
    
    def disable_auto_encrypt(self):
        """Disable auto-encryption, delete Task Scheduler task."""
        delete_task_scheduler_task("DataShield_AutoEncrypt")
        self.config.auto_schedule.enabled = False
        self.config.save()
        logger.info("Auto-encryption disabled")
    
    def enable_auto_decrypt_on_startup(self, master_password: str = None):
        """
        Enable auto-decryption on Windows startup.
        
        Note: This is tricky because we need the master password.
        
        Strategy:
        1. Encrypt the master password with DPAPI (user's credentials)
        2. Store encrypted password in config (only current user can decrypt)
        3. On startup, decrypt with DPAPI and use for auto-decrypt
        4. Task Scheduler runs with user's credentials (not SYSTEM)
        """
        
        if not master_password:
            raise ValueError("Master password required")
        
        # Encrypt with DPAPI (only user can decrypt)
        from datashield.vault.dpapi import dpapi_encrypt, dpapi_decrypt
        encrypted = dpapi_encrypt(master_password.encode())
        
        # Create task
        task = create_task_scheduler_task(
            task_name="DataShield_AutoDecrypt",
            trigger="at_startup",
            trigger_delay="30 seconds",  # Wait 30s after login
            action=f'datashield-vault decrypt-all --mode performance',
            run_as="current_user",
            run_level="highest"
        )
        
        # Save encrypted password
        self.config.auto_schedule.decrypt_on_startup = True
        self.config.vault.master_password_encrypted = encrypted  # DPAPI
        self.config.save()
        
        logger.info("Auto-decryption enabled on startup")
    
    def disable_auto_decrypt(self):
        """Disable auto-decryption, delete task."""
        delete_task_scheduler_task("DataShield_AutoDecrypt")
        self.config.auto_schedule.decrypt_on_startup = False
        self.config.vault.master_password_encrypted = None
        self.config.save()
        logger.info("Auto-decryption disabled")
```

### Security Considerations

1. **Master Password**: Never stored in plaintext
   - For auto-encrypt: hashed with bcrypt (one-way, can't recover)
   - For auto-decrypt: encrypted with DPAPI (user can decrypt)

2. **Task Scheduler**: Tasks run with "Run Level: Highest" (require admin)

3. **Decryption on Startup**: User sees dialog before decryption happens

4. **Config Storage**: All settings encrypted with DPAPI in config file

---

## Part 2: Operation Modes

### Three Modes: Performance, Safe, Interactive

#### Mode 1: **PERFORMANCE** (Default for most users)

```yaml
scanner:
  mode: "performance"
  settings:
    max_threads: 16                  # Max concurrent threads
    cpu_usage: "aggressive"          # 80-100% CPU if available
    ram_usage: "aggressive"          # Use up to 70% available RAM
    gpu_acceleration: true           # Use GPU if available (CUDA/OpenCL)
    batch_size: 1000                 # Process 1000 files before yield
    progress_update_interval: 100ms  # Update UI every 100ms
    cache_patterns: true             # Aggressive pattern caching
    prefetch_next_files: true        # Read-ahead next files
```

**Behavior**:
- Uses all available CPU cores
- Maintains large buffer of files in memory
- GPU acceleration for entropy analysis (if available)
- Pattern matching optimized for speed over memory
- Progress updates frequently for responsiveness

**Result**: 100k files in ~2-3 minutes (most aggressive)

**Use case**: Full disk scan on desktop, not urgent production system

---

#### Mode 2: **SAFE** (Lower resource usage)

```yaml
scanner:
  mode: "safe"
  settings:
    max_threads: 4                   # Fewer threads
    cpu_usage: "conservative"        # 30-50% CPU
    ram_usage: "conservative"        # Use up to 30% available RAM
    gpu_acceleration: false          # Don't use GPU
    batch_size: 100                  # Smaller batches
    progress_update_interval: 1000ms # Update UI every 1s
    cache_patterns: false            # Minimal caching
    prefetch_next_files: false       # No read-ahead
```

**Behavior**:
- Uses 4 threads (vs 16 in performance)
- Small file buffers
- Regular disk I/O (vs aggressive buffering)
- Simpler pattern matching (less memory)
- Less frequent progress updates

**Result**: 100k files in ~8-10 minutes (conservative)

**Use case**: Run during work hours without impacting other apps

---

#### Mode 3: **INTERACTIVE** (User decision-making)

```yaml
scanner:
  mode: "interactive"
  settings:
    max_threads: 4
    cpu_usage: "conservative"
    pauses_on_finding: true          # NEW: Pause after each finding
    action_required: true             # Wait for user action
    timeout_seconds: 300              # 5 min timeout if no response
    auto_action_on_timeout: "skip"    # Action if timeout: skip|continue|abort
```

**Behavior**:
```
Scanning... 1,234 files processed

⚠️ FINDING DETECTED:
   Type: SSH Private Key (id_rsa)
   Path: C:\Users\Miguel\.ssh\id_rsa
   Risk: CRITICAL (95/100)
   App: Git

What do you want to do?
  [1] Continue scanning
  [2] View details
  [3] Encrypt now
  [4] Skip this file
  [5] Stop scanning
  
> (waiting for input...)

If no input for 5 minutes → auto-skip and continue
```

**Result**: User reviews each critical finding as discovered

**Use case**: First-time scan, review high-risk findings

---

### Mode Selection

#### CLI
```bash
# Performance (default)
datashield scan C:\Users --mode performance

# Safe
datashield scan C:\Users --mode safe

# Interactive
datashield scan C:\Users --mode interactive
```

#### GUI
```
[Scan Options Panel]

Mode: ○ Performance  ● Safe  ○ Interactive
      (O) Default  (Low resource)  (User review)

[Info] Performance: ~2-3 min for 100k files, uses full system
[Info] Safe: ~8-10 min for 100k files, low impact on system
[Info] Interactive: Pauses on findings, requires user input
```

#### Programmatic
```python
from datashield.core.scanner import Scanner, ScanConfig, OperationMode

config = ScanConfig(
    root_path="C:\\Users",
    mode=OperationMode.INTERACTIVE,  # Enum: PERFORMANCE, SAFE, INTERACTIVE
)

scanner = Scanner(config)
async for finding in scanner.scan():
    # In interactive mode, scan pauses here
    # User must take action before continuing
    print(f"Found: {finding}")
```

---

### Implementation in `core/scanner.py`

```python
from enum import Enum

class OperationMode(Enum):
    """Three operation modes for different use cases."""
    PERFORMANCE = "performance"  # Max speed, resource aggressive
    SAFE = "safe"                # Low impact, slower
    INTERACTIVE = "interactive"  # User-guided, decision at each finding

class ScanConfig:
    mode: OperationMode = OperationMode.SAFE  # Default
    
    # Mode-specific overrides
    max_threads: int = None  # If None, use default for mode
    progress_interval_ms: int = None
    interactive_timeout_seconds: int = 300
    
    def apply_mode_defaults(self):
        """Apply defaults based on mode."""
        if self.mode == OperationMode.PERFORMANCE:
            self.max_threads = self.max_threads or 16
            self.progress_interval_ms = self.progress_interval_ms or 100
            # ... more aggressive settings
        elif self.mode == OperationMode.SAFE:
            self.max_threads = self.max_threads or 4
            self.progress_interval_ms = self.progress_interval_ms or 1000
            # ... conservative settings
        elif self.mode == OperationMode.INTERACTIVE:
            self.max_threads = self.max_threads or 4
            self.pause_on_finding = True
            # ... interactive settings

class Scanner:
    async def scan(self) -> AsyncIterator[Finding]:
        """
        Async generator that yields findings.
        
        In INTERACTIVE mode:
        - Yields finding
        - Waits for user action (continue, skip, encrypt, abort)
        - Continues based on action
        """
        
        if self.config.mode == OperationMode.INTERACTIVE:
            # Hook into UI event loop
            for finding in findings:
                yield finding
                # UI pauses here, waits for user action
                # Events: continue_scan, skip_file, encrypt_now, stop_scan
                action = await self._wait_for_user_action(timeout=self.config.interactive_timeout_seconds)
                
                if action == "encrypt_now":
                    # Encrypt immediately
                    await self.vault.encrypt_file(finding.file_path)
                elif action == "skip_file":
                    continue
                elif action == "stop_scan":
                    break
        else:
            # PERFORMANCE or SAFE: no pausing
            async for finding in self._scan_files():
                yield finding
```

---

## Integration

### CLI Command Examples

```bash
# Manual encryption (any mode)
datashield vault encrypt C:\Users\.ssh\id_rsa

# Manual decryption
datashield vault decrypt C:\Users\.ssh\id_rsa

# Enable auto-encrypt at 22:00 (requires user input for password)
datashield vault schedule --auto-encrypt --time 22:00

# Enable auto-decrypt on startup
datashield vault schedule --auto-decrypt-startup

# Disable auto-features
datashield vault schedule --disable-all

# Run scan in interactive mode
datashield scan C:\Users --mode interactive

# Run scan in performance mode
datashield scan C:\Users --mode performance
```

### GUI Controls

```
[Vault Panel]
┌─────────────────────────────┐
│ Encryption & Automation     │
├─────────────────────────────┤
│                             │
│ Manual Actions:             │
│ [Encrypt Selected]  [Decrypt Selected]
│                             │
│ Auto-Schedule:              │
│ ☐ Auto-encrypt daily at 22:00
│ ☐ Auto-decrypt on startup
│                             │
│ Status:                     │
│ ✓ 47 files in vault        │
│ ✗ Auto-encrypt disabled    │
│ ✗ Auto-decrypt disabled    │
│                             │
└─────────────────────────────┘

[Scan Panel]
┌─────────────────────────────┐
│ Scan Mode                   │
├─────────────────────────────┤
│ ○ Performance (fast, uses resources)
│ ● Safe (slow, low impact)
│ ○ Interactive (user review)
└─────────────────────────────┘
```

---

## Security & Considerations

### Passwords
- **Never stored**: Master password only in memory during use
- **Hashed**: For auto-encrypt, stored as bcrypt hash (one-way)
- **Encrypted**: For auto-decrypt, stored with DPAPI (user recoverable)

### Task Scheduler
- **Requires Admin**: Tasks created with "Run Level: Highest"
- **User-owned**: Tasks run as current user, not SYSTEM
- **Auditable**: All task creations logged to Windows Event Log

### Interactive Mode
- **User Control**: Complete control over each finding
- **Timeout**: 5 min timeout with auto-action if no input
- **Logging**: All user actions logged for audit trail

---

## Roadmap

### v1.0.0 (MVP)
- ✅ Manual encrypt/decrypt
- ✅ Auto-encrypt at daily time (Task Scheduler)
- ✅ PERFORMANCE and SAFE modes
- ☐ INTERACTIVE mode (v1.1)
- ☐ Auto-decrypt on startup (v1.1)

### v1.1
- ✅ INTERACTIVE mode fully implemented
- ✅ Auto-decrypt on startup
- ✅ Timeout + auto-action on interactive mode

### v1.2
- ✅ GPU acceleration (PERFORMANCE mode)
- ✅ Machine learning for mode selection
- ✅ Energy usage optimization (SAFE mode)
