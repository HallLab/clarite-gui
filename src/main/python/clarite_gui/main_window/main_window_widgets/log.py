from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QFileDialog, QWidget

from widgets.utilities import RunProgress


class LogWidget(QWidget):
    """
    Widget that displays the log
    """
    def __init__(self, filetype="Text Files (*.txt)", initial_log=None, *args, **kwargs):
        super(LogWidget, self).__init__(*args, **kwargs)
        self.messages = []
        self.appctx = self.parent().appctx  # Get App Context
        self.filetype = filetype
        self.setup_ui()
        if initial_log is not None:
            for m in initial_log:
                self.append(m)

    def setup_ui(self):
        # Layout
        layout = QVBoxLayout(self)

        # TextEdit to display the log
        self.log_te = QTextEdit(self)
        self.log_te.setReadOnly(True)
        layout.addWidget(self.log_te)

        # Buttons affecting the log
        log_button_layout = QHBoxLayout()
        log_button_layout.addStretch()

        # Clear Button
        self.btn_clear = QPushButton(text="Clear", parent=self)
        log_button_layout.addWidget(self.btn_clear)
        self.btn_clear.clicked.connect(self.clear_log)

        # Save As button
        self.btn_save_as = QPushButton(text="Save As", parent=self)
        log_button_layout.addWidget(self.btn_save_as)
        self.btn_save_as.clicked.connect(self.save_log)

        # Buttons start disabled because the log is empty
        self.btn_save_as.setEnabled(False)
        self.btn_clear.setEnabled(False)

        # Save the layout
        layout.addLayout(log_button_layout)

        # Add the initial log to the text edit
        for m in self.messages:
            self.append(m)

    def append(self, message):
        """Slot to add to the log"""
        # Append the new message to the internal list of strings
        self.messages.append(message)
        # Append the new message
        self.log_te.moveCursor(QTextCursor.End)
        self.log_te.insertPlainText(message)
        # Ensure the buttons are enabled since there is now log data
        self.btn_save_as.setEnabled(True)
        self.btn_clear.setEnabled(True)

    def clear_log(self):
        """Clear the displayed and the stored log"""
        self.messages = []
        self.log_te.clear()
        self.btn_save_as.setEnabled(False)
        self.btn_clear.setEnabled(False)

    def save_log(self):
        """Save the log"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, ok = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                   self.filetype, options=options)

        # Return without doing anything if a valid file wasn't selected
        if not ok:
            return

        # Define a no-parameter function to save the data using a thread
        log = self.messages

        def save_func():
            with open(filename, 'w') as o:
                o.writelines(log)

        RunProgress.run_with_progress(progress_str="Saving Log...",
                                      function=save_func,
                                      slot=None,
                                      parent=self)
