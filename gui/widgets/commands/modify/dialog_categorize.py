import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QSpinBox

from gui.widgets.utilities import warnings, RunProgress


class CategorizeDialog(QDialog):
    """
    This dialog allows sets settings for categorization
    """

    def __init__(self, *args, **kwargs):
        super(CategorizeDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        # Data
        self.cat_min = 3
        self.cat_max = 6
        self.cont_min = 15
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        dataset = self.dataset
        cat_min = self.cat_min
        cat_max = self.cat_max
        cont_min = self.cont_min

        def f():
            return clarite.modify.categorize(dataset.df, cat_min, cat_max, cont_min)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()
        new_data_name = self.appctx.datasets[
            self.appctx.current_dataset_idx
        ].get_python_name()
        self.appctx.log_python(
            f"{new_data_name} = clarite.modify.categorize("
            f"data={old_data_name}, "
            f"cat_min={self.cat_min}, "
            f"cat_max={self.cat_max}, "
            f"cont_min={self.cont_min})"
        )

    def setup_ui(self):
        self.setWindowTitle(f"Categorize Data")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout()
        layout.addRow(QLabel("Number of unique values:"))

        # Min cat (default = 3)
        self.setting_cat_min = QSpinBox(self)
        self.setting_cat_min.setValue(3)
        self.setting_cat_min.setMinimum(3)
        layout.addRow("Categorical Minimum", self.setting_cat_min)
        self.setting_cat_min.valueChanged.connect(self.change_cat_min)

        # Max cat (default = 6)
        self.setting_cat_max = QSpinBox(self)
        self.setting_cat_max.setValue(6)
        self.setting_cat_max.setMinimum(3)
        layout.addRow("Categorical Maximum", self.setting_cat_max)
        self.setting_cat_max.valueChanged.connect(self.change_cat_max)

        # Min cont (default = 15)
        self.setting_cont_min = QSpinBox(self)
        self.setting_cont_min.setValue(15)
        self.setting_cont_min.setMinimum(3)
        layout.addRow("Continuous Minimum", self.setting_cont_min)
        self.setting_cont_min.valueChanged.connect(self.change_cont_min)

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    @pyqtSlot(int)
    def change_cat_min(self, n):
        self.cat_min = n

    @pyqtSlot(int)
    def change_cat_max(self, n):
        self.cat_max = n

    @pyqtSlot(int)
    def change_cont_min(self, n):
        self.cont_min = n

    def submit(self):
        print(f"categorize with {self.cat_min}, {self.cat_max}, {self.cont_min}")
        if self.cat_min > self.cat_max:
            warnings.show_warning(
                "Parameter Error",
                f"'Categorical Minimum' must be <= 'Categorical Maximum'",
            )
        elif self.cat_min > self.cont_min:
            warnings.show_warning(
                "Parameter Error",
                f"'Categorical Minimum' must be < 'Continuous Minimum'",
            )
        elif self.cat_max >= self.cont_min:
            warnings.show_warning(
                "Parameter Error",
                f"'Categorical Maximum' must be < 'Continuous Minimum'",
            )
        else:
            # Run with a progress dialog
            RunProgress.run_with_progress(
                progress_str="Categorizing variables...",
                function=self.get_func(),
                slot=self.appctx.update_data,
                parent=self,
            )
            self.log_command()
            self.accept()
