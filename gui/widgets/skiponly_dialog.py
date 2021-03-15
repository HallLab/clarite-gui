from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QListView,
    QAbstractItemView,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGroupBox,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
)


class SkipOnlyDialog(QDialog):
    def __init__(self, columns=None, skip=None, only=None, parent=None):
        super(SkipOnlyDialog, self).__init__(parent)
        self.setWindowTitle("Select Columns")
        self.columns = columns
        self.selected_variables = (
            []
        )  # Names of selected variables.  Only updated when accepting the dialog.
        # Select 'only' by default (unless a skip list is passed in)
        # starting_only and only are booleans to indicate whether 'only' is selected
        # starting_selected and selected are boolean arrays to indicate whether each variable is selected
        if skip is not None:
            self.starting_only = False
            self.starting_selected = [(c in skip) for c in self.columns]
        elif only is not None:
            self.starting_only = True
            self.starting_selected = [(c in only) for c in self.columns]
        elif skip is None and only is None:
            self.starting_only = True
            self.starting_selected = [False for _ in self.columns]
        else:
            raise ValueError("Can't pass both 'skip' and 'only'")

        # Available- Left Side
        self.left_model = QStandardItemModel(self)
        self.left_proxy = QSortFilterProxyModel(self)
        self.left_proxy.setSourceModel(self.left_model)
        self.left_proxy.setFilterKeyColumn(0)  # Filters based on the only column
        self.left_proxy.setFilterCaseSensitivity(
            Qt.CaseInsensitive
        )  # Case insensitive search
        # Selected - Right side
        self.right_model = QStandardItemModel()
        self.right_proxy = QSortFilterProxyModel(self)
        self.right_proxy.setSourceModel(self.right_model)
        self.right_proxy.setFilterKeyColumn(0)  # Filters based on the only column
        self.right_proxy.setFilterCaseSensitivity(
            Qt.CaseInsensitive
        )  # Case insensitive search

        # Setup Layout
        layout = QGridLayout(self)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)

        # Left Side Group Box ("Available")
        left_list_box = QGroupBox("Available Variables")
        left_list_box_layout = QVBoxLayout()
        # Multiselect listing available columns
        self.left_list = QListView(self)
        self.left_list.setModel(self.left_proxy)
        self.left_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.left_list.selectionModel().selectionChanged.connect(
            self.left_selected_change
        )
        self.left_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        left_list_box_layout.addWidget(self.left_list)
        # Add a search box
        self.left_list_search = QLineEdit(parent=self)
        self.left_list_search.setPlaceholderText("Search...")
        self.left_list_search.textChanged.connect(self.left_proxy.setFilterFixedString)
        left_list_box_layout.addWidget(self.left_list_search)
        # Set layout and add to the main layout
        left_list_box.setLayout(left_list_box_layout)
        layout.addWidget(left_list_box, 0, 0)

        # Add/Remove Buttons
        btns = QWidget()
        btns_layout = QVBoxLayout()
        btns.setLayout(btns_layout)
        # Add
        self.btn_add = QPushButton(text="Add ->", parent=self)
        self.btn_add.clicked.connect(self.add)
        self.btn_add.setEnabled(False)
        btns_layout.addWidget(self.btn_add)
        # Remove
        self.btn_remove = QPushButton(text="<- Remove", parent=self)
        self.btn_remove.clicked.connect(self.remove)
        self.btn_remove.setEnabled(False)
        btns_layout.addWidget(self.btn_remove)
        # Undo Changes
        self.btn_undo = QPushButton(text="Undo Changes", parent=self)
        self.btn_undo.clicked.connect(self.undo)
        self.btn_undo.setEnabled(False)
        btns_layout.addWidget(self.btn_undo)
        # Reset
        self.btn_reset = QPushButton(text="Reset", parent=self)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_reset.setEnabled(False)
        btns_layout.addWidget(self.btn_reset)
        # Add to layout
        layout.addWidget(btns, 0, 1)

        # Right Side Group Box ("Selected")
        right_list_box = QGroupBox("Selected Variables")
        right_list_box_layout = QVBoxLayout()
        # Multiselect listing current selected columns
        self.right_list = QListView(self)
        self.right_list.setModel(self.right_proxy)
        self.right_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.right_list.selectionModel().selectionChanged.connect(
            self.right_selected_change
        )
        self.right_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        right_list_box_layout.addWidget(self.right_list)
        # Add a search box
        self.right_list_search = QLineEdit(parent=self)
        self.right_list_search.setPlaceholderText("Search...")
        self.right_list_search.textChanged.connect(
            self.right_proxy.setFilterFixedString
        )
        right_list_box_layout.addWidget(self.right_list_search)
        # Set layout and add to the main layout
        right_list_box.setLayout(right_list_box_layout)
        layout.addWidget(right_list_box, 0, 2)

        # Radio Select for Skip/Only
        self.radio_btns = QGroupBox("Skip Selected or Only Selected")
        radio_btns_layout = QHBoxLayout()
        self.radio_btns.setLayout(radio_btns_layout)
        self.radio_skip = QRadioButton("skip")
        radio_btns_layout.addWidget(self.radio_skip)
        self.radio_only = QRadioButton("only")
        self.radio_only.setChecked(True)
        radio_btns_layout.addWidget(self.radio_only)
        # If either button changes, a toggle signal is called for each one.  No need to pass the "checked" parameter.
        self.radio_skip.toggled.connect(lambda is_checked: self.update_result())
        layout.addWidget(self.radio_btns, 1, 2)

        # Result label
        self.result_label = QLabel(parent=self)
        self.result_label.setText("0 Variables to be used")
        layout.addWidget(self.result_label, 2, 0)

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox, 2, 2)

        # Run reset to initialize
        self.undo()

    def undo(self):
        """
        Reset both list views and set the parameters ('only' and 'selected') to their starting values
        """
        # Clear lists
        self.left_model.clear()
        self.right_model.clear()
        # Set to the starting state
        self.selected = (
            self.starting_selected.copy()
        )  # Take a copy, don't refer to the same list
        self.only = self.starting_only
        for v, is_selected in zip(self.columns, self.selected):
            if not is_selected:
                self.left_model.appendRow(QStandardItem(v))
            else:
                self.right_model.appendRow(QStandardItem(v))
        self.update_result()
        self.btn_undo.setEnabled(False)  # No reason to undo twice

    def reset(self):
        """
        Remove the initialized state to do a complete reset
        """
        self.starting_only = True
        self.starting_selected = [False for _ in self.columns]
        self.undo()
        self.btn_reset.setEnabled(False)  # No reason to reset twice

    def left_selected_change(self):
        """
        Track the currently selected rows on the left
        """
        left_selected_num = len(self.left_list.selectedIndexes())
        if left_selected_num == 0:
            self.btn_add.setEnabled(False)
        else:
            self.btn_add.setEnabled(True)

    def right_selected_change(self):
        """
        track the currently selected rows on the right
        """
        right_selected_num = len(self.right_list.selectedIndexes())
        if right_selected_num == 0:
            self.btn_remove.setEnabled(False)
        else:
            self.btn_remove.setEnabled(True)

    def reset_list(self, side):
        """Clear the search field and show the full list"""
        if side == "available":
            self.left_list_search.setText("")
            self.left_model.clear()
            for v, is_selected in zip(self.columns, self.selected):
                if not is_selected:
                    self.left_model.appendRow(QStandardItem(v))
        elif side == "selected":
            self.right_list_search.setText("")
            self.right_model.clear()
            for v, is_selected in zip(self.columns, self.selected):
                if is_selected:
                    self.right_model.appendRow(QStandardItem(v))

    def add(self):
        """
        Move currently selected columns on the left to the right side
        """
        # Clear any right-side search
        self.reset_list("selected")
        # Get selection rows (indexed directly in the model)
        left_selected = sorted(
            [
                self.left_proxy.mapToSource(idx).row()
                for idx in self.left_list.selectedIndexes()
            ]
        )
        # Move items
        for idx in left_selected:
            item = self.left_model.takeItem(idx)
            self.right_model.appendRow(item)
            # Mark as selected
            col_idx = self.columns.index(item.text())
            self.selected[col_idx] = True
        # Delete rows after moving them (don't do it during because it causes index changes)
        for idx in reversed(
            left_selected
        ):  # Remove in reverse order, otherwise index changes
            self.left_model.removeRow(idx)
        # Update label
        self.update_result()
        # Disable Add since nothing is now selected
        self.btn_add.setEnabled(False)

    def remove(self):
        """
        Move currently selected columns on the right to the left side
        """
        # Clear any left-side search
        self.reset_list("available")
        # Get selection rows (indexed directly in the model)
        right_selected = sorted(
            [
                self.right_proxy.mapToSource(idx).row()
                for idx in self.right_list.selectedIndexes()
            ]
        )
        # Move items
        for idx in right_selected:
            item = self.right_model.takeItem(idx)
            self.left_model.appendRow(item)
            # Mark as not selected
            col_idx = self.columns.index(item.text())
            self.selected[col_idx] = False
        # Delete rows after moving them (don't do it during because it causes index changes)
        for idx in reversed(
            right_selected
        ):  # Remove in reverse order, otherwise index changes
            self.right_model.removeRow(idx)
        # Update label
        self.update_result()
        # Disable Remove since nothing is now selected
        self.btn_remove.setEnabled(False)

    def update_result(self):
        """
        Update the tracking of what variables will be used
        """
        self.only = self.radio_only.isChecked()
        num_selected = sum(self.selected)
        if num_selected == 0:
            self.result_label.setText(f"Using all {len(self.columns):,} variables")
        elif self.only:
            self.result_label.setText(
                f"Only using {num_selected:,} of {len(self.columns):,} variables"
            )
        else:
            self.result_label.setText(
                f"Skipping {num_selected:,} of {len(self.columns):,} variables"
            )

        # Set the undo button status
        if self.selected == self.starting_selected and self.only == self.starting_only:
            # In the starting state
            self.btn_undo.setEnabled(False)
        else:
            self.btn_undo.setEnabled(True)

        # Set the reset button status
        if num_selected == 0 and self.only:
            # In the default state
            self.btn_reset.setEnabled(False)
        else:
            self.btn_reset.setEnabled(True)

    def submit(self):
        # TODO: Add any warnings here
        self.selected_variables = [
            c for (c, is_selected) in zip(self.columns, self.selected) if is_selected
        ]
        self.accept()

    @staticmethod
    def get_skip_only(columns=None, skip=None, only=None, parent=None):
        if columns is None:
            return "No columns", None, None
        # Launch dialog to select skip and only
        dlg = SkipOnlyDialog(columns, skip, only, parent)
        result = dlg.exec_()
        # Get info from the dialog
        label = dlg.result_label.text()
        if dlg.only:
            skip = None
            only = dlg.selected_variables
        else:
            skip = dlg.selected_variables
            only = None
        # Return
        return label, skip, only
