import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QHBoxLayout, \
    QVBoxLayout, QPushButton, QGroupBox, QSpinBox
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from gui.widgets.select_column_dialog import SelectColumnDialog


class HistogramDialog(QDialog):
    """
    This dialog controls settings for plotting a histogram and displays it
    """
    def __init__(self, *args, **kwargs):
        super(HistogramDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.column = list(self.dataset.df)[0]
        self.bins = None
        self.figsize = (12, 5)
        self.dpi = 100
        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Plot Histogram")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QHBoxLayout()
        # Settings
        settings = QGroupBox("Plot Settings")
        left_layout = QFormLayout()
        settings.setLayout(left_layout)
        layout.addWidget(settings)
        # Plot
        right_layout = QVBoxLayout()
        layout.addLayout(right_layout)

        # Canvas
        fig = Figure(figsize=self.figsize, dpi=self.dpi)
        self.canvas = FigureCanvas(fig)
        right_layout.addWidget(self.canvas)

        # Toolbar
        self.canvas_toolbar = NavigationToolbar(self.canvas, self)
        right_layout.addWidget(self.canvas_toolbar)

        # Which column in the dataset
        self.column_btn = QPushButton("None", parent=self)
        self.column_btn.clicked.connect(self.launch_get_column)
        left_layout.addRow("Variable", self.column_btn)

        # Number of bins
        self.bins_sb = QSpinBox(parent=self)
        self.bins_sb.valueChanged.connect(self.update_bin_num)
        self.update_bin_setting()
        left_layout.addRow("Number of Bins", self.bins_sb)

        # Ok/Cancel       
        QBtn = QDialogButtonBox.Close
        
        self.buttonBox = QDialogButtonBox(QBtn)
        right_layout.addWidget(self.buttonBox)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

        # Plot inital selection
        self.column_btn.setText(f"{self.column}")
        self.update_canvas()

    def launch_get_column(self):
        """Launch a dialog to set the plotted column from the dataset"""
        column = SelectColumnDialog.get_column(columns=list(self.dataset.df),
                                               selected=self.column,
                                               parent=self)
        if column is not None:
            self.column = column
            self.column_btn.setText(f"{self.column}")
            self.update_bin_setting()
            self.update_canvas()

    def update_bin_setting(self):
        var_type = self.dataset.get_types()[self.column]
        var_unique_vals = self.dataset.df[self.column].nunique()
        if var_type == 'categorical':
            self.bins_sb.setEnabled(False)
            self.bins_sb.setRange(1, var_unique_vals)
            self.bins_sb.setValue(var_unique_vals)
        else:
            self.bins_sb.setEnabled(True)
            self.bins_sb.setRange(1, var_unique_vals)
            self.bins_sb.setValue(min(100, var_unique_vals))

    def update_canvas(self):
        self.canvas.figure.clear()
        clarite.plot.histogram(data=self.dataset.df, column=self.column, title=f"Histogram of {self.column}",
                               figure=self.canvas.figure, bins=self.bins)
        self.canvas.draw()

    @pyqtSlot(int)
    def update_bin_num(self, value):
        self.bins = value
        self.update_canvas()

