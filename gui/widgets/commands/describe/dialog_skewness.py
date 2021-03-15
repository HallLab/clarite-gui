import clarite
from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit, QCheckBox

from gui.models import Dataset
from gui.widgets.utilities import RunProgress, show_warning


class SkewnessDialog(QDialog):
    """
    This dialog allows sets settings for getting percent NA values
    """

    def __init__(self, *args, **kwargs):
        super(SkewnessDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.data_name = None
        self.dropna = True
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        if self.data_name is None:
            data_name = f"Skewness for {self.appctx.datasets[self.appctx.current_dataset_idx].name}"
        else:
            data_name = self.data_name
        dropna = self.dropna

        def f():
            result = clarite.describe.skewness(data, dropna)
            return Dataset(data_name, "skewness", result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[
            self.appctx.current_dataset_idx
        ].get_python_name()  # New selected data
        self.appctx.log_python(
            f"{new_data_name} = clarite.describe.skewness(data={old_data_name}, "
            f"dropna={repr(self.dropna)})"
        )

    def setup_ui(self):
        self.setWindowTitle(f"Skewness")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout()

        # DropNA Checkbox
        self.dropna_cb = QCheckBox(self)
        self.dropna_cb.setChecked(self.dropna)
        self.dropna_cb.stateChanged.connect(self.update_dropna)
        layout.addRow("Drop NA values before calculating skewness", self.dropna_cb)

        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        input_name = self.appctx.datasets[self.appctx.current_dataset_idx].name
        self.le_data_name.setPlaceholderText(f"Skewness for {input_name}")
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

    def update_dropna(self):
        self.dropna = self.dropna_cb.isChecked()

    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    def submit(self):
        if self.data_name is not None and self.data_name in [
            d.name for d in self.appctx.datasets
        ]:
            show_warning(
                "Dataset already exists",
                f"A dataset named '{self.data_name}' already exists.\n"
                f"Use a different name or clear the dataset name field.",
            )
        else:
            print(f"Calculating Skewness")
            # Run with a progress dialog
            RunProgress.run_with_progress(
                progress_str="Calculating Skewness...",
                function=self.get_func(),
                slot=self.appctx.add_dataset,
                parent=self,
            )
            self.log_command()
            self.accept()
