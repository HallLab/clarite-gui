import clarite
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox, QPushButton, QSpinBox, QFileDialog, \
    QComboBox

from widgets import SkipOnlyDialog
from widgets.utilities import RunProgress


class DistributionsDialog(QDialog):
    """
    This dialog sets settings for saving plots of distributions to a pdf file
    """
    CONTINUOUS_KIND_OPTIONS = ['count', 'box', 'violin', 'qq']
    QUALITY_OPTIONS = ['low', 'medium', 'high']

    def __init__(self, *args, **kwargs):
        super(DistributionsDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Data
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.continuous_kind = self.CONTINUOUS_KIND_OPTIONS[0]
        self.nrows = 4
        self.ncols = 3
        self.quality = self.QUALITY_OPTIONS[0]
        self.sort_variables = True
        self.skip = None
        self.only = None
        self.saved_filename = None
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        data = self.dataset.df
        filename = self.saved_filename
        continuous_kind = self.continuous_kind
        nrows = self.nrows
        ncols = self.ncols
        quality = self.quality
        # Get variables based on skip/only
        if self.skip is None and self.only is None:
            variables = None  # All
        elif self.skip is not None:
            variables = [v for v in list(self.dataset) if v not in self.skip]
        elif self.only is not None:
            variables = self.only
        sort = self.sort_variables

        def f():
            clarite.plot.distributions(data=data,
                                       filename=filename,
                                       continuous_kind=continuous_kind,
                                       nrows=nrows, ncols=ncols,
                                       quality=quality,
                                       variables=variables,
                                       sort=sort)
        return f

    def setup_ui(self):
        self.setWindowTitle(f"Plot Variable Distributions")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout(self)
        
        # Skip/Only
        self.skiponly_label = QLabel(self)
        self.skiponly_label.setText(f"Using all {len(list(self.dataset.df)):,} variables")
        self.btn_skiponly = QPushButton("Edit", parent=self)
        self.btn_skiponly.clicked.connect(self.launch_skiponly)
        layout.addRow(self.skiponly_label, self.btn_skiponly)

        # Continuous Kind
        self.continuous_kind_cb = QComboBox(self)
        for option in self.CONTINUOUS_KIND_OPTIONS:
            self.continuous_kind_cb.addItem(option)
        self.continuous_kind_cb.currentIndexChanged.connect(lambda idx: self.update_continuous_kind(idx))
        layout.addRow("Continuous Variable Plots", self.continuous_kind_cb)

        # Nrows
        self.nrows_sb = QSpinBox(self)
        self.nrows_sb.setRange(1, 8)
        self.nrows_sb.setValue(self.nrows)
        self.nrows_sb.valueChanged.connect(self.update_nrows)
        layout.addRow("Rows per page", self.nrows_sb)

        # Ncols
        self.ncols_sb = QSpinBox(self)
        self.ncols_sb.setRange(1, 8)
        self.ncols_sb.setValue(self.ncols)
        self.ncols_sb.valueChanged.connect(self.update_ncols)
        layout.addRow("Columns per page", self.ncols_sb)

        # Quality
        self.quality_cb = QComboBox(self)
        for option in self.QUALITY_OPTIONS:
            self.quality_cb.addItem(option)
        self.quality_cb.currentIndexChanged.connect(lambda idx: self.update_quality(idx))
        layout.addRow("Quality", self.quality_cb)

        # Sort

        # Ok/Cancel
        QBtn = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.rejected.connect(self.reject)

        # Set Layout
        self.setLayout(layout)

    # Slots
    def launch_skiponly(self):
        """Launch a dialog to set skip/only"""
        # Update skip and only
        text, self.skip, self.only = SkipOnlyDialog.get_skip_only(columns=list(self.dataset.df),
                                                                  skip=self.skip, only=self.only,
                                                                  parent=self)
        self.skiponly_label.setText(text)

    @pyqtSlot(int)
    def update_continuous_kind(self, idx):
        self.continuous_kind = self.CONTINUOUS_KIND_OPTIONS[idx]

    @pyqtSlot(int)
    def update_quality(self, idx):
        self.quality = self.QUALITY_OPTIONS[idx]

    @pyqtSlot(int)
    def update_nrows(self, n):
        self.nrows = n

    @pyqtSlot(int)
    def update_ncols(self, n):
        self.ncols = n

    def save(self):
        fileName = QFileDialog.getSaveFileName(self,
                                               self.tr("Save file"), "",
                                               self.tr("PDF files (*.pdf)"))[0]
        if fileName:
            self.saved_filename = fileName

        # Generate and save the PDF
        RunProgress.run_with_progress(progress_str="Saving PDF...",
                                      function=self.get_func(),
                                      slot=lambda: print("Saving PDF"),
                                      parent=self)
        self.accept()
