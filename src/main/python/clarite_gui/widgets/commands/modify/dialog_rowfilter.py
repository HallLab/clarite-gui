import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QLineEdit, QGroupBox, \
    QHBoxLayout, QRadioButton, QComboBox, QWidget

from models import Dataset
from widgets.utilities import warnings, RunProgress


class RowfilterDialog(QDialog):
    """
    This dialog sets settings for recoding values
    """
    def __init__(self, *args, **kwargs):
        super(RowfilterDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        # Stored data to choose from
        self.columns = list(self.dataset.df)
        self.comparison_method_options = ["less than", "less than or equal to",
                                          "equal to", "not equal to",
                                          "greater than or equal to", "greater than"]
        # Actual selected values
        self.comparison_column = self.columns[0]
        self.comparison_method = self.comparison_method_options[0]
        self.comparison_value = None
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.appctx.datasets[self.appctx.current_dataset_idx].df
        column = self.comparison_column
        value = self.comparison_value
        method = self.comparison_method
        data_name = self.data_name

        # Build the function
        def f():
            if method == 'less than':
                result = data.loc[data[column] < value, ]
            elif method == 'less than or equal to':
                result = data.loc[data[column] <= value, ]
            elif method == 'equal to':
                result = data.loc[data[column] == value, ]
            elif method == 'not equal to':
                result = data.loc[data[column] != value, ]
            elif method == 'greater than or equal to':
                result = data.loc[data[column] >= value, ]
            elif method == 'greater than':
                result = data.loc[data[column] > value, ]

            print("=" * 80)
            print(f"Running Rowfilter: Keep rows where {repr(column)} is {method} {repr(value)}")
            print("-" * 80)
            print(f"Kept {len(result):,} of {len(data):,} rows ({len(result)/len(data):.2%})")
            print("=" * 80)

            if data_name is None:
                return result
            else:
                return Dataset(data_name, 'dataset', result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_python_name()  # New selected data

        # Get symbol
        if self.comparison_method == 'less than':
            symbol = "<"
        elif self.comparison_method == 'less than or equal to':
            symbol = "<="
        elif self.comparison_method == 'equal to':
            symbol = "=="
        elif self.comparison_method == 'not equal to':
            symbol = "!="
        elif self.comparison_method == 'greater than or equal to':
            symbol = ">="
        elif self.comparison_method == 'greater than':
            symbol = ">"

        self.appctx.log_python(f"{new_data_name} = {old_data_name}"
                               f".loc[{old_data_name}[{repr(self.comparison_column)}] {symbol} "
                               f"{repr(self.comparison_value)}, ]")

    def setup_ui(self):
        self.setWindowTitle(f"Rowfilter")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout(self)
        
        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        self.le_data_name.setPlaceholderText(self.appctx.datasets[self.appctx.current_dataset_idx].name)
        self.le_data_name.textChanged.connect(self.update_data_name)
        layout.addRow("Save Dataset Name: ", self.le_data_name)

        # Comparison Row
        comparison_widget = QWidget(parent=self)
        comparison_layout = QHBoxLayout()
        # Label
        comparison_layout.addWidget(QLabel(f"Keep Rows where"))
        # Column
        self.column_cb = QComboBox(parent=self)
        for col in self.columns:
            self.column_cb.addItem(col)
        self.column_cb.currentIndexChanged.connect(self.update_column)
        comparison_layout.addWidget(self.column_cb)
        # Label
        comparison_layout.addWidget(QLabel("is"))
        # Method
        self.comparison_method = QComboBox(parent=self)
        for comp_method in self.comparison_method_options:
            self.comparison_method.addItem(comp_method)
        self.comparison_method.currentIndexChanged.connect(self.update_method)
        comparison_layout.addWidget(self.comparison_method)
        # Value - assume numeric by default
        self.comparison_le = QLineEdit(parent=self)
        self.comparison_le.setPlaceholderText("value")
        self.comparison_le.textChanged.connect(self.update_value)
        self.comparison_le.setValidator(QDoubleValidator())
        comparison_layout.addWidget(self.comparison_le)
        comparison_widget.setLayout(comparison_layout)
        layout.addRow(comparison_widget)

        # Value Type - numeric or string
        self.comparison_type_gb = QGroupBox()
        self.comparison_type_layout = QHBoxLayout()

        self.comparison_type_int = QRadioButton("Integer", parent=self)
        self.comparison_type_int.clicked.connect(lambda: self.update_input_type(self.comparison_le, 'int'))
        self.comparison_type_layout.addWidget(self.comparison_type_int)
        self.comparison_type_int.setChecked(True)

        self.comparison_type_float = QRadioButton("Float", parent=self)
        self.comparison_type_float.clicked.connect(lambda: self.update_input_type(self.comparison_le, 'float'))
        self.comparison_type_layout.addWidget(self.comparison_type_float)

        self.comparison_type_string = QRadioButton("String", parent=self)
        self.comparison_type_string.clicked.connect(lambda: self.update_input_type(self.comparison_le, 'str'))
        self.comparison_type_layout.addWidget(self.comparison_type_string)

        self.comparison_type_none = QRadioButton("None", parent=self)
        self.comparison_type_none.clicked.connect(lambda: self.update_input_type(self.comparison_le, 'none'))
        self.comparison_type_layout.addWidget(self.comparison_type_none)

        self.comparison_type_gb.setLayout(self.comparison_type_layout)
        layout.addRow("Compare value as: ", self.comparison_type_gb)

        # Ok/Cancel       
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    # Slots
    @staticmethod
    def update_input_type(input, type):
        """Update the value input depending on the selected type"""
        # Enable/Disable based on "None" being selected
        if type in ('int', 'float', 'str'):
            input.setEnabled(True)
        else:
            input.setEnabled(False)

        # Reset Text
        input.clear()

        # Validators
        if type == 'int':
            input.setValidator(QIntValidator())
        elif type == 'float':
            input.setValidator(QDoubleValidator())
        else:
            input.setValidator(None)  # No validation

    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    @pyqtSlot(int)
    def update_column(self, value):
        self.comparison_column = self.columns[value]

    @pyqtSlot(int)
    def update_method(self, value):
        self.comparison_method = self.comparison_method_options[value]

    @pyqtSlot(str)
    def update_value(self, value):
        self.comparison_value = value

    def update_types(self):
        """
        Try to convert types, returning None on success and an error message on failure
        """
        # Update from type
        try:
            if self.comparison_type_int.isChecked():
                self.comparison_value = int(self.comparison_value)
            elif self.comparison_type_float.isChecked():
                self.comparison_value = float(self.comparison_value)
            elif self.comparison_type_string.isChecked():
                self.comparison_value = str(self.comparison_value)
            elif self.comparison_type_none.isChecked():
                self.comparison_value = np.nan
        except ValueError:
            return f"Couldn't convert the comparison value to the selected type"

        return None

    def submit(self):
        type_errors = self.update_types()  # Convert the types of 'from' and 'to', returning None if successful
        if self.data_name is not None and self.data_name in [d.name for d in self.appctx.datasets]:
            warnings.show_warning("Dataset already exists",
                                  f"A dataset named '{self.data_name}' already exists.\n"
                                  f"Use a different name or clear the dataset name field.")
        elif type_errors is not None:
            warnings.show_critical("Error", type_errors)
        else:
            # Run with a progress dialog
            if self.data_name is None:
                slot = self.appctx.update_data
            else:
                slot = self.appctx.add_dataset
            RunProgress.run_with_progress(progress_str="Filtering Rows...",
                                          function=self.get_func(),
                                          slot=slot,
                                          parent=self)
            self.log_command()
            self.accept()
