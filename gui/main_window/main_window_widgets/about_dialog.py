import webbrowser

import clarite
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QFormLayout, QPushButton, QHBoxLayout

from gui.resources import app_resources


class AboutDialog(QDialog):
    """
    This dialog shows some info about CLARITE
    """

    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"About CLARITE GUI")
        self.setModal(True)

        layout = QVBoxLayout()
        top_layout = QFormLayout()
        bottom_layout = QHBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        # GUI Version
        top_layout.addRow("Version", QLabel(self.appctx.VERSION))

        # CLARITE Version
        top_layout.addRow("Using CLARITE version:", QLabel(clarite.__version__))

        # Github
        github_link = QLabel('<a href="https://github.com/HallLab/clarite-gui">CLARITE GUI Repo</a>')
        github_link.setOpenExternalLinks(True)
        top_layout.addRow("Github:", github_link)

        # Hall Lab Logo Button
        self.button = QPushButton('', self)
        self.button.clicked.connect(lambda: self.open_site("https://www.hall-lab.org"))
        self.button.setIcon(QIcon(':/images/hall_lab_logo.png'))
        self.button.setIconSize(QSize(60, 60))
        self.button.setFixedSize(64, 64)
        bottom_layout.addWidget(self.button)

        # Clarite Logo Button
        self.button = QPushButton('', self)
        self.button.clicked.connect(lambda: self.open_site("https://www.hall-lab.org/clarite-python/"))
        self.button.setIcon(QIcon(':/images/clarite_logo.png'))
        self.button.setIconSize(QSize(60, 60))
        self.button.setFixedSize(64, 64)
        bottom_layout.addWidget(self.button)

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)

        # Set Layout
        self.setLayout(layout)

    def open_site(self, site):
        webbrowser.open(site)
