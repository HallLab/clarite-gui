import clarite
import pandas as pd
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QHBoxLayout, \
    QVBoxLayout, QPushButton, QGroupBox, QListWidget, QAbstractItemView, QFileDialog, QSpinBox
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from gui.widgets import SelectColumnDialog
from gui.widgets.utilities import show_warning, QHLine


class ManhattanPlotDialog(QDialog):
    """
    This dialog controls settings for plotting a manhattan plot and displays it
    """
    def __init__(self, *args, **kwargs):
        super(ManhattanPlotDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.datasets = dict()
        self.variables = []
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
            variables = variables | set(df.index.get_level_values('variable'))
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
        clarite.plot.manhattan(dfs=self.datasets,
                               categories=self.categories,
                               num_labeled=self.label_top_n,
                               label_vars=[self.label_specific],
                               figure=self.canvas.figure
                               )
        self.canvas.draw()

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
            show_warning("Variable Categories File Error", f"Expected 2 columns, found {len(list(categories)):,} columns")
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
