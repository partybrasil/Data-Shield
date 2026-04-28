"""Basic tests for Phase 1."""

import pytest
from pathlib import Path
from sqlalchemy.orm import Session
from datashield.config.loader import load_config
from datashield.storage.database import init_db, get_session
from datashield.core.scanner import Scanner
from datashield.core.pattern_engine import PatternEngine
from datashield.core.entropy import _shannon_entropy


@pytest.fixture
def config():
    """Get test configuration."""
    return load_config()


@pytest.fixture
def db_session():
    """Create in-memory test database."""
    SessionLocal = init_db("sqlite:///:memory:")
    session = get_session(SessionLocal)
    yield session
    session.close()


class TestPatternEngine:
    """Test pattern detection engine."""

    def test_pattern_engine_init(self):
        """Test pattern engine initialization."""
        engine = PatternEngine()
        assert engine is not None
        assert engine.regex_patterns is not None

    def test_detect_api_key_pattern(self):
        """Test API key pattern detection."""
        engine = PatternEngine()
        text = "api_key = sk_live_51234567890abcdef"
        findings = engine.detect_in_text(text, "test.py")
        assert len(findings) > 0

    def test_high_entropy_detection(self):
        """Test high entropy string detection."""
        engine = PatternEngine()
        text = "random_string_x7f9k2m1n0o"
        findings = engine.detect_in_text(text, "test.py")
        # Should detect high entropy
        assert any(f.pattern_id == "entropy" for f in findings)


class TestEntropy:
    """Test entropy calculations."""

    def test_low_entropy(self):
        """Test low entropy string."""
        entropy = _shannon_entropy(b"aaaa")
        assert entropy < 1.0

    def test_high_entropy(self):
        """Test high entropy string."""
        entropy = _shannon_entropy(b"x7f9k2m1n0o")
        assert entropy > 2.0


class TestScanner:
    """Test file scanner."""

    def test_scanner_init(self, config, db_session):
        """Test scanner initialization."""
        scanner = Scanner(config.scan, db_session)
        assert scanner is not None
        assert scanner.pattern_engine is not None

    def test_get_files(self, config, db_session, tmp_path):
        """Test file discovery."""
        # Create test files
        (tmp_path / "test.txt").write_text("api_key=123")
        (tmp_path / "test2.txt").write_text("password=456")

        scanner = Scanner(config.scan, db_session)
        files = scanner._get_files(tmp_path)

        assert len(files) >= 2

    def test_scan_directory(self, config, db_session, tmp_path):
        """Test directory scanning."""
        # Create test file with credential
        (tmp_path / "test.py").write_text("api_key = 'sk_live_1234567890'")

        scanner = Scanner(config.scan, db_session)
        session_id = scanner.scan(str(tmp_path))

        assert session_id is not None


class TestConfig:
    """Test configuration loading."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        config = load_config()
        assert config is not None
        assert config.scan.mode == "safe"
        assert config.scan.max_file_size == 104857600


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
