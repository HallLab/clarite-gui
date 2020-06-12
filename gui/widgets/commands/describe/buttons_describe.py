from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget

from gui.widgets.utilities import QHLine
from .dialog_correlations import CorrelationDialog
from .dialog_datatypes import DataTypesDialog
from .dialog_freqtable import FreqTableDialog
from .dialog_percentna import PercentNADialog
from .dialog_skewness import SkewnessDialog


class DescribeButtons(QWidget):
    """
    Widget that holds the buttons for Describe commands
    """
    def __init__(self, *args, **kwargs):
        super(DescribeButtons, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx

        self.btn_dict = {}  # Keep a reference to each button by name
        self.add_buttons()

        self.appctx.signals.added_dataset.connect(self.datasets_changed)
        self.appctx.signals.removed_dataset.connect(self.datasets_changed)
        self.appctx.signals.changed_dataset.connect(self.datasets_changed)

    def add_button(self, text, dialog, layout, **kwargs):
        btn = QPushButton(text=text, parent=self)
        btn.clicked.connect(lambda: dialog(parent=self.appctx.main_window, **kwargs).show())
        layout.addWidget(btn)
        self.btn_dict[text] = btn

    def add_buttons(self):
        layout = QVBoxLayout(self)

        self.add_button("Correlations", CorrelationDialog, layout)
        self.add_button("Frequency Table", FreqTableDialog, layout)
        self.add_button("Data Types", DataTypesDialog, layout)
        self.add_button("Percent NA", PercentNADialog, layout)
        self.add_button("Skewness", SkewnessDialog, layout)

        layout.addWidget(QHLine())

        # Spacer at the end
        layout.addStretch()

    @pyqtSlot()
    def datasets_changed(self):
        """Enable/Disable buttons depending on the kind of the current dataset and the total number of them"""
        df_count = len(self.appctx.datasets)
        if df_count > 0:
            current_kind = self.appctx.datasets[self.appctx.current_dataset_idx].kind
            dataset_count = len([d for d in self.appctx.datasets if d.kind == 'dataset'])
        else:
            current_kind = None
            dataset_count = 0

        # Current df must be a dataset
        for btn in self.btn_dict.values():
            if current_kind != 'dataset' or dataset_count == 0:
                btn.setEnabled(False)
            else:
                btn.setEnabled(True)
