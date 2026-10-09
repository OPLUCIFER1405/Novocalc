"""Display widget for NovaCalc.

Contains the editable expression input, result display, and status feedback.
Supports direct typing, cursor navigation, and copy actions.
"""

from __future__ import annotations
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QApplication,
)
from PySide6.QtGui import QKeyEvent, QClipboard


class ExpressionLineEdit(QLineEdit):
    """Custom QLineEdit providing tailored keyboard navigation for calculator expressions."""

    evaluateRequested = Signal()
    clearRequested = Signal()
    historyUpRequested = Signal()
    historyDownRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("expressionInput")
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setPlaceholderText("0")

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.evaluateRequested.emit()
            event.accept()
            return

        elif key == Qt.Key.Key_Escape:
            self.clearRequested.emit()
            event.accept()
            return

        elif key == Qt.Key.Key_Up:
            self.historyUpRequested.emit()
            event.accept()
            return

        elif key == Qt.Key.Key_Down:
            self.historyDownRequested.emit()
            event.accept()
            return

        elif key == Qt.Key.Key_Equal:
            # Pressing '=' on keyboard evaluates current expression
            self.evaluateRequested.emit()
            event.accept()
            return

        super().keyPressEvent(event)


class DisplayWidget(QFrame):
    """Encapsulates the mathematical expression input, result display, and status feedback."""

    evaluateRequested = Signal()
    clearRequested = Signal()
    historyUpRequested = Signal()
    historyDownRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("displayCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Top Bar: Status / Mode info & Copy Result Action
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        self.status_label = QLabel("DEG Mode • Ready")
        self.status_label.setObjectName("statusFeedback")
        self.status_label.setProperty("hasError", False)
        self.status_label.setProperty("hasSuccess", False)
        top_bar.addWidget(self.status_label)

        top_bar.addStretch()

        self.btn_copy = QPushButton("Copy")
        self.btn_copy.setObjectName("btnHeaderAction")
        self.btn_copy.setToolTip("Copy result to clipboard")
        self.btn_copy.setFixedHeight(24)
        self.btn_copy.clicked.connect(self._copy_result_to_clipboard)
        top_bar.addWidget(self.btn_copy)

        layout.addLayout(top_bar)

        # Expression Input (Editable QLineEdit)
        self.expression_input = ExpressionLineEdit(self)
        self.expression_input.evaluateRequested.connect(self.evaluateRequested)
        self.expression_input.clearRequested.connect(self.clearRequested)
        self.expression_input.historyUpRequested.connect(self.historyUpRequested)
        self.expression_input.historyDownRequested.connect(self.historyDownRequested)
        layout.addWidget(self.expression_input)

        # Large Result Display
        self.result_label = QLabel("0")
        self.result_label.setObjectName("resultLabel")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.result_label)

    def set_expression(self, text: str):
        """Set the expression text and place cursor at end."""
        self.expression_input.setText(text)
        self.expression_input.setFocus()
        self.expression_input.setCursorPosition(len(text))

    def get_expression(self) -> str:
        """Get current expression text."""
        return self.expression_input.text()

    def insert_text(self, text: str):
        """Insert text at the current cursor position."""
        self.expression_input.setFocus()
        self.expression_input.insert(text)

    def backspace(self):
        """Delete character before cursor."""
        self.expression_input.setFocus()
        self.expression_input.backspace()

    def clear_expression(self):
        """Clear current expression text."""
        self.expression_input.clear()
        self.expression_input.setFocus()

    def set_result(self, text: str):
        """Set the calculated result text."""
        self.result_label.setText(text)

    def get_result(self) -> str:
        """Get current result string."""
        return self.result_label.text()

    def set_status(self, message: str, is_error: bool = False, is_success: bool = False):
        """Update status message label with contextual styling."""
        self.status_label.setText(message)
        self.status_label.setProperty("hasError", is_error)
        self.status_label.setProperty("hasSuccess", is_success)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_focus_to_input(self):
        """Ensure input receives focus."""
        self.expression_input.setFocus()

    def _copy_result_to_clipboard(self):
        """Copy the current result text to clipboard."""
        result = self.result_label.text().strip()
        if result and result != "Error":
            clipboard: QClipboard = QApplication.clipboard()
            clipboard.setText(result)
            orig_text = self.btn_copy.text()
            self.btn_copy.setText("Copied!")
            QTimer.singleShot(1500, lambda: self.btn_copy.setText(orig_text))
