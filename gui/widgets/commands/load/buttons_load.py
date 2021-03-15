from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget

from .dialog_from_txt import FromTxtDialog


class LoadButtons(QWidget):
    """
    Widget that holds the buttons for Load commands
    """

    def __init__(self, *args, **kwargs):
        super(LoadButtons, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.add_buttons()

    def add_buttons(self):
        layout = QVBoxLayout(self)

        # From CSV
        btn_from_csv = QPushButton(text="From CSV", parent=self)
        btn_from_csv.clicked.connect(lambda: self.show_load_from("CSV"))
        layout.addWidget(btn_from_csv)
        # From TSV
        btn_from_tsv = QPushButton(text="From TSV", parent=self)
        btn_from_tsv.clicked.connect(lambda: self.show_load_from("TSV"))
        layout.addWidget(btn_from_tsv)
        # Spacer at the end
        layout.addStretch()

    # Button Functions
    def show_load_from(self, kind):
        dlg = FromTxtDialog(parent=self.appctx.main_window, kind=kind)
        dlg.show()
