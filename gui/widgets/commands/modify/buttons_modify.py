from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget

from gui.widgets.utilities import QHLine
from .dialog_categorize import CategorizeDialog
from .dialog_colfilter import ColfilterDialog
from .dialog_colfilter_mincatn import ColfilterMinCatN
from .dialog_colfilter_minn import ColfilterMinN
from .dialog_colfilter_pzero import ColfilterPZeroDialog
from .dialog_drop_extra_cat import DropExtraCatDialog
from .dialog_make_type import MakeTypeDialog
from .dialog_merge_obs import MergeObsDialog
from .dialog_merge_vars import MergeVarsDialog
from .dialog_recode_values import RecodeValuesDialog
from .dialog_remove_outliers import RemoveOutliersDialog
from .dialog_rowfilter import RowfilterDialog
from .dialog_rowfilter_incomplete import RowfilterIncompleteDialog
from .dialog_transform import TransformDialog


class ModifyButtons(QWidget):
    """
    Widget that holds the buttons for Modify commands
    """

    def __init__(self, *args, **kwargs):
        super(ModifyButtons, self).__init__(*args, **kwargs)
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

        self.add_button("Categorize", CategorizeDialog, layout)
        layout.addWidget(QHLine())
        self.add_button("Colfilter", ColfilterDialog, layout)
        self.add_button("Colfilter Percent Zero", ColfilterPZeroDialog, layout)
        self.add_button("Colfilter Min N", ColfilterMinN, layout)
        self.add_button("Colfilter Min Cat N", ColfilterMinCatN, layout)
        layout.addWidget(QHLine())
        self.add_button("Make Binary", MakeTypeDialog, layout, var_type="binary")
        self.add_button(
            "Make Categorical", MakeTypeDialog, layout, var_type="categorical"
        )
        self.add_button(
            "Make Continuous", MakeTypeDialog, layout, var_type="continuous"
        )
        layout.addWidget(QHLine())
        self.add_button("Merge Observations", MergeObsDialog, layout)
        self.add_button("Merge Variables", MergeVarsDialog, layout)
        layout.addWidget(QHLine())
        self.add_button("Recode Values", RecodeValuesDialog, layout)
        self.add_button("Remove Outliers", RemoveOutliersDialog, layout)
        self.add_button("Drop Extra Categories", DropExtraCatDialog, layout)
        layout.addWidget(QHLine())
        self.add_button("Rowfilter", RowfilterDialog, layout)
        self.add_button("Rowfilter Incomplete Obs", RowfilterIncompleteDialog, layout)
        layout.addWidget(QHLine())
        self.add_button("Transform", TransformDialog, layout)

        # Spacer at the end
        layout.addStretch()

    @pyqtSlot()
    def datasets_changed(self):
        """Enable/Disable buttons depending on the kind of the current dataset and the total number of them"""
        df_count = len(self.appctx.datasets)
        if df_count > 0:
            current_kind = self.appctx.datasets[self.appctx.current_dataset_idx].kind
            dataset_count = len(
                [d for d in self.appctx.datasets if d.kind == "dataset"]
            )
        else:
            current_kind = None
            dataset_count = 0

        # Disable all buttons by default
        for btn in self.btn_dict.values():
            btn.setEnabled(False)

        # Enable rowfilter and colfilter if at least one df is loaded
        if df_count > 0:
            for b in ["Colfilter", "Rowfilter"]:
                btn = self.btn_dict[b]
                btn.setEnabled(True)

        # Enable others if a dataset is currently shown
        if current_kind == "dataset":
            for btn in self.btn_dict.values():
                btn.setEnabled(True)

        # Disable merge buttons if there are not at least two datasets loaded
        if dataset_count < 2:
            for b in ["Merge Observations", "Merge Variables"]:
                btn = self.btn_dict[b]
                btn.setEnabled(False)
