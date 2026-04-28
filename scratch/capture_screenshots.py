import sys
import os
from PySide6.QtWidgets import QApplication, QTabWidget
from PySide6.QtCore import QTimer
from datashield.gui.main_window import MainWindow
from datashield.gui.theme import ThemeManager
from datashield.core.models import Finding, Confidence, DetectionLayer
from datetime import datetime, timezone

def capture_gui():
    app = QApplication(sys.argv)
    
    # Mock services
    window = MainWindow()
    theme_manager = ThemeManager(app)
    window.set_theme_manager(theme_manager)
    
    # Add dummy findings to results table
    for i in range(5):
        finding = Finding(
            id=f"test-{i}",
            session_id="sess-1",
            file_path=f"C:\\Users\\User\\project\\secret_{i}.txt",
            file_name=f"secret_{i}.txt",
            data_type="Generic Credential",
            pattern_id="high_entropy",
            sensitive_value="x" * 20,
            context_snippet=f"password = {'x' * 20}",
            risk_score=85 - (i * 10),
            confidence=Confidence.HIGH,
            detection_layer=DetectionLayer.ENTROPY,
            discovered_at=datetime.now(timezone.utc),
        )
        window.results_table.add_finding(finding)
    
    # Set to Dark Theme
    theme_manager.set_theme("dark")
    window.show()
    window.resize(1000, 600)
    
    # Force process events to render
    app.processEvents()
    
    # Save Scanner Tab
    window.grab().save("gui_scanner_dark.png")
    print("Saved gui_scanner_dark.png")
    
    # Find TabWidget
    tab_widget = window.findChild(QTabWidget)
    if tab_widget:
        # Switch to Vault Tab
        tab_widget.setCurrentIndex(1)
        app.processEvents()
        window.grab().save("gui_vault_dark.png")
        print("Saved gui_vault_dark.png")
        
        # Switch back to Scanner and set Light Theme
        theme_manager.set_theme("light")
        tab_widget.setCurrentIndex(0)
        app.processEvents()
        window.grab().save("gui_scanner_light.png")
        print("Saved gui_scanner_light.png")

    app.quit()

if __name__ == "__main__":
    capture_gui()
