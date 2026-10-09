"""Main window implementation for NovaCalc.

Assembles header, display, keypads, and history panel into a cohesive,
high-performance desktop experience.
"""

from __future__ import annotations
import os
from typing import List, Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.engine import AngleMode, CalculationEngine, CalculationResult
from .display import DisplayWidget
from .history_panel import HistoryPanel
from .keypad import KeypadWidget


class MainWindow(QMainWindow):
    """NovaCalc modern desktop scientific calculator main window."""

    DEFAULT_WIDTH = 900
    DEFAULT_HEIGHT = 620
    MIN_WIDTH = 700
    MIN_HEIGHT = 500

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaCalc — Modern Scientific Calculator")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Initialize calculation engine
        self.engine = CalculationEngine(AngleMode.DEG)

        # History navigation for arrow keys
        self._history_expressions: List[str] = []
        self._history_nav_index: int = -1

        self._setup_window_icon()
        self._setup_ui()
        self._connect_signals()
        self._update_angle_mode_ui()

    def _setup_window_icon(self):
        """Set application window icon if asset exists."""
        import sys
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _setup_ui(self):
        """Build main layout hierarchy."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)

        # Main Calculator Card
        self.calc_card = QFrame(central_widget)
        self.calc_card.setObjectName("mainCard")
        calc_layout = QVBoxLayout(self.calc_card)
        calc_layout.setContentsMargins(14, 14, 14, 14)
        calc_layout.setSpacing(12)

        # 1. Header Area
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # App branding title
        title_box = QHBoxLayout()
        title_box.setSpacing(6)
        title_label = QLabel("NovaCalc")
        title_label.setObjectName("appTitle")
        subtitle_label = QLabel("PRO")
        subtitle_label.setObjectName("appSubtitle")
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle_label)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Angle mode pill selector (DEG / RAD)
        angle_container = QFrame()
        angle_container.setObjectName("angleModeContainer")
        angle_layout = QHBoxLayout(angle_container)
        angle_layout.setContentsMargins(2, 2, 2, 2)
        angle_layout.setSpacing(2)

        self.btn_deg = QPushButton("DEG")
        self.btn_deg.setObjectName("btnDeg")
        self.btn_deg.setToolTip("Set angle mode to Degrees")
        self.btn_deg.clicked.connect(lambda: self.set_angle_mode(AngleMode.DEG))

        self.btn_rad = QPushButton("RAD")
        self.btn_rad.setObjectName("btnRad")
        self.btn_rad.setToolTip("Set angle mode to Radians")
        self.btn_rad.clicked.connect(lambda: self.set_angle_mode(AngleMode.RAD))

        angle_layout.addWidget(self.btn_deg)
        angle_layout.addWidget(self.btn_rad)
        header_layout.addWidget(angle_container)

        # History panel toggle button
        self.btn_toggle_history = QPushButton("History")
        self.btn_toggle_history.setObjectName("btnHeaderAction")
        self.btn_toggle_history.setProperty("active", True)
        self.btn_toggle_history.setToolTip("Toggle calculation history panel")
        self.btn_toggle_history.clicked.connect(self.toggle_history_panel)
        header_layout.addWidget(self.btn_toggle_history)

        calc_layout.addLayout(header_layout)

        # 2. Display Widget
        self.display = DisplayWidget(self.calc_card)
        calc_layout.addWidget(self.display)

        # 3. Keypad Widget
        self.keypad = KeypadWidget(self.calc_card)
        calc_layout.addWidget(self.keypad, 1)

        # Splitter to allow resizing calculator vs history panel
        self.splitter = QSplitter(Qt.Orientation.Horizontal, central_widget)
        self.splitter.addWidget(self.calc_card)

        # 4. History Panel
        self.history_panel = HistoryPanel(central_widget)
        self.splitter.addWidget(self.history_panel)

        # Set default splitter proportions (e.g., 68% calculator, 32% history)
        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 3)

        root_layout.addWidget(self.splitter)

    def _connect_signals(self):
        """Connect UI components and user actions."""
        # Display signals
        self.display.evaluateRequested.connect(self.calculate)
        self.display.clearRequested.connect(self.clear_expression)
        self.display.historyUpRequested.connect(self._navigate_history_up)
        self.display.historyDownRequested.connect(self._navigate_history_down)

        # Keypad signals
        self.keypad.insertRequested.connect(self._on_keypad_insert)
        self.keypad.evaluateRequested.connect(self.calculate)
        self.keypad.clearRequested.connect(self.clear_expression)
        self.keypad.clearAllRequested.connect(self.clear_all)
        self.keypad.backspaceRequested.connect(self.display.backspace)
        self.keypad.toggleSignRequested.connect(self.toggle_sign)

        # History signals
        self.history_panel.insertResultRequested.connect(self._on_history_insert_result)
        self.history_panel.restoreExpressionRequested.connect(self._on_history_restore_expr)
        self.history_panel.historyCleared.connect(self._on_history_cleared)

    # -------------------------------------------------------------------------
    # Core Actions & Logic
    # -------------------------------------------------------------------------

    def set_angle_mode(self, mode: AngleMode):
        """Update trigonometric angle mode in engine and UI."""
        self.engine.set_angle_mode(mode)
        self._update_angle_mode_ui()
        self.display.set_status(f"{mode.value} Mode • Ready")
        self.display.set_focus_to_input()

    def _update_angle_mode_ui(self):
        """Synchronize button pill styles with active angle mode."""
        is_deg = self.engine.angle_mode == AngleMode.DEG
        self.btn_deg.setProperty("active", is_deg)
        self.btn_rad.setProperty("active", not is_deg)

        self.btn_deg.style().unpolish(self.btn_deg)
        self.btn_deg.style().polish(self.btn_deg)
        self.btn_rad.style().unpolish(self.btn_rad)
        self.btn_rad.style().polish(self.btn_rad)

    def calculate(self):
        """Execute calculation of the current expression."""
        expr = self.display.get_expression().strip()
        if not expr:
            return

        result: CalculationResult = self.engine.evaluate(expr)

        if result.success:
            self.display.set_result(result.formatted_result)
            self.display.set_status(
                f"{result.angle_mode.value} Mode • Evaluated",
                is_success=True,
                is_error=False,
            )

            # Record in history
            self.history_panel.add_entry(
                expression=expr,
                result=result.formatted_result,
                angle_mode=result.angle_mode.value,
            )

            # Record in quick navigation history
            if not self._history_expressions or self._history_expressions[-1] != expr:
                self._history_expressions.append(expr)
            self._history_nav_index = len(self._history_expressions)

        else:
            # Keep user expression intact and report clear error message
            self.display.set_result("Error")
            err_msg = result.error_message or "Invalid expression"
            self.display.set_status(
                f"Error: {err_msg}",
                is_error=True,
                is_success=False,
            )

        self.display.set_focus_to_input()

    def clear_expression(self):
        """Clear the expression input while preserving previous result."""
        self.display.clear_expression()
        self.display.set_status(f"{self.engine.angle_mode.value} Mode • Cleared")

    def clear_all(self):
        """Clear expression, reset result display, and restore ready state."""
        self.display.clear_expression()
        self.display.set_result("0")
        self.display.set_status(f"{self.engine.angle_mode.value} Mode • Ready")

    def toggle_sign(self):
        """Toggle positive/negative sign of current expression or active number."""
        current = self.display.get_expression().strip()
        if not current:
            self.display.insert_text("-")
            return

        # If current is already wrapped in -(...)
        if current.startswith("-(") and current.endswith(")"):
            self.display.set_expression(current[2:-1])
        # If current is a simple negative number like -42
        elif current.startswith("-") and current[1:].replace(".", "", 1).isdigit():
            self.display.set_expression(current[1:])
        # If current is a simple positive number like 42
        elif current.replace(".", "", 1).isdigit():
            self.display.set_expression(f"-{current}")
        else:
            # Wrap compound expression in -(...)
            self.display.set_expression(f"-({current})")

    def toggle_history_panel(self):
        """Toggle history drawer visibility."""
        visible = not self.history_panel.isVisible()
        self.history_panel.setVisible(visible)
        self.btn_toggle_history.setProperty("active", visible)
        self.btn_toggle_history.style().unpolish(self.btn_toggle_history)
        self.btn_toggle_history.style().polish(self.btn_toggle_history)
        self.display.set_focus_to_input()

    def _on_keypad_insert(self, text: str):
        """Handle insertion from keypad buttons."""
        self.display.insert_text(text)

    def _on_history_insert_result(self, result_str: str):
        """Insert result from history item into current expression."""
        self.display.insert_text(result_str)

    def _on_history_restore_expr(self, expr_str: str):
        """Restore full historical expression."""
        self.display.set_expression(expr_str)

    def _on_history_cleared(self):
        """Handle history clear notification."""
        self._history_expressions.clear()
        self._history_nav_index = -1
        self.display.set_status("History cleared")

    def _navigate_history_up(self):
        """Navigate to earlier calculation expression using Up arrow."""
        if not self._history_expressions:
            return
        if self._history_nav_index > 0:
            self._history_nav_index -= 1
            self.display.set_expression(self._history_expressions[self._history_nav_index])

    def _navigate_history_down(self):
        """Navigate to later calculation expression using Down arrow."""
        if not self._history_expressions:
            return
        if self._history_nav_index < len(self._history_expressions) - 1:
            self._history_nav_index += 1
            self.display.set_expression(self._history_expressions[self._history_nav_index])
        else:
            self._history_nav_index = len(self._history_expressions)
            self.display.clear_expression()
