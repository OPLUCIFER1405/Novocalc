"""Integration tests for NovaCalc UI, signals, history integration, and window interaction.
"""

import os
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from core.engine import AngleMode


@pytest.fixture(scope="session")
def qapp():
    """Ensure single QApplication instance exists for tests."""
    app = QApplication.instance()
    if app is None:
        # Use offscreen platform for headless testing
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        app = QApplication([])
    return app


@pytest.fixture
def window(qapp):
    win = MainWindow()
    yield win
    win.close()


def test_window_initialization(window):
    assert window.windowTitle() == "NovaCalc — Modern Scientific Calculator"
    assert window.engine.angle_mode == AngleMode.DEG
    assert window.display.get_result() == "0"
    assert window.display.get_expression() == ""


def test_ui_basic_calculation(window):
    window.display.set_expression("25 + 15")
    window.calculate()
    assert window.display.get_result() == "40"
    assert len(window.history_panel.get_entries()) == 1
    assert window.history_panel.get_entries()[0].result == "40"


def test_ui_scientific_deg_mode(window):
    window.set_angle_mode(AngleMode.DEG)
    window.display.set_expression("sin(30)")
    window.calculate()
    assert window.display.get_result() == "0.5"


def test_ui_scientific_rad_mode(window):
    window.set_angle_mode(AngleMode.RAD)
    window.display.set_expression("cos(0)")
    window.calculate()
    assert window.display.get_result() == "1"


def test_ui_division_by_zero_error_handling(window):
    window.display.set_expression("10 / 0")
    window.calculate()
    assert window.display.get_result() == "Error"
    # Expression is preserved
    assert window.display.get_expression() == "10 / 0"
    # Error message shown
    assert "divide by zero" in window.display.status_label.text().lower()


def test_ui_history_clear(window):
    window.display.set_expression("10 + 2")
    window.calculate()
    assert len(window.history_panel.get_entries()) == 1

    window.history_panel.clear_history()
    assert len(window.history_panel.get_entries()) == 0


def test_ui_keypad_insert(window):
    window.display.clear_expression()
    window._on_keypad_insert("7")
    window._on_keypad_insert(" + ")
    window._on_keypad_insert("3")
    assert window.display.get_expression() == "7 + 3"
    window.calculate()
    assert window.display.get_result() == "10"


def test_ui_sign_toggle(window):
    window.display.set_expression("42")
    window.toggle_sign()
    assert window.display.get_expression() == "-42"
    window.toggle_sign()
    assert window.display.get_expression() == "42"


def test_ui_history_navigation_arrows(window):
    window.display.set_expression("1 + 1")
    window.calculate()
    window.display.set_expression("2 + 2")
    window.calculate()

    window._navigate_history_up()
    assert window.display.get_expression() == "2 + 2"
    window._navigate_history_up()
    assert window.display.get_expression() == "1 + 1"
    window._navigate_history_down()
    assert window.display.get_expression() == "2 + 2"
