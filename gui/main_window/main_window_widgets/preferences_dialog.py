from PyQt5.QtCore import QSettings, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTabWidget, QWidget, QGroupBox, QFormLayout, QLabel, \
    QSpinBox, QHBoxLayout, QPushButton
from gui.widgets.utilities import ColorPickerWidget, FontPickerWidget


class PreferencesDialog(QDialog):
    """
    This dialog adjusts preferences
    """

    def __init__(self, *args, **kwargs):
        super(PreferencesDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # TODO: Add preferences settings
        self.setWindowTitle(f"CLARITE Preferences")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout()

        # Tabs
        self.tabs = QTabWidget(self)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tab_display = DisplayTab(self)
        self.tabs.addTab(self.tab_display, "Display")
        layout.addWidget(self.tabs)

        # Bottom row of buttons
        bottom_layout = QHBoxLayout()
        layout.addLayout(bottom_layout)
        # Reset
        self.default_btn = QPushButton("Default")
        self.default_btn.clicked.connect(self.use_default_settings)
        bottom_layout.addWidget(self.default_btn)
        # Spacer
        bottom_layout.addStretch()
        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        bottom_layout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    def submit(self):
        # Write settings from each tab
        self.tab_display.write_settings()
        # Refresh the display
        self.appctx.data_model.refresh()
        # Close the dialog
        self.accept()

    def use_default_settings(self):
        # Reset the current tab to default settings
        w = self.tabs.currentWidget()
        w.load_default_settings()
        w.refresh_ui()


class DisplayTab(QWidget):
    """
    Widget that holds the display settings.
    """
    # Settings groups controlled in this tab
    GROUP = "display"

    def __init__(self, *args, **kwargs):
        super(DisplayTab, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.read_settings()
        self.setup_ui()

    def load_default_settings(self):
        # display/header
        self.header_font = QFont("sans-serif", pointSize=12, weight=QFont.Bold, italic=False)
        # display/index
        self.index_font = QFont("sans-serif", pointSize=10, weight=QFont.Normal, italic=False)
        # display/data
        self.data_font = QFont("sans-serif", pointSize=10, weight=QFont.Normal, italic=False)
        self.data_bgcolor_unknown = QColor.fromRgb(255, 255, 255)
        self.data_bgcolor_binary = QColor.fromRgb(255, 204, 153)
        self.data_bgcolor_categorical = QColor.fromRgb(153, 204, 255)
        self.data_bgcolor_continuous = QColor.fromRgb(204, 153, 255)
        self.data_float_precision = 3

    def read_settings(self):
        # Load default settings first
        self.load_default_settings()

        # Override with any saved settings
        settings = QSettings(self.appctx.ORG, self.appctx.APPLICATION)

        # Read Header Settings
        settings.beginGroup("display/header")
        self.header_font = QFont(settings.value("font", defaultValue=self.header_font))
        settings.endGroup()

        # Read Index Settings
        settings.beginGroup("display/index")
        self.index_font = QFont(settings.value("font", defaultValue=self.index_font))
        settings.endGroup()

        # Read Data Settings
        settings.beginGroup("display/data")
        # Font
        self.data_font = QFont(settings.value("font", defaultValue=self.data_font))
        # Colors
        self.data_bgcolor_unknown = QColor(settings.value("bgcolor_unknown", defaultValue=self.data_bgcolor_unknown))
        self.data_bgcolor_binary = QColor(settings.value("bgcolor_binary", defaultValue=self.data_bgcolor_binary))
        self.data_bgcolor_categorical = QColor(settings.value("bgcolor_categorical",
                                                              defaultValue=self.data_bgcolor_categorical))
        self.data_bgcolor_continuous = QColor(settings.value("bgcolor_continuous",
                                                             defaultValue=self.data_bgcolor_continuous))
        # Float Precision
        self.data_float_precision = settings.value("float_precision", defaultValue=self.data_float_precision)
        settings.endGroup()

    def write_settings(self):
        settings = QSettings(self.appctx.ORG, self.appctx.APPLICATION)

        # Write Header settings
        settings.beginGroup("display/header")
        settings.setValue("font", self.header_font)
        settings.endGroup()

        # Write Index settings
        settings.beginGroup("display/index")
        settings.setValue("font", self.index_font)
        settings.endGroup()

        # Write Data settings
        settings.beginGroup("display/data")
        settings.setValue("font", self.data_font)
        settings.setValue("bgcolor_unknown", self.data_bgcolor_unknown)
        settings.setValue("bgcolor_binary", self.data_bgcolor_binary)
        settings.setValue("bgcolor_categorical", self.data_bgcolor_categorical)
        settings.setValue("bgcolor_continuous", self.data_bgcolor_continuous)
        settings.setValue("float_precision", self.data_float_precision)
        settings.endGroup()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header #
        ##########
        table_header_group = QGroupBox("Table Header", parent=self)
        table_header_layout = QFormLayout()
        table_header_group.setLayout(table_header_layout)
        layout.addWidget(table_header_group)

        # Font
        self.header_font_picker = FontPickerWidget("Font", self.header_font)
        table_header_layout.addWidget(self.header_font_picker)

        # Index #
        #########
        table_index_group = QGroupBox("Table Index", parent=self)
        table_index_layout = QVBoxLayout()
        table_index_group.setLayout(table_index_layout)
        layout.addWidget(table_index_group)

        # Font
        self.index_font_picker = FontPickerWidget("Font", self.index_font)
        table_index_layout.addWidget(self.index_font_picker)

        # Data #
        ########
        table_data_group = QGroupBox("Table Data", parent=self)
        table_data_layout = QVBoxLayout()
        table_data_group.setLayout(table_data_layout)
        layout.addWidget(table_data_group)

        # Font
        self.data_font_picker = FontPickerWidget("Font", self.data_font)
        table_data_layout.addWidget(self.data_font_picker)

        # Background Colors
        table_data_layout.addWidget(QLabel("Data Type Colors:"))
        # Unknown
        self.data_bgcolor_unknown_picker = ColorPickerWidget(label_text="\tUnknown",
                                                             initial_color=self.data_bgcolor_unknown,
                                                             initial_font=self.data_font)
        table_data_layout.addWidget(self.data_bgcolor_unknown_picker)
        # Binary
        self.data_bgcolor_binary_picker = ColorPickerWidget(label_text="\tBinary",
                                                            initial_color=self.data_bgcolor_binary,
                                                            initial_font=self.data_font)
        table_data_layout.addWidget(self.data_bgcolor_binary_picker)
        # Categorical
        self.data_bgcolor_categorical_picker = ColorPickerWidget(label_text="\tCategorical",
                                                                 initial_color=self.data_bgcolor_categorical,
                                                                 initial_font=self.data_font)
        table_data_layout.addWidget(self.data_bgcolor_categorical_picker)
        # Continuous
        self.data_bgcolor_continuous_picker = ColorPickerWidget(label_text="\tContinuous",
                                                                initial_color=self.data_bgcolor_continuous,
                                                                initial_font=self.data_font)
        table_data_layout.addWidget(self.data_bgcolor_continuous_picker)

        # Float precision
        self.float_precision_sb = QSpinBox()
        self.float_precision_sb.setRange(1, 10)
        self.float_precision_sb.setValue(self.data_float_precision)
        precision_layout = QHBoxLayout()
        precision_layout.addWidget(QLabel("Float Precision:"))
        precision_layout.addWidget(self.float_precision_sb)
        table_data_layout.addLayout(precision_layout)

        # Connections
        # Header
        self.header_font_picker.font_changed.connect(self.update_header_font)
        # Index
        self.index_font_picker.font_changed.connect(self.update_index_font)
        # Data - Font
        self.data_font_picker.font_changed.connect(self.update_data_font)
        self.data_font_picker.font_changed.connect(lambda f: self.data_bgcolor_unknown_picker.refresh(font=f))
        self.data_font_picker.font_changed.connect(lambda f: self.data_bgcolor_binary_picker.refresh(font=f))
        self.data_font_picker.font_changed.connect(lambda f: self.data_bgcolor_categorical_picker.refresh(font=f))
        self.data_font_picker.font_changed.connect(lambda f: self.data_bgcolor_continuous_picker.refresh(font=f))
        # Data - Colors
        self.data_bgcolor_unknown_picker.color_changed.connect(self.update_data_bgcolor_unknown)
        self.data_bgcolor_binary_picker.color_changed.connect(self.update_data_bgcolor_binary)
        self.data_bgcolor_categorical_picker.color_changed.connect(self.update_data_bgcolor_categorical)
        self.data_bgcolor_continuous_picker.color_changed.connect(self.update_data_bgcolor_continuous)
        # Data - Precision
        self.float_precision_sb.valueChanged.connect(self.update_float_precision)

    def refresh_ui(self):
        """Adjust the UI to match the current settings"""
        # Header
        self.header_font_picker.refresh(font=self.header_font)
        # Index
        self.index_font_picker.refresh(font=self.index_font)
        # Data
        self.data_font_picker.refresh(font=self.data_font)
        self.data_bgcolor_unknown_picker.refresh(color=self.data_bgcolor_unknown, font=self.data_font)
        self.data_bgcolor_binary_picker.refresh(color=self.data_bgcolor_binary, font=self.data_font)
        self.data_bgcolor_categorical_picker.refresh(color=self.data_bgcolor_categorical, font=self.data_font)
        self.data_bgcolor_continuous_picker.refresh(color=self.data_bgcolor_continuous, font=self.data_font)
        self.float_precision_sb.setValue(self.data_float_precision)

    # Setting update slots #
    ########################

    # Header
    def update_header_font(self, font: QFont):
        self.header_font = font

    # Index
    def update_index_font(self, font: QFont):
        self.index_font = font

    # Data
    def update_data_font(self, font: QFont):
        self.data_font = font

    def update_data_bgcolor_unknown(self, color):
        self.data_bgcolor_unknown = color

    def update_data_bgcolor_binary(self, color):
        self.data_bgcolor_binary = color

    def update_data_bgcolor_categorical(self, color):
        self.data_bgcolor_categorical = color

    def update_data_bgcolor_continuous(self, color):
        self.data_bgcolor_continuous = color

    def update_float_precision(self, value):
        self.data_float_precision = value
