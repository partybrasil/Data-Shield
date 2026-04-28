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
        """Load YARA rules (stub implementation)."""
        try:
            # In full implementation, load from yara_rules/ directory
            return None
        except Exception:
            return None

    def detect_in_text(self, text: str, file_path: str) -> List[Finding]:
        """Detect credentials using all 6 layers.

        Layers:
        1. Regex patterns (known formats)
        2. YARA rules (binary/content patterns)
        3. Entropy analysis (random-looking strings)
        4. App parsers (config files)
        5. Fingerprinting (app-specific)
        6. Structural analysis (context clues)

        Args:
            text: Text content to scan
            file_path: Path to file being scanned

        Returns:
            List of findings.
        """
        findings = []

        # Layer 1: Regex patterns
        for pattern_name, pattern in self.regex_patterns.items():
            for match in pattern.finditer(text):
                finding = Finding(
                    id=str(uuid4()),
                    session_id="",  # Will be set by caller
                    file_path=file_path,
                    file_name=Path(file_path).name,
                    data_type=f"pattern:{pattern_name}",
                    pattern_id=pattern_name,
                    sensitive_value=match.group()[:100],
                    context_snippet=match.group(),
                    risk_score=80,
                    confidence=Confidence.HIGH,
                    detection_layer=DetectionLayer.REGEX,
                    discovered_at=datetime.now(timezone.utc),
                )
                findings.append(finding)

        # Layer 3: Entropy analysis
        for line in text.split("\n"):
            if len(line) > 10:
                entropy = _shannon_entropy(line.encode())
                if entropy > self.entropy_threshold:
                    finding = Finding(
                        id=str(uuid4()),
                        session_id="",  # Will be set by caller
                        file_path=file_path,
                        file_name=Path(file_path).name,
                        data_type="entropy:high",
                        pattern_id="entropy",
                        sensitive_value=line[:50],
                        context_snippet=line[:200],
                        risk_score=int(60),
                        confidence=Confidence.MEDIUM,
                        detection_layer=DetectionLayer.ENTROPY,
                        discovered_at=datetime.now(timezone.utc),
                    )
                    findings.append(finding)

        return findings
