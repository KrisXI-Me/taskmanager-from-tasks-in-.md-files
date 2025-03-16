import json
from PySide6.QtCore import QSettings

def save_column_config(tree_widget, settings):
    """Save the current column configuration for QTreeWidget."""
    columns = []
    for i in range(tree_widget.columnCount()):
        columns.append(tree_widget.headerItem().text(i))
    settings.setValue("columns", json.dumps(columns))

def load_column_config(tree_widget, settings):
    """Load the saved column configuration for QTreeWidget."""
    columns = settings.value("columns")
    if columns:
        columns = json.loads(columns)
        tree_widget.setColumnCount(len(columns))
        tree_widget.setHeaderLabels(columns)