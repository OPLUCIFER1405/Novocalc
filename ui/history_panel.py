"""History panel widget for NovaCalc.

Displays a scrollable log of previous successful calculations, allowing users
to review, copy, restore expressions, and reuse results.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QAction, QCursor


@dataclass
class HistoryEntry:
    """Represents a single historical calculation record."""
    expression: str
    result: str
    angle_mode: str


class HistoryItemWidget(QFrame):
    """Visual card displaying a single calculation history entry."""

    clicked = Signal(str)  # emits result string to insert
    doubleClicked = Signal(str)  # emits original expression to restore

    def __init__(self, entry: HistoryEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setObjectName("historyCardItem")
        self.setProperty("class", "history-item-card")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # Header: Expression + Mode badge
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        expr_label = QLabel(self.entry.expression)
        expr_label.setProperty("class", "history-item-expr")
        expr_label.setWordWrap(True)
        header_layout.addWidget(expr_label, 1)

        mode_badge = QLabel(self.entry.angle_mode)
        mode_badge.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        header_layout.addWidget(mode_badge, 0, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(header_layout)

        # Result line
        res_label = QLabel(f"= {self.entry.result}")
        res_label.setProperty("class", "history-item-res")
        layout.addWidget(res_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.entry.result)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit(self.entry.expression)
        super().mouseDoubleClickEvent(event)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        action_insert = menu.addAction("Insert Result into Expression")
        action_restore = menu.addAction("Restore Expression")
        action_copy_res = menu.addAction("Copy Result")
        action_copy_expr = menu.addAction("Copy Expression")

        chosen = menu.exec(self.mapToGlobal(pos))
        if chosen == action_insert:
            self.clicked.emit(self.entry.result)
        elif chosen == action_restore:
            self.doubleClicked.emit(self.entry.expression)
        elif chosen == action_copy_res:
            QApplication.clipboard().setText(self.entry.result)
        elif chosen == action_copy_expr:
            QApplication.clipboard().setText(self.entry.expression)


class HistoryPanel(QFrame):
    """Panel widget maintaining calculation history in session memory."""

    insertResultRequested = Signal(str)
    restoreExpressionRequested = Signal(str)
    historyCleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyPanel")
        self.setMinimumWidth(260)
        self._entries: List[HistoryEntry] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Top Bar: Title, Count, Clear Button
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        title = QLabel("History")
        title.setObjectName("historyHeaderTitle")
        top_bar.addWidget(title)

        self.count_label = QLabel("(0)")
        self.count_label.setObjectName("historyCountLabel")
        top_bar.addWidget(self.count_label)

        top_bar.addStretch()

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setObjectName("btnClearHistory")
        self.btn_clear.setToolTip("Clear all calculation history")
        self.btn_clear.clicked.connect(self.clear_history)
        top_bar.addWidget(self.btn_clear)

        layout.addLayout(top_bar)

        # Scrollable container for history items
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("historyScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.container_widget = QWidget()
        self.container_widget.setObjectName("historyListWidget")
        self.items_layout = QVBoxLayout(self.container_widget)
        self.items_layout.setContentsMargins(0, 4, 0, 4)
        self.items_layout.setSpacing(8)
        self.items_layout.addStretch()

        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)

        # Empty state label
        self.empty_label = QLabel("No previous calculations.\nComplete a calculation to see history here.")
        self.empty_label.setObjectName("historyEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.items_layout.insertWidget(0, self.empty_label)

    def add_entry(self, expression: str, result: str, angle_mode: str):
        """Add a successful calculation result to the history."""
        entry = HistoryEntry(expression=expression, result=result, angle_mode=angle_mode)
        self._entries.append(entry)

        self.empty_label.hide()
        self.count_label.setText(f"({len(self._entries)})")

        # Create item widget
        item_widget = HistoryItemWidget(entry, self.container_widget)
        item_widget.clicked.connect(self.insertResultRequested.emit)
        item_widget.doubleClicked.connect(self.restoreExpressionRequested.emit)

        # Insert at the top of the history list (most recent first)
        self.items_layout.insertWidget(0, item_widget)

    def clear_history(self):
        """Remove all history records and reset empty state."""
        self._entries.clear()
        self.count_label.setText("(0)")

        # Remove item widgets
        for i in reversed(range(self.items_layout.count())):
            item = self.items_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget and widget != self.empty_label:
                widget.deleteLater()

        self.empty_label.show()
        self.historyCleared.emit()

    def get_entries(self) -> List[HistoryEntry]:
        """Return all history entries."""
        return list(self._entries)
