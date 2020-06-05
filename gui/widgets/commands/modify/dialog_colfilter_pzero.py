import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QPushButton, QDoubleSpinBox, QLineEdit

from gui.models import Dataset
from gui.widgets import SkipOnlyDialog
from gui.widgets.utilities import warnings, RunProgress


class ColfilterPZeroDialog(QDialog):
    """
    This dialog sets settings for colfilter percent zero
    """
    def __init__(self, *args, **kwargs):
        super(ColfilterPZeroDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.filter_percent = 90.0
        self.skip = None
        self.only = None
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        filter_percent = self.filter_percent
        skip = self.skip
        only = self.only
        data_name = self.data_name

        def f():
            result = clarite.modify.colfilter_percent_zero(data, filter_percent, skip, only)
            if data_name is None:
                return result
            else:
                return Dataset(data_name, 'dataset', result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_python_name()  # New selected data
        self.appctx.log_python(f"{new_data_name} = clarite.modify.colfilter_percent_zero("
                               f"data={old_data_name}, "
                               f"filter_percent={self.filter_percent}, "
                               f"skip={self.skip}, "
                               f"only={self.only})")

    def setup_ui(self):
        self.setWindowTitle(f"Colfilter: Percent Zero")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout(self)
        
        # Skip/Only
        self.skiponly_label = QLabel(self)
        self.skiponly_label.setText(f"Using all {len(list(self.dataset.df)):,} variables")
        self.btn_skiponly = QPushButton("Edit", parent=self)
        self.btn_skiponly.clicked.connect(self.launch_skiponly)
        layout.addRow(self.skiponly_label, self.btn_skiponly)

        # Filter Percent
        label = QLabel(self)
        label.setText("Percent of Rows equal to 0")
        sb = QDoubleSpinBox(self)
        sb.setDecimals(1)
        sb.setRange(0.0, 100.0)
        sb.setValue(self.filter_percent)
        sb.valueChanged.connect(self.update_filter_percent)
        layout.addRow(label, sb)

        # Data Name       
        self.le_data_name = QLineEdit(self.data_name)
        self.le_data_name.setPlaceholderText(self.appctx.datasets[self.appctx.current_dataset_idx].name)
        self.le_data_name.textChanged.connect(self.update_data_name)
        layout.addRow("Save Dataset Name: ", self.le_data_name)

        # Ok/Cancel       
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    # Slots
    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    @pyqtSlot(float)
    def update_filter_percent(self, value):
        self.filter_percent = value

    def launch_skiponly(self):
        """Launch a dialog to set skip/only"""
        # Update skip and only
        text, self.skip, self.only = SkipOnlyDialog.get_skip_only(columns=list(self.dataset.df),
                                                                  skip=self.skip, only=self.only,
                                                                  parent=self)
        self.skiponly_label.setText(text)

    def submit(self):
        if self.data_name is not None and self.data_name in [d.name for d in self.appctx.datasets]:
            warnings.show_warning("Dataset already exists",
                                  f"A dataset named '{self.data_name}' already exists.\n"
                                  f"Use a different name or clear the dataset name field.")
        else:
            # Run with a progress dialog
            if self.data_name is None:
                slot = self.appctx.update_data
            else:
                slot = self.appctx.add_dataset
            RunProgress.run_with_progress(progress_str="Filtering variables...",
                                          function=self.get_func(),
                                          slot=slot,
                                          parent=self)
            self.log_command()
            self.accept()
