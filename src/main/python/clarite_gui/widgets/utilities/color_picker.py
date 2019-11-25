from typing import Optional

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QColorDialog


class ColorPickerWidget(QWidget):
    """
    A color picker widget consisting of a name label and a button that updates when the color is changed
    """
    color_changed = pyqtSignal(QColor)

    def __init__(self,
                 label_text,
                 initial_color: QColor = QColor.fromRgb(255, 255, 255),
                 initial_font: QFont = QFont(),
                 *args, **kwargs):
        super(ColorPickerWidget, self).__init__(*args, **kwargs)
        self.label_text = label_text
        self.color = initial_color
        self.font = initial_font
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Label
        self.label = QLabel(self.label_text)
        layout.addWidget(self.label)

        # Button
        self.btn = QPushButton(self.color.name())
        self.btn.setFont(self.font)
        self.btn.clicked.connect(self.get_color)
        self.refresh()
        layout.addWidget(self.btn)

    def get_color(self):
        color = QColorDialog.getColor()
        if color.isValid() and color != self.color:
            # Update stored color
            self.color = color
            # Update button
            self.refresh(color=self.color)
            # Emit signal
            self.color_changed.emit(self.color)

    def refresh(self, color: Optional[QColor] = None, font: Optional[QFont] = None):
        """
        Update display of the widget, optionally setting color and/or font externally
        """
        if color is not None:
            self.color = color
        if font is not None:
            self.font = font
        self.btn.setText(self.color.name())
        self.btn.setStyleSheet(f"border: 1px solid black;"
                               f"background-color: {self.color.name()};"
                               f"padding: 5;")
        self.btn.setFont(self.font)
