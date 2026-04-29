"""Pattern detection engine with 6-layer detection strategy."""

import re
import yara
from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from datetime import datetime, timezone
from ..core.models import Finding, DetectionLayer, Confidence
from ..core.entropy import _shannon_entropy
from ..patterns.regex_patterns import PATTERNS


class PatternEngine:
    """6-layer detection engine for credential patterns."""

    def __init__(self):
        """Initialize pattern engine."""
        self.regex_patterns = {}
        for pattern_name, pattern_info in PATTERNS.items():
            try:
                self.regex_patterns[pattern_name] = re.compile(pattern_info["regex"])
            except (KeyError, TypeError):
                pass
        self.yara_rules = self._load_yara_rules()
        self.entropy_threshold = 3.5

    def _load_yara_rules(self) -> Optional[yara.Rules]:
        """Load YARA rules from patterns directory."""
        try:
            rules_dir = Path(__file__).parent.parent / "patterns" / "yara_rules"
            if not rules_dir.exists():
                return None
                
            rule_files = {}
            for yar_file in rules_dir.glob("*.yar"):
                rule_files[yar_file.stem] = str(yar_file)
            
            if not rule_files:
                return None
                
            return yara.compile(filepaths=rule_files)
        except Exception:
            return None

    def detect_in_text(self, text: str, file_path: str, mode: str = "safe") -> List[Finding]:
        """Detect credentials using all layers based on mode."""
        findings = []
        path_obj = Path(file_path)
        file_name = path_obj.name.lower()

        # Layer 0: Filename detection (Always active)
        sensitive_filenames = {
            ".env": "Environment File",
            ".gitconfig": "Git Configuration",
            ".git-credentials": "Git Credentials",
            "config.yml": "App Configuration",
            "hosts.yml": "Auth Hosts (GH CLI)",
            "github.xml": "GitHub Settings (Android Studio)",
            "security.xml": "Security Settings",
            "credentials": "Cloud Credentials",
            "id_rsa": "SSH Private Key",
            "id_ed25519": "SSH Private Key",
            "master.key": "Master Key File",
            "vault.db": "Vault Database",
            "cookies": "Session Cookies (SQLite/LevelDB)",
            "local storage": "Web Storage Data",
            "globalstorage": "IDE Global Secrets",
            "session.json": "Session Tokens"
        }
        
        for s_name, s_type in sensitive_filenames.items():
            if s_name in file_name:
                findings.append(Finding(
                    id=str(uuid4()),
                    session_id="",
                    file_path=file_path,
                    file_name=path_obj.name,
                    data_type=f"file:{s_type}",
                    pattern_id=f"filename_{s_name}",
                    sensitive_value=f"[Sensitive File: {path_obj.name}]",
                    context_snippet=f"Detected sensitive file by name: {path_obj.name}",
                    risk_score=70,
                    confidence=Confidence.HIGH,
                    detection_layer=DetectionLayer.FILENAME,
                    discovered_at=datetime.now(timezone.utc),
                ))

        # Layer 1: Regex patterns (Always active)
        for pattern_name, pattern in self.regex_patterns.items():
            for match in pattern.finditer(text):
                findings.append(Finding(
                    id=str(uuid4()),
                    session_id="",
                    file_path=file_path,
                    file_name=path_obj.name,
                    data_type=f"pattern:{pattern_name}",
                    pattern_id=pattern_name,
                    sensitive_value=match.group()[:100],
                    context_snippet=match.group(),
                    risk_score=80,
                    confidence=Confidence.HIGH,
                    detection_layer=DetectionLayer.REGEX,
                    discovered_at=datetime.now(timezone.utc),
                ))

        # Skip intensive layers for ultra_fast
        if mode == "ultra_fast":
            return findings

        # Layer 2: YARA rules (Active in fast, safe, deep)
        if self.yara_rules:
            try:
                matches = self.yara_rules.match(data=text)
                for match in matches:
                    findings.append(Finding(
                        id=str(uuid4()),
                        session_id="",
                        file_path=file_path,
                        file_name=Path(file_path).name,
                        data_type=f"yara:{match.rule}",
                        pattern_id=match.rule,
                        sensitive_value="[YARA Match]",
                        context_snippet=str(match.strings[:3]),
                        risk_score=90,
                        confidence=Confidence.HIGH,
                        detection_layer=DetectionLayer.YARA,
                        discovered_at=datetime.now(timezone.utc),
                    ))
            except Exception:
                pass

        # Skip entropy for fast
        if mode == "fast":
            return findings

        # Layer 3: Entropy analysis (Active in safe, deep)
        # Skip entropy for binary/media extensions to avoid massive false positives
        binary_extensions = {
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".exe", ".dll", ".bin",
            ".zip", ".tar", ".gz", ".7z", ".rar", ".pyc", ".pyd", ".so", ".node",
            ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3", ".wav"
        }
        if path_obj.suffix.lower() in binary_extensions:
            return findings

        threshold = 4.5 if mode == "deep" else 5.2 # Increased from 3.5 to reduce noise
        for line in text.split("\n"):
            line = line.strip()
            if 15 < len(line) < 200: # Focused range for secrets
                entropy = _shannon_entropy(line.encode())
                if entropy > threshold:
                    findings.append(Finding(
                        id=str(uuid4()),
                        session_id="",
                        file_path=file_path,
                        file_name=Path(file_path).name,
                        data_type="entropy:high",
                        pattern_id="entropy",
                        sensitive_value=line[:50],
                        context_snippet=line[:200],
                        risk_score=int(60 if mode != "deep" else 75),
                        confidence=Confidence.MEDIUM,
                        detection_layer=DetectionLayer.ENTROPY,
                        discovered_at=datetime.now(timezone.utc),
                    ))

        return findings
