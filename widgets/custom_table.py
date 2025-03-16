from PySide6.QtWidgets import QTreeWidget
from models.column_types import TextColumn, DropdownColumn, CheckboxColumn

class CustomTableWidget(QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.column_types = {}  # Store column types for each column index

    def set_column_type(self, column_index, column_type):
        """Set the column type for a specific column."""
        self.column_types[column_index] = column_type

    def edit_item(self, item, column):
        """Edit an item in the table using the appropriate column type."""
        if column in self.column_types:
            column_type = self.column_types[column]
            if isinstance(column_type, CheckboxColumn):
                self._create_checkbox(item, column)
            else:
                self._create_editor(item, column, column_type)
        else:
            super().editItem(item, column)

    def _create_checkbox(self, item, column):
        """Create a checkbox for the item."""
        checkbox = QCheckBox(self)
        checkbox.setChecked(item.text(column) == "True")
        checkbox.stateChanged.connect(lambda state, item=item: self.checkbox_changed(state, item, column))
        self.layout().addWidget(checkbox)

    def _create_editor(self, item, column, column_type):
        """Create an editor for the item."""
        editor = column_type.create_editor(self)
        editor.setGeometry(self.visualItemRect(item))
        editor.show()

        # Set initial value
        column_type.set_editor_data(editor, item.text(column))

        # Save changes when editing is finished
        def save_changes():
            item.setText(column, column_type.get_editor_data(editor))
            editor.deleteLater()

        editor.editingFinished.connect(save_changes)

    def checkbox_changed(self, state, item, column):
        """Handle checkbox state change."""
        item.setText(column, "True" if state == Qt.Checked else "False")