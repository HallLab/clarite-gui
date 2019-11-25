from contextlib import redirect_stdout

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QProgressDialog

from .warnings import show_critical


class RunProgress(QProgressDialog):
    """
    Convenience class to run a function in a qthread, showing a progress dialog while it runs.
    Any errors in the function result in a warning dialog.
    After initializing, use set_function to specify a no-parameter function that gets run in a thread.
    Optionally use set_slot to specify a slot for any returned results

    Parameters
    ----------
    progress_str: The string displayed in the progress dialog

    """
    def __init__(self, progress_str, parent, *args, **kwargs):
        super(RunProgress, self).__init__(progress_str, "Cancel", 0, 0, parent=parent, *args, **kwargs)
        # Create thread running the command
        self.thread = RunThread(self)
        self.func = None
        self.slot = None
        self.appctx = parent.appctx

    def set_function(self, func):
        self.thread.func = func

    def set_slot(self, slot):
        self.slot = slot

    def run(self):
        if self.thread.func is None:
            raise ValueError("set_function(func) must be called before calling run()")
        # Connect the result signal to the slot, if one was provided
        if self.slot is not None:
            self.thread.result.connect(self.slot)
        # Connect other thread signals
        self.thread.message.connect(self.appctx.log_info)
        self.thread.error.connect(lambda s: show_critical("Error", s))
        self.thread.finished.connect(self.close)
        self.canceled.connect(self.thread.cancel)  # Exit thread if the operation is cancelled
        # Start the thread
        self.thread.start()
        # Show self
        self.exec_()

    @staticmethod
    def run_with_progress(progress_str, function, slot, parent, *args, **kwargs):
        """Run a function in a thread with a progress dialog"""
        progress = RunProgress(progress_str, parent, *args, **kwargs)
        progress.set_function(function)
        progress.set_slot(slot)
        progress.run()


class RunThread(QThread):
    """
    Runs a function in a QThread.  Signaling the 'cancel' slot will attempt to quit the thread, but will prevent any result from being used regardless. 
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    message = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(RunThread, self).__init__(*args, **kwargs)
        self.cancelled = False
        self.func = None

    @pyqtSlot()
    def cancel(self):
        self.cancelled = True
        self.quit()

    def run(self):
        with redirect_stdout(self):
            try:
                result = self.func()
                if not self.cancelled:
                    self.result.emit(result)
                self.finished.emit()
            except Exception as e:
                self.error.emit(str(e))
                self.finished.emit()

    def write(self, message):
        self.message.emit(message)

    def flush(self):
        """must be implemented"""
        pass
