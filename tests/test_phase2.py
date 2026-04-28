"""Phase 2 tests for GUI, Vault, Monitor, Export."""

import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from datashield.vault.vault import Vault
from datashield.monitor.monitor import Monitor
from datashield.export.exporter import Exporter
from datashield.core.pattern_engine import PatternEngine
from datashield.core.events import EventBus
from datashield.gui.theme import ThemeManager


@pytest.fixture
def vault():
    """Create test vault."""
    return Vault()


@pytest.fixture
def monitor():
    """Create test monitor."""
    engine = PatternEngine()
    bus = EventBus()
    return Monitor(engine, bus)


@pytest.fixture
def exporter(tmp_path):
    """Create test exporter."""
    return Exporter(tmp_path)


@pytest.fixture
def app(qtbot):
    """Create QApplication."""
    return QApplication.instance() or QApplication([])


class TestVault:
    """Test Vault encryption."""

    def test_vault_init(self, vault):
        """Test vault initialization."""
        assert vault is not None
        assert vault.is_locked

    def test_set_password(self, vault):
        """Test setting password."""
        vault.set_password("test_password")
        assert not vault.is_locked
        assert vault.master_key is not None

    def test_encrypt_decrypt(self, vault):
        """Test encryption and decryption."""
        vault.set_password("test_password")

        plaintext = "my_secret_api_key"
        ct, iv, tag = vault.encrypt(plaintext)

        assert ct
        assert iv
        assert tag

        decrypted = vault.decrypt(ct, iv, tag)
        assert decrypted == plaintext

    def test_lock_unlock(self, vault):
        """Test lock/unlock."""
        vault.set_password("test_password")
        assert not vault.is_locked

        vault.lock()
        assert vault.is_locked

        vault.unlock("test_password")
        assert not vault.is_locked


class TestMonitor:
    """Test file monitoring."""

    def test_monitor_init(self, monitor):
        """Test monitor initialization."""
        assert monitor is not None
        assert not monitor.is_running

    def test_add_watch_dir(self, monitor):
        """Test adding watch directory."""
        monitor.add_watch_dir("/home/user/documents")
        assert "/home/user/documents" in monitor.watch_dirs

    def test_remove_watch_dir(self, monitor):
        """Test removing watch directory."""
        monitor.add_watch_dir("/home/user/documents")
        monitor.remove_watch_dir("/home/user/documents")
        assert "/home/user/documents" not in monitor.watch_dirs


class TestExporter:
    """Test result exporting."""

    def test_exporter_init(self, exporter):
        """Test exporter initialization."""
        assert exporter is not None
        assert exporter.output_dir.exists()

    def test_to_json(self, exporter, tmp_path):
        """Test JSON export."""
        from datashield.core.models import Finding, Confidence, DetectionLayer
        from datetime import datetime, timezone

        # Create mock finding
        finding = Finding(
            id="test-1",
            session_id="sess-1",
            file_path="/path/to/file.txt",
            file_name="file.txt",
            data_type="AWS Key",
            pattern_id="aws_key",
            sensitive_value="AKIAIOSFODNN7EXAMPLE",
            context_snippet="api_key=AKIAIOSFODNN7EXAMPLE",
            risk_score=90,
            confidence=Confidence.HIGH,
            detection_layer=DetectionLayer.REGEX,
            discovered_at=datetime.now(timezone.utc),
        )

        # Create mock session
        from datashield.storage.database import ScanSession
        session = ScanSession(
            id="sess-1",
            target_path="/home/user",
            mode="safe",
            status="completed",
        )

        # Export
        exporter_inst = Exporter(tmp_path)
        output = exporter_inst.to_json([finding], session)

        assert output.exists()
        assert output.suffix == ".json"

    def test_to_csv(self, exporter, tmp_path):
        """Test CSV export."""
        from datashield.core.models import Finding, Confidence, DetectionLayer
        from datetime import datetime, timezone

        finding = Finding(
            id="test-1",
            session_id="sess-1",
            file_path="/path/to/file.txt",
            file_name="file.txt",
            data_type="AWS Key",
            pattern_id="aws_key",
            sensitive_value="AKIAIOSFODNN7EXAMPLE",
            context_snippet="api_key=AKIAIOSFODNN7EXAMPLE",
            risk_score=90,
            confidence=Confidence.HIGH,
            detection_layer=DetectionLayer.REGEX,
            discovered_at=datetime.now(timezone.utc),
        )

        exporter_inst = Exporter(tmp_path)
        output = exporter_inst.to_csv([finding])

        assert output.exists()
        assert output.suffix == ".csv"

    def test_to_txt(self, exporter, tmp_path):
        """Test TXT export."""
        from datashield.core.models import Finding, Confidence, DetectionLayer
        from datashield.storage.database import ScanSession
        from datetime import datetime, timezone

        finding = Finding(
            id="test-1",
            session_id="sess-1",
            file_path="/path/to/file.txt",
            file_name="file.txt",
            data_type="AWS Key",
            pattern_id="aws_key",
            sensitive_value="AKIAIOSFODNN7EXAMPLE",
            context_snippet="api_key=AKIAIOSFODNN7EXAMPLE",
            risk_score=90,
            confidence=Confidence.HIGH,
            detection_layer=DetectionLayer.REGEX,
            discovered_at=datetime.now(timezone.utc),
        )

        session = ScanSession(
            id="sess-1",
            target_path="/home/user",
            mode="safe",
            status="completed",
        )

        exporter_inst = Exporter(tmp_path)
        output = exporter_inst.to_txt([finding], session)

        assert output.exists()
        assert output.suffix == ".txt"

    def test_to_html(self, exporter, tmp_path):
        """Test HTML export."""
        from datashield.core.models import Finding, Confidence, DetectionLayer
        from datashield.storage.database import ScanSession
        from datetime import datetime, timezone

        finding = Finding(
            id="test-1",
            session_id="sess-1",
            file_path="/path/to/file.txt",
            file_name="file.txt",
            data_type="AWS Key",
            pattern_id="aws_key",
            sensitive_value="AKIAIOSFODNN7EXAMPLE",
            context_snippet="api_key=AKIAIOSFODNN7EXAMPLE",
            risk_score=90,
            confidence=Confidence.HIGH,
            detection_layer=DetectionLayer.REGEX,
            discovered_at=datetime.now(timezone.utc),
        )

        session = ScanSession(
            id="sess-1",
            target_path="/home/user",
            mode="safe",
            status="completed",
        )

        exporter_inst = Exporter(tmp_path)
        output = exporter_inst.to_html([finding], session)

        assert output.exists()
        assert output.suffix == ".html"


class TestTheme:
    """Test theme management."""

    def test_theme_manager_init(self, app):
        """Test theme manager initialization."""
        manager = ThemeManager(app)
        assert manager is not None
        assert manager.current_theme == "dark"

    def test_set_theme(self, app):
        """Test setting theme."""
        manager = ThemeManager(app)
        manager.set_theme("light")
        assert manager.current_theme == "light"

    def test_toggle_theme(self, app):
        """Test toggling theme."""
        manager = ThemeManager(app)
        initial = manager.current_theme
        manager.toggle_theme()
        assert manager.current_theme != initial
