import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit, QComboBox

from models import Dataset
from widgets.utilities import warnings, RunProgress


class MergeVarsDialog(QDialog):
    """
    This dialog sets settings for merging variables.
    Showing the dialog isn't possible unless there are at least two datasets loaded.
    """
    def __init__(self, *args, **kwargs):
        super(MergeVarsDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.left_idx = None
        self.left_name = None
        self.right_idx = None
        self.right_name = None
        self.how_options = ['left', 'right', 'inner', 'outer']
        self.how = "outer"
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        left = self.appctx.datasets[self.left_idx].df
        right = self.appctx.datasets[self.right_idx].df
        how = self.how
        data_name = self.data_name

        def f():
            result = clarite.modify.merge_variables(left, right, how)
            return Dataset(data_name, 'dataset', result)

        return f

    def log_command(self):
        left_data_name = self.appctx.datasets[self.left_idx].get_python_name()
        right_data_name = self.appctx.datasets[self.right_idx].get_python_name()
        new_data_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_python_name()  # New selected data
        self.appctx.log_python(f"{new_data_name} = clarite.modify.merge_variables("
                               f"left={left_data_name}, "
                               f"right={right_data_name}), "
                               f"how={repr(self.how)})")

    def setup_ui(self):
        self.setWindowTitle(f"Merge Variables")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout(self)
        
        # Left
        self.left_select = QComboBox(self)
        self.left_select.currentIndexChanged.connect(self.update_left)
        layout.addRow("'Left' Dataset: ", self.left_select)

        # Bottom
        self.right_select = QComboBox(self)
        self.right_select.currentIndexChanged.connect(self.update_right)
        layout.addRow("'Right' Dataset: ", self.right_select)

        # How
        self.how_select = QComboBox(self)
        for option in self.how_options:
            self.how_select.addItem(option)
        self.how_select.currentIndexChanged.connect(self.update_how)
        self.how_select.setCurrentIndex(3)  # 'outer' by default
        layout.addRow("How: ", self.how_select)

        # Data Name       
        self.le_data_name = QLineEdit(self.data_name)
        self.le_data_name.setPlaceholderText(f"{self.left_name}_{self.right_name}")
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
            self.left_select.addItem(dataset.name)
            self.right_select.addItem(dataset.name)
        # Set top to the latest one, and bottom to the one before
        self.left_select.setCurrentIndex(len(self.appctx.datasets) - 1)
        self.right_select.setCurrentIndex(len(self.appctx.datasets) - 2)

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
    def update_left(self, idx):
        self.left_idx = idx
        self.left_name = self.appctx.datasets[idx].name
        if self.data_name is None:
            self.le_data_name.setPlaceholderText(f"{self.left_name}_{self.right_name}")

    @pyqtSlot(int)
    def update_right(self, idx):
        self.right_idx = idx
        self.right_name = self.appctx.datasets[idx].name
        if self.data_name is None:
            self.le_data_name.setPlaceholderText(f"{self.left_name}_{self.right_name}")

    @pyqtSlot(int)
    def update_how(self, idx):
        self.how = self.how_options[idx]

    def submit(self):
        if self.data_name is None:
            self.data_name = self.le_data_name.placeholderText()

        if self.data_name is not None and self.data_name in [d.name for d in self.appctx.datasets]:
            warnings.show_warning("Dataset already exists",
                                  f"A dataset named '{self.data_name}' already exists.\n"
                                  f"Use a different name.")
        elif self.left_idx is None or self.right_idx is None or self.left_idx == self.right_idx:
            warnings.show_warning("Select Two Datasets", "Two different datasets must be selected.")
        else:
            RunProgress.run_with_progress(progress_str="Merging Data...",
                                          function=self.get_func(),
                                          slot=self.appctx.add_dataset,
                                          parent=self)
            self.log_command()
            self.accept()
