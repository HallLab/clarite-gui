import clarite
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QPushButton

from gui.widgets import SkipOnlyDialog
from gui.widgets.utilities import RunProgress


class DropExtraCatDialog(QDialog):
    """
    This dialog sets settings for the make_<type> functions
    """

    def __init__(self, *args, **kwargs):
        super(DropExtraCatDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.skip = None
        self.only = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        skip = self.skip
        only = self.only

        def f():
            result = clarite.modify.drop_extra_categories(data, skip, only)
            return result

        return f

    def log_command(self):
        dataset_name = self.dataset.get_python_name()  # Original selected data
        self.appctx.log_python(
            f"{dataset_name} = clarite.modify.drop_extra_categories("
            f"data={dataset_name}, "
            f"skip={self.skip}, "
            f"only={self.only})"
        )

    def setup_ui(self):
        self.setWindowTitle(f"Drop Extra Categories")
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

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    # Slots
    def launch_skiponly(self):
        """Launch a dialog to set skip/only"""
        # Update skip and only
        text, self.skip, self.only = SkipOnlyDialog.get_skip_only(
            columns=list(self.dataset.df), skip=self.skip, only=self.only, parent=self
        )
        self.skiponly_label.setText(text)

    def submit(self):
        # Run with a progress dialog
        RunProgress.run_with_progress(
            progress_str="Dropping extra categories...",
            function=self.get_func(),
            slot=self.appctx.update_data,
            parent=self,
        )
        self.log_command()
        self.accept()
