import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit, QComboBox

from gui.models import Dataset
from gui.widgets.utilities import warnings, RunProgress


class MergeObsDialog(QDialog):
    """
    This dialog sets settings for merging observations.
    Showing the dialog isn't possible unless there are at least two datasets loaded.
    """

    def __init__(self, *args, **kwargs):
        super(MergeObsDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.top_idx = None
        self.top_name = None
        self.bottom_idx = None
        self.bottom_name = None
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        top = self.appctx.datasets[self.top_idx].df
        bottom = self.appctx.datasets[self.bottom_idx].df
        data_name = self.data_name

        def f():
            result = clarite.modify.merge_observations(top, bottom)
            return Dataset(data_name, "dataset", result)

        return f

    def log_command(self):
        top_data_name = self.appctx.datasets[self.top_idx].get_python_name()
        bottom_data_name = self.appctx.datasets[self.bottom_idx].get_python_name()
        new_data_name = self.appctx.datasets[
            self.appctx.current_dataset_idx
        ].get_python_name()  # New selected data
        self.appctx.log_python(
            f"{new_data_name} = clarite.modify.merge_observations("
            f"top={top_data_name}, "
            f"bottom={bottom_data_name})"
        )

    def setup_ui(self):
        self.setWindowTitle(f"Merge Observations")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout(self)

        # Top
        self.top_select = QComboBox(self)
        self.top_select.currentIndexChanged.connect(self.update_top)
        layout.addRow("'Top' Dataset: ", self.top_select)

        # Bottom
        self.bottom_select = QComboBox(self)
        self.bottom_select.currentIndexChanged.connect(self.update_bottom)
        layout.addRow("'Bottom' Dataset: ", self.bottom_select)

        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        self.le_data_name.setPlaceholderText(f"{self.top_name}_{self.bottom_name}")
        self.le_data_name.textChanged.connect(self.update_data_name)
        layout.addRow("Save Dataset Name: ", self.le_data_name)

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Add datasets
        for dataset in self.appctx.datasets:
            self.top_select.addItem(dataset.name)
            self.bottom_select.addItem(dataset.name)
        # Set top to the latest one, and bottom to the one before
        self.top_select.setCurrentIndex(len(self.appctx.datasets) - 1)
        self.bottom_select.setCurrentIndex(len(self.appctx.datasets) - 2)

        # Set Layout
        self.setLayout(layout)

    # Slots
    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    @pyqtSlot(int)
    def update_top(self, idx):
        self.top_idx = idx
        self.top_name = self.appctx.datasets[idx].name
        if self.data_name is None:
            self.le_data_name.setPlaceholderText(f"{self.top_name}_{self.bottom_name}")

    @pyqtSlot(int)
    def update_bottom(self, idx):
        self.bottom_idx = idx
        self.bottom_name = self.appctx.datasets[idx].name
        if self.data_name is None:
            self.le_data_name.setPlaceholderText(f"{self.top_name}_{self.bottom_name}")

    def submit(self):
        if self.data_name is None:
            self.data_name = self.le_data_name.placeholderText()

        if self.data_name is not None and self.data_name in [
            d.name for d in self.appctx.datasets
        ]:
            warnings.show_warning(
                "Dataset already exists",
                f"A dataset named '{self.data_name}' already exists.\n"
                f"Use a different name.",
            )
        elif (
            self.top_idx is None
            or self.bottom_idx is None
            or self.top_idx == self.bottom_idx
        ):
            warnings.show_warning(
                "Select Two Datasets", "Two different datasets must be selected."
            )
        else:
            RunProgress.run_with_progress(
                progress_str="Merging Data...",
                function=self.get_func(),
                slot=self.appctx.add_dataset,
                parent=self,
            )
            self.log_command()
            self.accept()
