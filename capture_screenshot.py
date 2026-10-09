"""Captures high-resolution UI screenshots of NovaCalc for documentation and visual verification.
"""

import os
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from main import load_stylesheet
from ui.main_window import MainWindow
from core.engine import AngleMode


def capture():
    app = QApplication.instance() or QApplication(sys.argv)
    load_stylesheet(app)

    win = MainWindow()
    win.resize(920, 640)
    win.show()

    # Populate a few interesting calculations into history
    win.display.set_expression("25 * 4 + 10")
    win.calculate()

    win.display.set_expression("log(1000) * 5!")
    win.calculate()

    win.display.set_expression("sqrt(144) + 2pi")
    win.calculate()

    # Active calculation on screen
    win.display.set_expression("sin(30) + 12.5 × 2")
    win.calculate()

    # Let Qt process layout and styles
    app.processEvents()

    # Grab pixmap
    pixmap = win.grab()
    out_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "screenshot.png")
    pixmap.save(out_path, "PNG")
    print(f"Screenshot successfully saved to {out_path} ({pixmap.width()}x{pixmap.height()})")

    win.close()


if __name__ == "__main__":
    capture()
