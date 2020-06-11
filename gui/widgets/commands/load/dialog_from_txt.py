from pathlib import Path

import clarite
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QFormLayout, QPushButton, QLineEdit

from gui.models import Dataset
from gui.widgets.utilities import warnings, RunProgress


class FromTxtDialog(QDialog):
    """
    This dialog allows loading files from a text format, including specifying a dataset name and the index column.
    Currently supported types (each maps to a different CLARITE load.from_ function):
       - tsv (tab-separated)
       - csv (comma-separated)
    """
    def __init__(self, kind, *args, **kwargs):
        super(FromTxtDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Kind of file being loaded
        if kind not in {'CSV', 'TSV'}:
            raise ValueError(f"{kind} isn't a supported file loader")
        else:
            self.kind = kind
        # Data
        self.filename = None
        self.data_name = None
        self.index_col = 0  # First column by default
        self.df = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        filename = self.filename
        data_name = self.data_name
        index_col = self.index_col
        kind = self.kind

        # Get Function
        def f():
            if kind == 'CSV':
                df = clarite.load.from_csv(filename, index_col)
            elif kind == 'TSV':
                df = clarite.load.from_tsv(filename, index_col)
            return Dataset(data_name, 'dataset', df)

        return f

    def log_command(self):
        # Log the addition of the dataset (The new dataset is the current one)
        dataset_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_python_name()
        # Get index col, wrapping strings in quotes
        index_col = repr(self.index_col)
        # Log the command
        if self.kind == "CSV":
            self.appctx.log_python(
                f"{dataset_name} = clarite.load.from_csv(filename='{self.filename}', index_col={index_col})")
        elif self.kind == 'TSV':
            self.appctx.log_python(
                f"{dataset_name} = clarite.load.from_tsv(filename='{self.filename}', index_col={index_col})")

    def setup_ui(self):
        self.setWindowTitle(f"Load - From {self.kind}")
        self.setMinimumWidth(500)
        self.setModal(True)

        self.layout = QFormLayout(self)

        # Load Button
        self.btn_select_file = QPushButton(text="Select File", parent=self)
        self.btn_select_file.clicked.connect(self.launch_dlg_get_file)
        self.layout.addWidget(self.btn_select_file)

        # Filename        
        self.le_selected_file = QLineEdit(self.filename)
        self.le_selected_file.setPlaceholderText(f"{self.kind} File")
        self.le_selected_file.textChanged.connect(self.update_filename)

        self.layout.addRow("Filename: ", self.le_selected_file)

        # Data Name       
        self.le_data_name = QLineEdit(self.data_name)
        self.le_data_name.setPlaceholderText("")
        self.le_data_name.textChanged.connect(self.update_data_name)
        self.layout.addRow("Dataset Name: ", self.le_data_name)

        # Index Column       
        self.le_index_col = QLineEdit(self.filename)
        self.le_index_col.setPlaceholderText("None (Use first column)")
        self.le_index_col.textChanged.connect(self.update_index_col)
        self.layout.addRow("Index Column Name: ", self.le_index_col)

        # Ok/Cancel       
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addRow(self.buttonBox)

        # Set size
        self.setMinimumWidth(400)

    def submit(self):
        if len(self.filename) == 0:
            self.reject()
            return
        datafile = Path(self.filename)
        if not datafile.exists():
            warnings.show_warning(title="File Not Found",
                                  text=f"The file could not be found:\n'{str(datafile)}''")
        elif not datafile.is_file():
            warnings.show_warning(title="Not a File",
                                  text=f"A folder was given instead of a file:\n'{str(datafile)}''")
        elif self.data_name in [d.name for d in self.appctx.datasets]:
            warnings.show_warning(title="Dataset already exists",
                                  text=f"A dataset named '{self.data_name}' already exists.  Use a different name.")
        else:
            RunProgress.run_with_progress(progress_str=f"Loading {self.kind} file...",
                                          function=self.get_func(),
                                          slot=self.appctx.add_dataset,
                                          parent=self)
            self.log_command()
            self.accept()

    #########
    # Slots #
    #########
    def update_filename(self):
        text = self.le_selected_file.text()
        if len(text.strip()) == 0:
            self.filename = None
        else:
            self.filename = text
        # Update data_name automatically if it doesn't have one
        if self.data_name is None:
            self.data_name = Path(self.filename).stem
            self.le_data_name.setText(self.data_name)

    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    def update_index_col(self):
        text = self.le_index_col.text()
        if len(text.strip()) > 0:
            self.index_col = text

    ###############
    # Sub-dialogs #
    ###############
    def launch_dlg_get_file(self):
        """Launch a dialog to select the file"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  f"Load - From {self.kind} File",
                                                  "",
                                                  f"{self.kind} Files (*.{self.kind.lower()} *.txt)",
                                                  options=options)
        # Set filename
        self.le_selected_file.setText(filename)
        return
