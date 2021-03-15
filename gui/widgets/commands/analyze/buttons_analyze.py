from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget

from gui.widgets.utilities import QHLine
from .dialog_corrected_pval import CorrectedPvalDialog
from .dialog_ewas import EWASDialog


class AnalyzeButtons(QWidget):
    """
    Widget that holds the buttons for Describe commands
    """

    def __init__(self, *args, **kwargs):
        super(AnalyzeButtons, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx

        self.btn_dict = {}  # Keep a reference to each button by name
        self.add_buttons()

        self.appctx.signals.added_dataset.connect(self.datasets_changed)
        self.appctx.signals.removed_dataset.connect(self.datasets_changed)
        self.appctx.signals.changed_dataset.connect(self.datasets_changed)

    def add_button(self, text, dialog, layout, **kwargs):
        btn = QPushButton(text=text, parent=self)
        btn.clicked.connect(
            lambda: dialog(parent=self.appctx.main_window, **kwargs).show()
        )
        btn.setEnabled(
            False
        )  # Start disabled until a dataset is loaded, triggering 'datasets changed'
        layout.addWidget(btn)
        self.btn_dict[text] = btn

    def add_buttons(self):
        layout = QVBoxLayout(self)

        self.add_button("EWAS", EWASDialog, layout)
        self.add_button("Add Corrected Pvalues", CorrectedPvalDialog, layout)

        layout.addWidget(QHLine())

        # Spacer at the end
        layout.addStretch()

    @pyqtSlot()
    def datasets_changed(self):
        """Enable/Disable buttons depending on the kind of the current dataset and the total number of them"""
        df_count = len(self.appctx.datasets)
        if df_count > 0:
            current_kind = self.appctx.datasets[self.appctx.current_dataset_idx].kind
            current_columns = list(
                self.appctx.datasets[self.appctx.current_dataset_idx].df
            )
        else:
            current_kind = None
            current_columns = []

        # Current df must be a dataset for ewas
        if current_kind != "dataset":
            self.btn_dict["EWAS"].setEnabled(False)
        else:
            self.btn_dict["EWAS"].setEnabled(True)

        # Must have pvalue column to add corrected pvalues
        if "pvalue" in current_columns and "converged" in current_columns:
            self.btn_dict["Add Corrected Pvalues"].setEnabled(True)
        else:
            self.btn_dict["Add Corrected Pvalues"].setEnabled(False)
