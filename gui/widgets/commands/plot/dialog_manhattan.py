import clarite
import pandas as pd
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QHBoxLayout, \
    QVBoxLayout, QPushButton, QGroupBox, QListWidget, QAbstractItemView, QFileDialog, QSpinBox, QComboBox, QCheckBox, \
    QDoubleSpinBox, QWidget
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from gui.widgets import SelectColumnDialog
from gui.widgets.utilities import show_warning, QHLine


class ManhattanPlotDialog(QDialog):
    """
    This dialog controls settings for plotting a manhattan plot and displays it
    """

    PVALUE_TYPES = ["Raw", "Bonferroni", "FDR"]

    def __init__(self, *args, **kwargs):
        super(ManhattanPlotDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.datasets = dict()
        self.variables = []
        self.pvalue_type = self.PVALUE_TYPES[0]
        self.cutoff_bonferroni_enabled = True
        self.cutoff_bonferroni_value = 0.05
        self.cutoff_fdr_enabled = False
        self.cutoff_fdr_value = 0.05
        self.categories = dict()
        self.label_top_n = 3
        self.label_specific = None
        self.figsize = (12, 6)
        self.dpi = 100
        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Manhattan Plot")
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

        # Which datasets
        self.datasets_label = QLabel("No Datasets Selected", parent=self)
        left_layout.addRow(self.datasets_label)

        self.dataset_listwidget = QListWidget(self)
        for ds in self.appctx.datasets:
            if ds.kind == 'ewas_result':
                self.dataset_listwidget.addItem(ds.name)
        self.dataset_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dataset_listwidget.itemSelectionChanged.connect(self.update_dataset_selection)
        left_layout.addRow(self.dataset_listwidget)

        left_layout.addRow(QHLine())

        # Pvalue Type
        self.pvalue_type_combobox = QComboBox(self)
        for option in self.PVALUE_TYPES:
            self.pvalue_type_combobox.addItem(option)
        self.pvalue_type_combobox.currentIndexChanged.connect(lambda idx: self.update_pvalue_type(idx))
        left_layout.addRow("Pvalue Type", self.pvalue_type_combobox)

        # Bonferroni Cutoff
        self.cutoff_bonferroni_widget = QWidget(parent=self)
        cutoff_bonferroni_layout = QHBoxLayout()
        self.cutoff_bonferroni_cb = QCheckBox(self)
        self.cutoff_bonferroni_cb.setChecked(self.cutoff_bonferroni_enabled)
        self.cutoff_bonferroni_cb.stateChanged.connect(self.update_cutoffs)
        cutoff_bonferroni_layout.addWidget(self.cutoff_bonferroni_cb)
        cutoff_bonferroni_layout.addWidget(QLabel("Bonferroni Cutoff"))
        self.cutoff_bonferroni_sb = QDoubleSpinBox(self)
        self.cutoff_bonferroni_sb.setValue(self.cutoff_bonferroni_value)
        self.cutoff_bonferroni_sb.setSingleStep(0.001)
        self.cutoff_bonferroni_sb.setDecimals(3)
        self.cutoff_bonferroni_sb.setRange(0, 1)
        self.cutoff_bonferroni_sb.valueChanged.connect(self.update_bonferroni_cutoff_value)
        cutoff_bonferroni_layout.addWidget(self.cutoff_bonferroni_sb)
        self.cutoff_bonferroni_widget.setLayout(cutoff_bonferroni_layout)
        left_layout.addRow(self.cutoff_bonferroni_widget)

        # FDR Cutoff
        self.cutoff_fdr_widget = QWidget(parent=self)
        cutoff_fdr_layout = QHBoxLayout()
        self.cutoff_fdr_cb = QCheckBox(self)
        self.cutoff_fdr_cb.setChecked(self.cutoff_fdr_enabled)
        self.cutoff_fdr_cb.stateChanged.connect(self.update_cutoffs)
        cutoff_fdr_layout.addWidget(self.cutoff_fdr_cb)
        cutoff_fdr_layout.addWidget(QLabel("FDR Cutoff"))
        self.cutoff_fdr_sb = QDoubleSpinBox(self)
        self.cutoff_fdr_sb.setValue(self.cutoff_fdr_value)
        self.cutoff_fdr_sb.setSingleStep(0.001)
        self.cutoff_fdr_sb.setDecimals(3)
        self.cutoff_fdr_sb.setRange(0, 1)
        self.cutoff_fdr_sb.valueChanged.connect(self.update_fdr_cutoff_value)
        cutoff_fdr_layout.addWidget(self.cutoff_fdr_sb)
        self.cutoff_fdr_widget.setLayout(cutoff_fdr_layout)
        left_layout.addRow(self.cutoff_fdr_widget)

        # Categories - Loaded from a file
        self.category_file_btn = QPushButton("Not Set", parent=self)
        self.category_file_btn.clicked.connect(self.launch_get_category_file)
        left_layout.addRow("Variable Categories", self.category_file_btn)

        # Label top results
        self.label_top_n_sb = QSpinBox(self)
        self.label_top_n_sb.setValue(3)
        self.label_top_n_sb.setMinimum(0)
        self.label_top_n_sb.setMaximum(50)
        left_layout.addRow("Label Top N Results", self.label_top_n_sb)
        self.label_top_n_sb.valueChanged.connect(self.change_label_top_n)

        # Label specific results
        self.label_specific_btn = QPushButton("None Selected", parent=self)
        self.label_specific_btn.setEnabled(False)  # False until datasets are selected
        self.label_specific_btn.clicked.connect(self.launch_get_specific)
        left_layout.addRow("Label Specific Variable", self.label_specific_btn)

        # Show/Reload plot button
        self.update_plot_btn = QPushButton("Update Plot", parent=self)
        self.update_plot_btn.setEnabled(False)  # False until datasets are selected
        left_layout.addRow(self.update_plot_btn)
        self.update_plot_btn.clicked.connect(self.update_canvas)

        # Ok/Cancel       
        QBtn = QDialogButtonBox.Close

        self.buttonBox = QDialogButtonBox(QBtn)
        right_layout.addWidget(self.buttonBox)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    def update_dataset_selection(self):
        selected_names = [i.text() for i in self.dataset_listwidget.selectedItems()]
        self.datasets = {d.name: d.df
                         for d in self.appctx.datasets
                         if d.name in selected_names}

        # Update variables
        variables = set()
        for df in self.datasets.values():
            variables = variables | set(df.index.get_level_values('Variable'))
        self.variables = list(variables)

        # Update label listing how many datasets are selected
        if len(self.datasets) == 0:
            self.datasets_label.setText("No Datasets Selected (0 variables)")
            self.label_specific_btn.setText("None Selected")
            self.label_specific_btn.setEnabled(False)
            self.label_specific = None
            self.update_plot_btn.setEnabled(False)
        elif len(self.datasets) == 1:
            self.datasets_label.setText(f"1 Dataset Selected ({len(self.variables):,} variables)")
            self.label_specific_btn.setEnabled(True)
            self.update_plot_btn.setEnabled(True)
        else:
            self.datasets_label.setText(f"{len(self.datasets):,} Datasets Selected ({len(self.variables):,} variables)")
            self.label_specific_btn.setEnabled(True)
            self.update_plot_btn.setEnabled(True)

    def update_canvas(self):
        self.canvas.figure.clear()
        # Cutoff lines
        if self.cutoff_bonferroni_enabled:
            bonferroni = self.cutoff_bonferroni_value
        else:
            bonferroni = None
        if self.cutoff_fdr_enabled:
            fdr = self.cutoff_fdr_value
        else:
            fdr = None
        # Plot by type
        if self.pvalue_type == "Raw":
            clarite.plot.manhattan(dfs=self.datasets,
                                   categories=self.categories,
                                   bonferroni=bonferroni,
                                   fdr=fdr,
                                   num_labeled=self.label_top_n,
                                   label_vars=[self.label_specific],
                                   figure=self.canvas.figure)
        elif self.pvalue_type == "Bonferroni":
            clarite.plot.manhattan_bonferroni(dfs=self.datasets,
                                              categories=self.categories,
                                              cutoff=bonferroni,
                                              num_labeled=self.label_top_n,
                                              label_vars=[self.label_specific],
                                              figure=self.canvas.figure)
        elif self.pvalue_type == "FDR":
            clarite.plot.manhattan_fdr(dfs=self.datasets,
                                       categories=self.categories,
                                       cutoff=fdr,
                                       num_labeled=self.label_top_n,
                                       label_vars=[self.label_specific],
                                       figure=self.canvas.figure)
        self.canvas.draw()

    @pyqtSlot(int)
    def update_pvalue_type(self, idx):
        self.pvalue_type = self.PVALUE_TYPES[idx]
        self.update_cutoffs()

    @pyqtSlot(float)
    def update_bonferroni_cutoff_value(self, v):
        self.cutoff_bonferroni_value = v
        self.update_cutoffs()

    @pyqtSlot(float)
    def update_fdr_cutoff_value(self, v):
        self.cutoff_fdr_value = v
        self.update_cutoffs()

    def update_cutoffs(self):
        if self.pvalue_type == "Bonferroni":
            # Enable Bonferroni
            self.cutoff_bonferroni_cb.setEnabled(True)
            self.cutoff_bonferroni_sb.setEnabled(True)
            # Uncheck and Disable FDR
            self.cutoff_fdr_cb.setChecked(False)
            self.cutoff_fdr_cb.setEnabled(False)
            self.cutoff_fdr_sb.setEnabled(False)
        elif self.pvalue_type == "FDR":
            # Uncheck and Disable Bonferroni
            self.cutoff_bonferroni_cb.setChecked(False)
            self.cutoff_bonferroni_cb.setEnabled(False)
            self.cutoff_bonferroni_sb.setEnabled(False)
            # Enable FDR
            self.cutoff_fdr_cb.setEnabled(True)
            self.cutoff_fdr_sb.setEnabled(True)
        elif self.pvalue_type == "Raw":
            # Enable both
            self.cutoff_bonferroni_cb.setEnabled(True)
            self.cutoff_bonferroni_sb.setEnabled(True)
            self.cutoff_fdr_cb.setEnabled(True)
            self.cutoff_fdr_sb.setEnabled(True)

        # Enable/Disable Bonferroni
        self.cutoff_bonferroni_enabled = self.cutoff_bonferroni_cb.isChecked()
        self.cutoff_bonferroni_sb.setEnabled(self.cutoff_bonferroni_enabled)
        # Enable/Disable FDR
        self.cutoff_fdr_enabled = self.cutoff_fdr_cb.isChecked()
        self.cutoff_fdr_sb.setEnabled(self.cutoff_fdr_enabled)

    def launch_get_category_file(self):
        """Launch a dialog to load a file which specified categories for each variable"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  f"Load Variable Category File",
                                                  "",
                                                  f"TSV Files (*.tsv *.txt)",
                                                  options=options)
        # Set filename
        if len(filename) == 0:
            return

        # Read file
        try:
            categories = pd.read_csv(filename, sep="\t")
        except Exception as e:
            show_warning("Variable Categories File Error", f"Error reading file: {str(e)}")
            return

        # Must have two columns
        if len(list(categories)) != 2:
            show_warning("Variable Categories File Error",
                         f"Expected 2 columns, found {len(list(categories)):,} columns")
            return

        # Set columns and convert to a dictionary
        categories.columns = ['variable', 'category']
        categories = categories.set_index('variable')
        categories = categories.to_dict()['category']

        self.categories = categories
        self.category_file_btn.setText(f"{len(categories):,} variable categories loaded")

    @pyqtSlot(int)
    def change_label_top_n(self, n):
        self.label_top_n = n

    def launch_get_specific(self):
        """Launch a dialog to select a specific variable for labeling"""
        specific = SelectColumnDialog.get_column(columns=self.variables,
                                                 selected=self.label_specific,
                                                 parent=self)
        if specific is not None:
            self.label_specific = specific
            self.label_specific_btn.setText(f"{self.label_specific}")
        else:
            self.label_specific = None
            self.label_specific_btn.setText(f"None Selected")
