from PySide6.QtWidgets import QTableWidget

class CustomTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom behavior here