from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget

from widgets.utilities import QHLine
from .dialog_distributions import DistributionsDialog
from .dialog_histogram import HistogramDialog
from .dialog_manhattan import ManhattanPlotDialog


class PlotButtons(QWidget):
    """
    Widget that holds the buttons for Describe commands
    """
    def __init__(self, *args, **kwargs):
        super(PlotButtons, self).__init__(*args, **kwargs)
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

        self.add_button("Histogram", HistogramDialog, layout)
        self.add_button("Distributions", DistributionsDialog, layout)
        self.add_button("Manhattan", ManhattanPlotDialog, layout)

        layout.addWidget(QHLine())

        # Spacer at the end
        layout.addStretch()

    @pyqtSlot()
    def datasets_changed(self):
        """Enable/Disable buttons depending on the kind of the current dataset and the total number of them"""
        df_count = len(self.appctx.datasets)
        if df_count > 0:
            current_kind = self.appctx.datasets[self.appctx.current_dataset_idx].kind
        else:
            current_kind = None

        # Current df must be a dataset for some plots
        for b in ['Histogram', 'Distributions']:
            btn = self.btn_dict[b]
            if current_kind != 'dataset':
                btn.setEnabled(False)
            else:
                btn.setEnabled(True)

        # Must have ewas results for the manhattan plot
        # TODO: Update to make more flexible (don't need to match kind, just certain columns)
        manhattan_btn = self.btn_dict["Manhattan"]
        num_results = len([d for d in self.appctx.datasets if d.kind == 'ewas_result'])
        if num_results > 0:
            manhattan_btn.setEnabled(True)
        else:
            manhattan_btn.setEnabled(False)
