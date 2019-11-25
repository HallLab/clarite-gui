from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QDialog, QListView, QAbstractItemView, QVBoxLayout, QGroupBox,
                             QDialogButtonBox, QLineEdit)


class SelectColumnDialog(QDialog):
    """
    Dialog for selecting a single column from the current dataframe
    """

    def __init__(self, columns=None, selected=None, parent=None):
        super(SelectColumnDialog, self).__init__(parent)
        self.setWindowTitle("Select Column")
        self.columns = columns
        self.selected = selected  # Name of selected variable, or None.

        # Available
        self.varlist_model = QStandardItemModel(self)

        # Proxy model for filtering/sorting
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.varlist_model)
        self.proxy.setFilterKeyColumn(0)  # Filters based on the only column
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)  # Case insensitive search

        # Setup Layout
        layout = QVBoxLayout(self)

        # Left Side Group Box ("Available")
        varlist_box = QGroupBox("Available Variables")
        varlist_box_layout = QVBoxLayout()
        # Multiselect listing available columns
        self.varlist = QListView(self)
        self.varlist.setModel(self.proxy)
        self.varlist.setSelectionMode(QAbstractItemView.SingleSelection)
        self.varlist.selectionModel().selectionChanged.connect(self.selected_change)
        self.varlist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        varlist_box_layout.addWidget(self.varlist)

        # Add a search box
        self.varlist_search = QLineEdit(parent=self)
        self.varlist_search.setPlaceholderText('Search...')
        self.varlist_search.textChanged.connect(self.proxy.setFilterFixedString)
        varlist_box_layout.addWidget(self.varlist_search)

        # Set layout and add to the main layout
        varlist_box.setLayout(varlist_box_layout)
        layout.addWidget(varlist_box)

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        # Reset to update
        self.reset_list()

    def selected_change(self):
        """
        Update the current selection.  Disable "Ok" if nothing is selected.
        """
        selection_indexes = self.varlist.selectedIndexes()
        if len(selection_indexes) == 0:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            selected_index = selection_indexes[0]
            self.selected = self.proxy.itemData(selected_index)[0]

    def reset_list(self):
        """Clear the search field and show the full list"""
        self.varlist_search.setText("")
        self.varlist_model.clear()
        for idx, v in enumerate(self.columns):
            self.varlist_model.appendRow(QStandardItem(v))
            if v == self.selected:
                selection_index = self.varlist_model.index(idx, 0)
                mode = QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
                self.varlist.selectionModel().select(selection_index, mode)

    def submit(self):
        # TODO: Add any warnings here
        self.selected = self.selected
        self.accept()

    @staticmethod
    def get_column(columns=None, selected=None, parent=None):
        if columns is None:
            return "No columns", None, None
        # Launch dialog to select a column
        dlg = SelectColumnDialog(columns, selected, parent)
        result = dlg.exec_()
        if result:
            # Update the selected value if the dialog accepted
            selected = dlg.selected
        return selected
