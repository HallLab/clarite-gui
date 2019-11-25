import clarite
import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QPushButton, QLineEdit, QGroupBox, \
    QHBoxLayout, QVBoxLayout, QRadioButton

from models import Dataset
from widgets import SkipOnlyDialog
from widgets.utilities import warnings, RunProgress


class RecodeValuesDialog(QDialog):
    """
    This dialog sets settings for recoding values
    """
    def __init__(self, *args, **kwargs):
        super(RecodeValuesDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.from_value = None
        self.to_value = None
        self.skip = None
        self.only = None
        self.data_name = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        replacement_dict = {self.from_value: self.to_value}
        skip = self.skip
        only = self.only
        data_name = self.data_name

        # Build the function
        def f():
            result = clarite.modify.recode_values(data=data, replacement_dict=replacement_dict,
                                                  skip=skip, only=only)
            if data_name is None:
                return result
            else:
                return Dataset(data_name, 'dataset', result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_python_name()  # New selected data
        # Write 'None' instead of 'np.nan'
        if np.isnan(self.from_value):
            from_value = None
        else:
            from_value = self.from_value
        if np.isnan(self.to_value):
            to_value = None
        else:
            to_value = self.to_value
        # Log
        self.appctx.log_python(f"{new_data_name} = clarite.modify.recode_values("
                               f"data={old_data_name}, "
                               f"replacement_dict={repr({from_value: to_value})}, "
                               f"skip={self.skip}, "
                               f"only={self.only})")

    def setup_ui(self):
        self.setWindowTitle(f"Recode Values")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout(self)
        
        # Skip/Only
        self.skiponly_label = QLabel(self)
        self.skiponly_label.setText(f"Using all {len(list(self.dataset.df)):,} variables")
        self.btn_skiponly = QPushButton("Edit", parent=self)
        self.btn_skiponly.clicked.connect(self.launch_skiponly)
        layout.addRow(self.skiponly_label, self.btn_skiponly)

        # Data Name       
        self.le_data_name = QLineEdit(self.data_name)
        self.le_data_name.setPlaceholderText(self.appctx.datasets[self.appctx.current_dataset_idx].name)
        self.le_data_name.textChanged.connect(self.update_data_name)
        layout.addRow("Save Dataset Name: ", self.le_data_name)

        # Recode Values
        values_layout = QHBoxLayout()

        # From Group
        from_group = QGroupBox("From")
        from_group_layout = QVBoxLayout()
        self.from_input = QLineEdit(self.from_value)
        self.from_input.setPlaceholderText(f"Old Value")
        self.from_input.textChanged.connect(self.update_from_value)
        self.from_kind_int = QRadioButton("Integer", parent=self)
        self.from_kind_float = QRadioButton("Float", parent=self)
        self.from_kind_string = QRadioButton("String", parent=self)
        self.from_kind_string.setChecked(True)
        self.from_kind_None = QRadioButton("None", parent=self)

        # Disable input when "None" is selected and use validators
        self.from_kind_int.clicked.connect(lambda: self.update_input_type(self.from_input, 'int'))
        self.from_kind_float.clicked.connect(lambda: self.update_input_type(self.from_input, 'float'))
        self.from_kind_string.clicked.connect(lambda: self.update_input_type(self.from_input, 'str'))
        self.from_kind_None.clicked.connect(lambda: self.update_input_type(self.from_input, None))

        from_group_layout.addWidget(self.from_input)
        from_group_layout.addWidget(self.from_kind_int)
        from_group_layout.addWidget(self.from_kind_float)
        from_group_layout.addWidget(self.from_kind_string)
        from_group_layout.addWidget(self.from_kind_None)
        from_group.setLayout(from_group_layout)
        values_layout.addWidget(from_group)

        # To Group
        to_group = QGroupBox("To")
        to_group_layout = QVBoxLayout()
        self.to_input = QLineEdit(self.to_value)
        self.to_input.setPlaceholderText(f"New Value")
        self.to_input.textChanged.connect(self.update_to_value)
        self.to_kind_int = QRadioButton("Integer", parent=self)
        self.to_kind_float = QRadioButton("Float", parent=self)
        self.to_kind_string = QRadioButton("String", parent=self)
        self.to_kind_string.setChecked(True)
        self.to_kind_None = QRadioButton("None", parent=self)

        # Disable input when "None" is selected and use validators
        self.to_kind_int.clicked.connect(lambda: self.update_input_type(self.to_input, 'int'))
        self.to_kind_float.clicked.connect(lambda: self.update_input_type(self.to_input, 'float'))
        self.to_kind_string.clicked.connect(lambda: self.update_input_type(self.to_input, 'str'))
        self.to_kind_None.clicked.connect(lambda: self.update_input_type(self.to_input, None))

        to_group_layout.addWidget(self.to_input)
        to_group_layout.addWidget(self.to_kind_int)
        to_group_layout.addWidget(self.to_kind_float)
        to_group_layout.addWidget(self.to_kind_string)
        to_group_layout.addWidget(self.to_kind_None)
        to_group.setLayout(to_group_layout)
        values_layout.addWidget(to_group)

        # Add to main layout
        layout.addRow(values_layout)

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

    @pyqtSlot(str)
    def update_from_value(self, value):
        self.from_value = value

    @pyqtSlot(str)
    def update_to_value(self, value):
        self.to_value = value

    def launch_skiponly(self):
        """Launch a dialog to set skip/only"""
        # Update skip and only
        text, self.skip, self.only = SkipOnlyDialog.get_skip_only(columns=list(self.dataset.df),
                                                                  skip=self.skip, only=self.only,
                                                                  parent=self)
        self.skiponly_label.setText(text)

    def update_types(self):
        """
        Try to convert types, returning None on success and an error message on failure
        """
        # Update from type
        try:
            if self.from_kind_int.isChecked():
                self.from_value = int(self.from_value)
            elif self.from_kind_float.isChecked():
                self.from_value = float(self.from_value)
            elif self.from_kind_string.isChecked():
                self.from_value = str(self.from_value)
            elif self.from_kind_string.isChecked():
                self.from_value = np.nan
        except ValueError:
            return f"Couldn't convert the 'from' value to the selected type"

        # Update to type
        try:
            if self.to_kind_int.isChecked():
                self.to_value = int(self.to_value)
            elif self.to_kind_float.isChecked():
                self.to_value = float(self.to_value)
            elif self.to_kind_string.isChecked():
                self.to_value = str(self.to_value)
            elif self.to_kind_None.isChecked():
                self.to_value = np.nan
        except ValueError:
            return f"Couldn't convert the 'to' value to the selected type"

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
            RunProgress.run_with_progress(progress_str="Recoding variables...",
                                          function=self.get_func(),
                                          slot=slot,
                                          parent=self)
            self.log_command()
            self.accept()
