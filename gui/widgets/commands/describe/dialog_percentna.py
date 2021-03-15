import clarite
from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit

from gui.models import Dataset
from gui.widgets.utilities import RunProgress, show_warning


class PercentNADialog(QDialog):
    """
    This dialog allows sets settings for getting percent NA values
    """

    def __init__(self, *args, **kwargs):
        super(PercentNADialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        if self.data_name is None:
            data_name = f"Percent NA for {self.appctx.datasets[self.appctx.current_dataset_idx].name}"
        else:
            data_name = self.data_name

        def f():
            result = clarite.describe.percent_na(data)
            return Dataset(data_name, "percentna", result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[
            self.appctx.current_dataset_idx
        ].get_python_name()  # New selected data
        self.appctx.log_python(
            f"{new_data_name} = clarite.describe.percent_na(data={old_data_name})"
        )

    def setup_ui(self):
        self.setWindowTitle(f"Percent NA")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout()

        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        input_name = self.appctx.datasets[self.appctx.current_dataset_idx].name
        self.le_data_name.setPlaceholderText(f"Percent NA for {input_name}")
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
            print(f"Calculating Percent NA")
            # Run with a progress dialog
            RunProgress.run_with_progress(
                progress_str="Calculating Percent NA...",
                function=self.get_func(),
                slot=self.appctx.add_dataset,
                parent=self,
            )
            self.log_command()
            self.accept()
