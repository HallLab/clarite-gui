from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QTableView, QMenu


class DatasetTableView(QTableView):
    """
    Widget allowing for selection and display of a dataset
    """
    def __init__(self, *args, **kwargs):
        super(DatasetTableView, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx  # Get App Context
        self.setup_ui()

    def setup_ui(self):
        # Note: Don't try to automatically adjust columns to content width: freezes when loading a big csv
        # header = self.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.ResizeToContents)
        pass

    def contextMenuEvent(self, pos):
        if self.selectionModel().selection().indexes():
            for i in self.selectionModel().selection().indexes():
                click_row, click_col = i.row(), i.column()
            menu = TableContextMenu(parent=self, click_row=click_row, click_col=click_col)
            menu.popup(QCursor.pos())


class TableContextMenu(QMenu):
    def __init__(self, click_col, click_row, *args, **kwargs):
        super(TableContextMenu, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.data_kind = self.appctx.datasets[self.appctx.current_dataset_idx].kind
        self.setup_ui()
        self.click_col = click_col
        self.click_row = click_row

    def setup_ui(self):
        # Add 'rename'
        action_rename = self.addAction("Rename column")
        action_rename.triggered.connect(lambda: self.appctx.data_model.slot_rename(self.click_col))
        # Add 'convert' menu
        if self.data_kind == 'dataset':
            convert_menu = self.addMenu("Convert type to...")
            convert_binary = convert_menu.addAction("Binary")
            convert_binary.triggered.connect(lambda: self.appctx.data_model.slot_convert('binary', self.click_col))
            convert_categorical = convert_menu.addAction("Categorical")
            convert_categorical.triggered.connect(
                lambda: self.appctx.data_model.slot_convert('categorical', self.click_col))
            convert_continuous = convert_menu.addAction("Continuous")
            convert_continuous.triggered.connect(
                lambda: self.appctx.data_model.slot_convert('continuous', self.click_col))
            convert_unknown = convert_menu.addAction("Unknown")
            convert_unknown.triggered.connect(lambda: self.appctx.data_model.slot_convert('unknown', self.click_col))
