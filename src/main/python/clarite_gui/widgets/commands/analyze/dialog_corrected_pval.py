import clarite
from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit

from models import Dataset
from widgets.utilities import RunProgress, show_warning


class CorrectedPvalDialog(QDialog):
    """
    This dialog allows sets settings for EWAS
    """

    def __init__(self, *args, **kwargs):
        super(CorrectedPvalDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        # Saved results name
        data_name = self.data_name

        # EWAS parameters
        data = self.dataset.df

        # Survey Parameters
        def f():
            result = data.copy(deep=True)  # This function works in-place, so a copy must be created first
            clarite.analyze.add_corrected_pvalues(result)
            if data_name is None:
                return result
            else:
                return Dataset(data_name, 'ewas_result', result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_python_name()  # New selected data
        self.appctx.log_python(f"{new_data_name} = clarite.describe.correlations(data={old_data_name}, "
                               f"threshold={repr(self.threshold)})")

    def setup_ui(self):
        self.setWindowTitle(f"Add Corrected P-values")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout()
        self.setLayout(layout)

        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        input_name = self.appctx.datasets[self.appctx.current_dataset_idx].name
        self.le_data_name.setPlaceholderText(input_name)
        self.le_data_name.textChanged.connect(self.update_data_name)
        layout.addRow("Save Dataset Name: ", self.le_data_name)

        # Ok/Cancel       
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    def submit(self):
        if self.data_name is not None and self.data_name in [d.name for d in self.appctx.datasets]:
            show_warning("Dataset already exists",
                         f"A dataset named '{self.data_name}' already exists.\n"
                         f"Use a different name or clear the dataset name field.")
        elif 'converged' not in list(self.dataset.df):
            show_warning("Incorrect Data Input",
                         "A 'converged' column must be present")
        elif 'pvalue' not in list(self.dataset.df):
            show_warning("Incorrect Data Input",
                         "A 'pvalue' column must be present")
        else:
            print(f"Adding corrected P-values...")
            # Run with a progress dialog
            if self.data_name is None:
                slot = self.appctx.update_data
            else:
                slot = self.appctx.add_dataset
            RunProgress.run_with_progress(progress_str="Adding corrected P-values...",
                                          function=self.get_func(),
                                          slot=slot,
                                          parent=self)
            self.log_command()
            self.accept()
