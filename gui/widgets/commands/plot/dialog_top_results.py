from typing import Optional

import clarite
import pandas as pd
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QHBoxLayout, \
    QVBoxLayout, QPushButton, QGroupBox, QListWidget, QAbstractItemView, QFileDialog, QSpinBox, QComboBox, QCheckBox, \
    QDoubleSpinBox, QWidget
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from gui.models import Dataset
from gui.widgets import SelectColumnDialog
from gui.widgets.utilities import show_warning, QHLine


class TopResultsPlotDialog(QDialog):
    """
    This dialog controls settings for plotting a manhattan plot and displays it
    """

    PVALUE_TYPES = ["Raw", "Bonferroni", "FDR"]

    def __init__(self, *args, **kwargs):
        super(TopResultsPlotDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset_map: Optional[dict] = None
        self.dataset: Optional[Dataset] = None
        self.variables = []
        self.pvalue_type = self.PVALUE_TYPES[0]
        self.cutoff_enabled = True
        self.cutoff_value = 0.05
        self.cutoff = self.cutoff_value
        self.num_rows = 20
        self.figsize = (12, 6)
        self.dpi = 100
        # Setup UI
        self.setup_ui()
        # Initialize selection
        self.dataset_listwidget.setCurrentRow(0)

    def setup_ui(self):
        self.setWindowTitle(f"Top Results Plot")
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

        self.dataset_listwidget = QListWidget(self)
        self.dataset_listwidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dataset_map = dict()
        for all_dataset_idx, ds in enumerate(self.appctx.datasets):
            if ds.kind == 'ewas_result':
                self.dataset_listwidget.addItem(ds.name)
                self.dataset_map[len(self.dataset_listwidget) -1] = all_dataset_idx
        self.dataset_listwidget.itemSelectionChanged.connect(self.update_dataset_selection)
        left_layout.addRow(self.dataset_listwidget)

        left_layout.addRow(QHLine())

        # Pvalue Type
        self.pvalue_type_combobox = QComboBox(self)
        for option in self.PVALUE_TYPES:
            self.pvalue_type_combobox.addItem(option)
        self.pvalue_type_combobox.currentIndexChanged.connect(lambda idx: self.update_pvalue_type(idx))
        left_layout.addRow("Pvalue Type", self.pvalue_type_combobox)

        # Cutoff
        self.cutoff_widget = QWidget(parent=self)
        cutoff_layout = QHBoxLayout()
        self.cutoff_cb = QCheckBox(self)
        self.cutoff_cb.setChecked(self.cutoff_enabled)
        self.cutoff_cb.stateChanged.connect(self.update_cutoff)
        cutoff_layout.addWidget(self.cutoff_cb)
        cutoff_layout.addWidget(QLabel("Cutoff Line"))
        self.cutoff_sb = QDoubleSpinBox(self)
        self.cutoff_sb.setValue(self.cutoff_value)
        self.cutoff_sb.setSingleStep(0.001)
        self.cutoff_sb.setDecimals(3)
        self.cutoff_sb.setRange(0, 1)
        self.cutoff_sb.valueChanged.connect(self.update_cutoff_value)
        cutoff_layout.addWidget(self.cutoff_sb)
        self.cutoff_widget.setLayout(cutoff_layout)
        left_layout.addRow(self.cutoff_widget)

        # Show top n results
        self.show_top_n_sb = QSpinBox(self)
        self.show_top_n_sb.setValue(self.num_rows)
        self.show_top_n_sb.setMinimum(0)
        self.show_top_n_sb.setMaximum(50)
        left_layout.addRow("Show Top N Results", self.show_top_n_sb)
        self.show_top_n_sb.valueChanged.connect(self.change_num_rows)

        # Show/Reload plot button
        self.update_plot_btn = QPushButton("Update Plot", parent=self)
        self.update_plot_btn.setEnabled(False)  # False until a dataset is selected
        left_layout.addRow(self.update_plot_btn)
        self.update_plot_btn.clicked.connect(self.update_canvas)

        # Ok/Cancel       
        QBtn = QDialogButtonBox.Close

        self.buttonBox = QDialogButtonBox(QBtn)
        right_layout.addWidget(self.buttonBox)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    def update_canvas(self):
        self.canvas.figure.clear()
        # Plot by type
        if self.pvalue_type == "Raw":
            pvalue_name = "pvalue"
        elif self.pvalue_type == "Bonferroni":
            pvalue_name = "pvalue_bonferroni"
        elif self.pvalue_type == "FDR":
            pvalue_name = "pvalue_fdr"
        else:
            return

        title = f"Top Results for {self.dataset.name}"

        clarite.plot.top_results(ewas_result=self.dataset.df,
                                 pvalue_name=pvalue_name,
                                 cutoff=self.cutoff,
                                 num_rows=self.num_rows,
                                 figure=self.canvas.figure,
                                 title=title)

        self.canvas.draw()

    @pyqtSlot(int)
    def update_pvalue_type(self, idx):
        self.pvalue_type = self.PVALUE_TYPES[idx]

    @pyqtSlot(float)
    def update_cutoff_value(self, v):
        self.cutoff_value = v
        self.update_cutoff()

    def update_cutoff(self):
        self.cutoff_enabled = self.cutoff_cb.isChecked()
        if self.cutoff_enabled:
            self.cutoff = self.cutoff_value
        else:
            self.cutoff = None

    def update_dataset_selection(self):
        selected_idx = [i.row() for i in self.dataset_listwidget.selectedIndexes()]
        if len(selected_idx) == 0:
            self.update_plot_btn.setEnabled(False)
        else:
            self.update_plot_btn.setEnabled(True)
            print(selected_idx, type(selected_idx))
            selected_dataset = self.appctx.datasets[self.dataset_map[selected_idx[0]]]
            self.dataset = selected_dataset

    @pyqtSlot(int)
    def change_num_rows(self, n):
        self.num_rows = n
