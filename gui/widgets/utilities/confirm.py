from typing import Callable, Dict

from PyQt5.QtWidgets import QMessageBox, QWidget

btn_map = {
    "Ok": QMessageBox.Ok,
    "Open": QMessageBox.Open,
    "Save": QMessageBox.Save,
    "Cancel": QMessageBox.Cancel,
    "Close": QMessageBox.Close,
    "Discard": QMessageBox.Discard,
    "Apply": QMessageBox.Apply,
    "Yes": QMessageBox.Yes,
    "No": QMessageBox.No,
    "Abort": QMessageBox.Abort,
    "Retry": QMessageBox.Retry,
    "Ignore": QMessageBox.Ignore,
}


def confirm_click(
    parent: QWidget, txt: str, inform_txt: str, button_slots: Dict[str, Callable]
) -> None:
    """
    Confirm an operation, hooking up button to slots (or None) depending on what is clicked.
    Valid buttons:
        Ok, Open, Save, Cancel, Close, Discard, Apply, Yes, No, Abort, Retry, Ignore
    """
    msg_box = QMessageBox(parent=parent)
    msg_box.setText(txt)
    msg_box.setInformativeText(inform_txt)
    button_refs = dict()  # Map button name to the actual created buttons
    for btn_name, slot in button_slots.items():
        if btn_name not in btn_map:
            raise NotImplementedError(f"No button named '{btn_name}'")
        button_refs[btn_name] = msg_box.addButton(btn_map[btn_name])

    # Show the message box and wait for a click
    msg_box.exec()

    # Run the slot for the clicked button
    for btn_name, button in button_refs.items():
        if msg_box.clickedButton() == button:
            clicked_slot = button_slots[btn_name]
            if clicked_slot is not None:
                clicked_slot()
            else:
                break
    return
