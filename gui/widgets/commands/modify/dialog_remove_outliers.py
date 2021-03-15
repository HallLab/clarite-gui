import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QFormLayout,
    QDialogButtonBox,
    QPushButton,
    QLineEdit,
    QComboBox,
)

from gui.models import Dataset
from gui.widgets import SkipOnlyDialog
from gui.widgets.utilities import warnings, RunProgress


class RemoveOutliersDialog(QDialog):
    """
    This dialog sets settings for recoding values
    """

    def __init__(self, *args, **kwargs):
        super(RemoveOutliersDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.method_options_display = [
            "Gaussian",
            "Interquartile Range (IQR)",
        ]  # Options as displayed
        self.method_options_use = [
            "gaussian",
            "iqr",
        ]  # Options as input into the function
        self.method = "gaussian"
        self.cutoff = 3.0
        self.skip = None
        self.only = None
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        method = self.method
        cutoff = self.cutoff
        skip = self.skip
        only = self.only
        data_name = self.data_name

        # Build the function
        def f():
            result = clarite.modify.remove_outliers(
                data=data, method=method, cutoff=cutoff, skip=skip, only=only
            )
            if data_name is None:
                return result
            else:
                return Dataset(data_name, "dataset", result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[
            self.appctx.current_dataset_idx
        ].get_python_name()  # New selected data
        self.appctx.log_python(
            f"{new_data_name} = clarite.modify.remove_outliers("
            f"data={old_data_name}, "
            f"method={repr(self.method)}, "
            f"cutoff={repr(self.cutoff)}, "
            f"skip={self.skip}, "
            f"only={self.only})"
        )

    def setup_ui(self):
        self.setWindowTitle(f"Remove Outliers")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout(self)

        # Skip/Only
        self.skiponly_label = QLabel(self)
        self.skiponly_label.setText(
            f"Using all {len(list(self.dataset.df)):,} variables"
        )
        self.btn_skiponly = QPushButton("Edit", parent=self)
        self.btn_skiponly.clicked.connect(self.launch_skiponly)
        layout.addRow(self.skiponly_label, self.btn_skiponly)

        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        self.le_data_name.setPlaceholderText(
            self.appctx.datasets[self.appctx.current_dataset_idx].name
        )
        self.le_data_name.textChanged.connect(self.update_data_name)
        layout.addRow("Save Dataset Name: ", self.le_data_name)

        # Method used to remove outliers
        self.method_cb = QComboBox(parent=self)
        for method in self.method_options_display:
            self.method_cb.addItem(method)
        self.method_cb.currentIndexChanged.connect(self.update_method)
        layout.addRow("Outlier Method: ", self.method_cb)

        # Cutoff
        self.cutoff_input = QLineEdit(parent=self)
        self.cutoff_input.setText(f"{self.cutoff}")
        self.cutoff_input.setValidator(QDoubleValidator(bottom=0))
        self.cutoff_input.textChanged.connect(self.update_cutoff)
        layout.addRow("Cutoff Value: ", self.cutoff_input)

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    # Slots
    @pyqtSlot(int)
    def update_method(self, method_idx):
        """Update the selected method"""
        self.method = self.method_options_use[method_idx]

    @pyqtSlot(str)
    def update_cutoff(self, cutoff_value):
        """Update the cutoff value being used"""
        self.cutoff = float(cutoff_value)

    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    def launch_skiponly(self):
        """Launch a dialog to set skip/only"""
        # Update skip and only
        text, self.skip, self.only = SkipOnlyDialog.get_skip_only(
            columns=list(self.dataset.df), skip=self.skip, only=self.only, parent=self
        )
        self.skiponly_label.setText(text)

    def submit(self):
        if self.data_name is not None and self.data_name in [
            d.name for d in self.appctx.datasets
        ]:
            warnings.show_warning(
                "Dataset already exists",
                f"A dataset named '{self.data_name}' already exists.\n"
                f"Use a different name or clear the dataset name field.",
            )
        else:
            # Run with a progress dialog
            if self.data_name is None:
                slot = self.appctx.update_data
            else:
                slot = self.appctx.add_dataset
            RunProgress.run_with_progress(
                progress_str="Removing outliers...",
                function=self.get_func(),
                slot=slot,
                parent=self,
            )
            self.log_command()
            self.accept()
