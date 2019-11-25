import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QLineEdit, QDoubleSpinBox

from models import Dataset
from widgets.utilities import RunProgress, show_warning


class CorrelationDialog(QDialog):
    """
    This dialog allows sets settings for calculating correlations
    """
    def __init__(self, *args, **kwargs):
        super(CorrelationDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.threshold = 0.75
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        threshold = self.threshold
        if self.data_name is None:
            data_name = f"Correlations for {self.appctx.datasets[self.appctx.current_dataset_idx].name}"
        else:
            data_name = self.data_name

        def f():
            result = clarite.describe.correlations(data, threshold)
            return Dataset(data_name, 'correlations', result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_python_name()  # New selected data
        self.appctx.log_python(f"{new_data_name} = clarite.describe.correlations(data={old_data_name}, "
                               f"threshold={repr(self.threshold)})")

    def setup_ui(self):
        self.setWindowTitle(f"Correlations")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout()

        # Minimum Correlation
        label = QLabel(self)
        label.setText("Minimum correlation value to report")
        sb = QDoubleSpinBox(self)
        sb.setDecimals(2)
        sb.setRange(0, 1)
        sb.setValue(self.threshold)
        sb.valueChanged.connect(self.update_threshold)
        layout.addRow(label, sb)

        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        input_name = self.appctx.datasets[self.appctx.current_dataset_idx].name
        self.le_data_name.setPlaceholderText(f"Correlations for {input_name}")
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

    def update_threshold(self, threshold):
        self.threshold = float(threshold)

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
        else:
            print(f"Reporting correlations >= {self.threshold:.2f}")
            # Run with a progress dialog
            RunProgress.run_with_progress(progress_str="Calculating correlations...",
                                          function=self.get_func(),
                                          slot=self.appctx.add_dataset,
                                          parent=self)
            self.log_command()
            self.accept()
