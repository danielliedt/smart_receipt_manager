# File: ui_components.py
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal

class DragDropArea(QLabel):
    """
    Custom widget for file drops.
    Emits 'files_dropped' with a list of valid file paths.
    """
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__("Drag & Drop Files\n(PDF, JPG, PNG)")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        # Component styling
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                font-size: 16px;
                color: #555;
                background-color: #f9f9f9;
                min-height: 150px;
            }
            QLabel:hover {
                background-color: #e2e6ea;
                border-color: #3498db;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        
        # Filter for supported file extensions
        allowed_ext = ('.pdf', '.png', '.jpg', '.jpeg')
        valid_files = [f for f in files if f.lower().endswith(allowed_ext)]
        
        if valid_files:
            self.files_dropped.emit(valid_files)