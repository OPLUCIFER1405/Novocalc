"""Keypad widgets for NovaCalc: Scientific and Numeric keypads.

Provides organized grids for numbers, arithmetic operators, scientific functions,
constants, parentheses, and evaluation controls.
"""

from __future__ import annotations
from typing import Callable
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class KeypadButton(QPushButton):
    """Custom styled push button for NovaCalc keypad."""

    def __init__(self, text: str, css_class: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("calcBtn")
        self.setProperty("class", css_class)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Keep focus in expression input


class KeypadWidget(QWidget):
    """Combines scientific and numeric keypads with categorized buttons."""

    # Signals
    insertRequested = Signal(str)
    evaluateRequested = Signal()
    clearRequested = Signal()
    clearAllRequested = Signal()
    backspaceRequested = Signal()
    toggleSignRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # 1. Scientific Keypad Frame
        sci_frame = QFrame(self)
        sci_frame.setObjectName("keypadContainer")
        sci_layout = QGridLayout(sci_frame)
        sci_layout.setContentsMargins(8, 8, 8, 8)
        sci_layout.setSpacing(6)

        # Scientific buttons layout: (label, insert_text, css_class, row, col)
        sci_buttons = [
            ("sin", "sin(", "calc-btn btn-sci", 0, 0),
            ("cos", "cos(", "calc-btn btn-sci", 0, 1),
            ("tan", "tan(", "calc-btn btn-sci", 0, 2),
            ("asin", "asin(", "calc-btn btn-sci", 1, 0),
            ("acos", "acos(", "calc-btn btn-sci", 1, 1),
            ("atan", "atan(", "calc-btn btn-sci", 1, 2),
            ("log₁₀", "log(", "calc-btn btn-sci", 2, 0),
            ("ln", "ln(", "calc-btn btn-sci", 2, 1),
            ("eˣ", "exp(", "calc-btn btn-sci", 2, 2),
            ("√x", "sqrt(", "calc-btn btn-sci", 3, 0),
            ("x²", "^2", "calc-btn btn-sci", 3, 1),
            ("xʸ", "^", "calc-btn btn-sci", 3, 2),
            ("n!", "!", "calc-btn btn-sci", 4, 0),
            ("|x|", "|", "calc-btn btn-sci", 4, 1),
            ("π", "π", "calc-btn btn-sci", 4, 2),
            ("e", "e", "calc-btn btn-sci", 5, 0),
            ("(", "(", "calc-btn btn-util", 5, 1),
            (")", ")", "calc-btn btn-util", 5, 2),
        ]

        for text, insert_val, css, r, c in sci_buttons:
            btn = KeypadButton(text, css, sci_frame)
            btn.clicked.connect(lambda checked=False, val=insert_val: self.insertRequested.emit(val))
            sci_layout.addWidget(btn, r, c)

        main_layout.addWidget(sci_frame, 3)

        # 2. Numeric and Arithmetic Keypad Frame
        num_frame = QFrame(self)
        num_frame.setObjectName("keypadContainer")
        num_layout = QGridLayout(num_frame)
        num_layout.setContentsMargins(8, 8, 8, 8)
        num_layout.setSpacing(6)

        # Row 0: Clear & Edit
        btn_c = KeypadButton("C", "calc-btn btn-danger", num_frame)
        btn_c.setToolTip("Clear expression (Esc)")
        btn_c.clicked.connect(self.clearRequested.emit)
        num_layout.addWidget(btn_c, 0, 0)

        btn_ac = KeypadButton("AC", "calc-btn btn-danger", num_frame)
        btn_ac.setToolTip("Clear all and reset")
        btn_ac.clicked.connect(self.clearAllRequested.emit)
        num_layout.addWidget(btn_ac, 0, 1)

        btn_back = KeypadButton("DEL", "calc-btn btn-danger", num_frame)
        btn_back.setToolTip("Delete previous character (Backspace)")
        btn_back.clicked.connect(self.backspaceRequested.emit)
        num_layout.addWidget(btn_back, 0, 2)

        btn_div = KeypadButton("÷", "calc-btn btn-op", num_frame)
        btn_div.clicked.connect(lambda: self.insertRequested.emit(" ÷ "))
        num_layout.addWidget(btn_div, 0, 3)

        # Row 1: 7, 8, 9, ×
        self._add_num_btn(num_layout, "7", 1, 0, num_frame)
        self._add_num_btn(num_layout, "8", 1, 1, num_frame)
        self._add_num_btn(num_layout, "9", 1, 2, num_frame)
        btn_mul = KeypadButton("×", "calc-btn btn-op", num_frame)
        btn_mul.clicked.connect(lambda: self.insertRequested.emit(" × "))
        num_layout.addWidget(btn_mul, 1, 3)

        # Row 2: 4, 5, 6, −
        self._add_num_btn(num_layout, "4", 2, 0, num_frame)
        self._add_num_btn(num_layout, "5", 2, 1, num_frame)
        self._add_num_btn(num_layout, "6", 2, 2, num_frame)
        btn_sub = KeypadButton("−", "calc-btn btn-op", num_frame)
        btn_sub.clicked.connect(lambda: self.insertRequested.emit(" − "))
        num_layout.addWidget(btn_sub, 2, 3)

        # Row 3: 1, 2, 3, +
        self._add_num_btn(num_layout, "1", 3, 0, num_frame)
        self._add_num_btn(num_layout, "2", 3, 1, num_frame)
        self._add_num_btn(num_layout, "3", 3, 2, num_frame)
        btn_add = KeypadButton("+", "calc-btn btn-op", num_frame)
        btn_add.clicked.connect(lambda: self.insertRequested.emit(" + "))
        num_layout.addWidget(btn_add, 3, 3)

        # Row 4: ±, 0, ., %
        btn_sign = KeypadButton("±", "calc-btn btn-num", num_frame)
        btn_sign.setToolTip("Toggle sign (+/-)")
        btn_sign.clicked.connect(self.toggleSignRequested.emit)
        num_layout.addWidget(btn_sign, 4, 0)

        self._add_num_btn(num_layout, "0", 4, 1, num_frame)

        btn_dot = KeypadButton(".", "calc-btn btn-num", num_frame)
        btn_dot.clicked.connect(lambda: self.insertRequested.emit("."))
        num_layout.addWidget(btn_dot, 4, 2)

        btn_mod = KeypadButton("%", "calc-btn btn-op", num_frame)
        btn_mod.setToolTip("Modulo (%)")
        btn_mod.clicked.connect(lambda: self.insertRequested.emit(" % "))
        num_layout.addWidget(btn_mod, 4, 3)

        # Row 5: Equals spans across the bottom
        btn_eq = KeypadButton("=", "calc-btn btn-equals", num_frame)
        btn_eq.setToolTip("Calculate (Enter)")
        btn_eq.clicked.connect(self.evaluateRequested.emit)
        num_layout.addWidget(btn_eq, 5, 0, 1, 4)

        main_layout.addWidget(num_frame, 4)

    def _add_num_btn(self, layout: QGridLayout, digit: str, r: int, c: int, parent: QWidget):
        btn = KeypadButton(digit, "calc-btn btn-num", parent)
        btn.clicked.connect(lambda checked=False, val=digit: self.insertRequested.emit(val))
        layout.addWidget(btn, r, c)
