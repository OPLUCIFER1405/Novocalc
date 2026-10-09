"""NovaCalc — Modern Scientific Calculator.

Application entry point, resource path resolver, and Qt initialization.
"""

import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, supporting both development mode and PyInstaller bundles."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_stylesheet(app: QApplication) -> None:
    """Load and apply application dark theme QSS."""
    style_path = get_resource_path(os.path.join("styles", "dark_theme.qss"))
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main() -> int:
    """Main application routine."""
    app = QApplication(sys.argv)
    app.setApplicationName("NovaCalc")
    app.setApplicationDisplayName("NovaCalc")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("NovaCalc")

    # Set application icon
    icon_path = get_resource_path(os.path.join("assets", "icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Apply modern stylesheet
    load_stylesheet(app)

    # Launch main window
    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
