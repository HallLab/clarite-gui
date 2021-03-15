from typing import Optional

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontInfo
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QColorDialog,
    QFontDialog,
)


class FontPickerWidget(QWidget):
    """
    A font picker widget consisting of a name label and a button that updates when the font is changed
    """

    font_changed = pyqtSignal(QFont)

    def __init__(self, label_text, initial_font: QFont = QFont(), *args, **kwargs):
        super(FontPickerWidget, self).__init__(*args, **kwargs)
        self.label_text = label_text
        self.font = initial_font
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Label
        self.label = QLabel(self.label_text)
        layout.addWidget(self.label)

        # Button
        self.btn = QPushButton(self.get_font_display_str())
        self.btn.clicked.connect(self.get_font)
        self.refresh()
        layout.addWidget(self.btn)

    def get_font_display_str(self):
        info = QFontInfo(self.font)
        info_str = f"{info.pointSize()}pt {info.family()}"
        return info_str

    def get_font(self):
        font, ok = QFontDialog(parent=self).getFont(self.font)
        if ok and font != self.font:
            # Update stored font
            self.font = font
            # Update button
            self.refresh()
            # Emit signal
            self.font_changed.emit(self.font)

    def refresh(self, font: Optional[QFont] = None):
        """Update display of the widget, optionally setting font externally"""
        if font is not None:
            self.font = font
        self.btn.setText(self.get_font_display_str())
        self.btn.setFont(self.font)
