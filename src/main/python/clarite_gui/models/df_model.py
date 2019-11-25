import clarite
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QSettings
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox

from widgets.utilities import show_warning


class PandasDFModel(QtCore.QAbstractTableModel):
    """
    Manage current state for the currently selected dataset
    """
    def __init__(self, appctx, *args):
        super(PandasDFModel, self).__init__()
        self.appctx = appctx
        self.read_settings()
        self.appctx.data_model = self  # Add self to the appctx
        if self.appctx.current_dataset_idx is None:
            self.dataset = None
            self.dtypes = None
            self.kind = None
        else:
            self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
            self.dtypes = self.dataset.get_types()
            self.kind = self.dataset.kind

    def read_settings(self):
        settings = QSettings(self.appctx.ORG, self.appctx.APPLICATION)

        # Read Header Settings
        settings.beginGroup("display/header")
        default_font = QFont("sans-serif", pointSize=12, weight=QFont.Bold, italic=False)
        self.header_font = QFont(settings.value("font", defaultValue=default_font))
        settings.endGroup()

        # Read Index Settings
        settings.beginGroup("display/index")
        default_font = QFont("sans-serif", pointSize=10, weight=QFont.Normal, italic=False)
        self.index_font = QFont(settings.value("font", defaultValue=default_font))
        settings.endGroup()

        # Read Data Settings
        settings.beginGroup("display/data")
        # Font
        default_font = QFont("sans-serif", pointSize=10, weight=QFont.Normal, italic=False)
        self.data_font = QFont(settings.value("font", defaultValue=default_font))
        # Colors
        self.data_bgcolor_unknown = QColor(settings.value("bgcolor_unknown",
                                                          defaultValue=QColor.fromRgb(255, 255, 255)))
        self.data_bgcolor_binary = QColor(settings.value("bgcolor_binary",
                                                         defaultValue=QColor.fromRgb(255, 204, 153)))
        self.data_bgcolor_categorical = QColor(settings.value("bgcolor_categorical",
                                                              defaultValue=QColor.fromRgb(153, 204, 255)))
        self.data_bgcolor_continuous = QColor(settings.value("bgcolor_continuous",
                                                             defaultValue=QColor.fromRgb(204, 153, 255)))
        # Float Precision
        self.data_float_precision = settings.value("float_precision", defaultValue=3)
        settings.endGroup()

    def refresh(self):
        """Update display based on the currently selected data in the app context"""
        # Start
        self.beginResetModel()

        # Reload settings
        self.read_settings()

        # Remove if there are no datasets
        current_dataset_num = len(self.appctx.datasets)
        if current_dataset_num == 0 or self.appctx.current_dataset_idx > current_dataset_num:
            self.dataset = None
            self.dtypes = None
            self.kind = None
        else:
            self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
            self.dtypes = self.dataset.get_types()
            self.kind = self.dataset.kind

        # Recolor Legend
        self.appctx.dataset_widget.color_legend()

        # Done
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.dataset is None:
            return 0
        else:
            return len(self.dataset.df)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if self.dataset is None:
            return 0
        else:
            return len(list(self.dataset.df))

    def get_legend_label(self, var_type):
        """For example, '345 continuous'"""
        if self.dataset is None:
            return f"0 {var_type}"
        else:
            count = self.dataset.get_types().value_counts().get(var_type, 0)
            return f"{count:,} {var_type}"

    def headerData(self, section: int, orientation, role):
        """
        Return the formatted section-th index label depending on whether it's for the horizontal orientation (column) or vertical (row)
        """
        settings = QSettings(self.appctx.ORG, self.appctx.APPLICATION)

        # Return values
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal: 
                # Return column name
                return self.dataset.get_column_name(section)
            else:
                # Return index value (as a string)
                return self.dataset.get_row_name(section)

        # Tooltip (for a dataset)
        elif role == QtCore.Qt.ToolTipRole and self.kind == 'dataset':
            if orientation == QtCore.Qt.Horizontal:
                col_name = self.dataset.get_column_name(section)
                col_type = self.dtypes[section]
                col = self.dataset.df[col_name]
                return (f"{col_type}\n"
                        f"{len(col.unique()):,} unique values\n"
                        f"{1-(col.count() / len(col)):.2%} NA")
            else:
                # Return index value (as a string)
                row = self.dataset.df.iloc[section]
                na_count = row.isnull().sum() 
                return f"{na_count / len(row):.2%} NA"
        
        # Font
        elif role == QtCore.Qt.FontRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header_font
            else:
                return self.index_font
        
        # Text Alignment    
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        # Anything Else
        else:
            return None

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Return the formatted data at the given index"""
        # Data
        if role == QtCore.Qt.DisplayRole:
            row_idx = index.row()
            col_idx = index.column()
            value = self.dataset.df.iloc[row_idx, col_idx]
            if type(value) is pd.np.float64:
                return f"{value:.{self.data_float_precision}E}"
            else:
                return str(value)
        
        # BG Color based on datatype in datasets
        elif role == QtCore.Qt.BackgroundRole and self.kind == 'dataset':
            # Background color based on data type
            col_idx = index.column()
            col_dtype = self.dtypes.iloc[col_idx]
            if col_dtype == 'binary':
                return self.data_bgcolor_binary
            elif col_dtype == 'categorical':
                return self.data_bgcolor_categorical
            elif col_dtype == 'continuous':
                return self.data_bgcolor_continuous
            else:
                return self.data_bgcolor_unknown

        # Text Alignment
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        # Font
        elif role == QtCore.Qt.FontRole:
            return self.data_font

        return None

    # Functions modifying the data
    def slot_convert(self, kind, column_idx):
        column = self.dataset.get_column_name(column_idx)

        # Determine which function to run in order to convert
        if kind == 'binary':
            convert_func = clarite.modify.make_binary
        elif kind == 'categorical':
            convert_func = clarite.modify.make_categorical
        elif kind == 'continuous':
            convert_func = clarite.modify.make_continuous
        else:
            show_warning("Error converting to unknown", "Converting to unknown type is not yet implemented.")
            return

        # Try to convert, reporting any errors
        try:
            self.appctx.update_data(convert_func(self.dataset.df, only=column))
        except ValueError as e:
            show_warning(f"Error converting to {kind}", str(e))
            return

        # Log successful conversion
        info_str = f"\nConverted '{column}' to {kind} in '{self.dataset.get_selector_name()}'\n"
        self.appctx.log_info("\n" + "=" * 80 + info_str + "=" * 80)
        self.appctx.log_python(f"{self.dataset.get_python_name()} = "
                               f"clarite.modify.make_{kind}("
                               f"data={self.dataset.get_python_name()}, "
                               f"skip=[], "
                               f"only=['{column}'])")

    def slot_rename(self, column_idx):
        column = self.dataset.get_column_name(column_idx)
        # Show a dialog
        new_name = RenameDialog.get_new_name(data=self.appctx.datasets[self.appctx.current_dataset_idx].df,
                                             column=column,
                                             parent=self.parent())
        if new_name is None:
            return

        try:
            self.appctx.update_data(self.dataset.df.rename(columns={column: new_name}))
        except ValueError as e:
            show_warning("Error renaming column", str(e))
            return

        # Log successful rename
        info_str = f"\nRenamed '{column}' to '{new_name}' in '{self.dataset.get_selector_name()}'\n"
        self.appctx.log_info("\n" + "="*80 + info_str + "="*80)
        self.appctx.log_python(f"{self.dataset.get_python_name()} = "
                               f"{self.dataset.get_python_name()}.rename("
                               f"columns={repr({column: new_name})})")




class RenameDialog(QDialog):

    def __init__(self, data=None, column=None, parent=None):
        super(RenameDialog, self).__init__(parent)
        self.setWindowTitle(f"Rename Column '{column}'")
        self.data = data
        self.old_name = column
        self.new_name = None

        # Setup Layout
        layout = QFormLayout(self)

        # New column name
        self.le_new_name = QLineEdit(self.new_name)
        self.le_new_name.setPlaceholderText(self.old_name)
        self.le_new_name.textChanged.connect(self.update_new_name)
        layout.addRow("New Column Name: ", self.le_new_name)

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)

    @pyqtSlot(str)
    def update_new_name(self, name):
        self.new_name = name
        if self.new_name is None:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def submit(self):
        # TODO: Add any warnings here
        if self.new_name == self.old_name:
            self.reject()
        elif self.new_name in list(self.data):
            show_warning("Error renaming column", f"The specified column ('{self.new_name}') already exists")
        else:
            self.accept()

    @staticmethod
    def get_new_name(data=None, column=None, parent=None):
        dlg = RenameDialog(data, column, parent)
        result = dlg.exec_()
        name = dlg.new_name
        # Return
        return name
