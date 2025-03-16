from PySide6.QtWidgets import QLineEdit, QComboBox, QCheckBox
from PySide6.QtCore import Qt

class TextColumn:
    """A column type for plain text input."""
    def create_editor(self, parent):
        editor = QLineEdit(parent)
        return editor

    def set_editor_data(self, editor, value):
        editor.setText(value)

    def get_editor_data(self, editor):
        return editor.text()

class DropdownColumn:
    """A column type for dropdown selection."""
    def __init__(self, options):
        self.options = options

    def create_editor(self, parent):
        editor = QComboBox(parent)
        editor.addItems(self.options)
        return editor

    def set_editor_data(self, editor, value):
        editor.setCurrentText(value)

    def get_editor_data(self, editor):
        return editor.currentText()

class CheckboxColumn:
    """A column type for checkbox toggles."""
    def create_editor(self, parent):
        editor = QCheckBox(parent)
        editor.setChecked(False)
        editor.setStyleSheet("margin-left: 50%; margin-right: 50%;")
        return editor

    def set_editor_data(self, editor, value):
        editor.setChecked(value == "True")

    def get_editor_data(self, editor):
        return "True" if editor.isChecked() else "False"