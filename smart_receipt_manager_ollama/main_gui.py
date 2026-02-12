# File: main_gui.py
import sys
import os

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QStackedWidget, 
                             QLabel, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import custom modules
from ui_components import DragDropArea
from worker import ReceiptWorker
from processed_page import ProcessedPage
from table_page import ReceiptTablePage
from statistics_page import StatisticsPage

from path_config import INPUT_FOLDER

class ReceiptManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Receipt Manager")
        self.resize(1000, 600)

        # Main Container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Horizontal Layout: [Sidebar] | [Content]
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_content_area()

    def setup_sidebar(self):
        """Left navigation bar."""
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(80)
        self.sidebar_widget.setStyleSheet("background-color: #2c3e50;")
        
        layout = QVBoxLayout(self.sidebar_widget)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(20)

        # Navigation Buttons
        buttons_config = [
            ("➕", "Add Receipts", 0),
            ("📂", "Processed Files", 1),
            ("📄", "Data Table", 2),
            ("📊", "Statistics", 3)
        ]

        for icon_text, tooltip, index in buttons_config:
            btn = QPushButton(icon_text)
            btn.setToolTip(tooltip)
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 24px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    border-radius: 5px;
                }
            """)
            btn.clicked.connect(lambda checked, idx=index: self.on_nav_button_clicked(idx))
            layout.addWidget(btn)

        layout.addStretch()
        self.main_layout.addWidget(self.sidebar_widget)

    def setup_content_area(self):
        """Right content area with stacked pages."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Header with Settings
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.btn_theme = QPushButton("Darkmode: ON")
        top_bar.addWidget(self.btn_theme)
        right_layout.addLayout(top_bar)

        # Stacked Pages
        self.pages = QStackedWidget()
        
        # Page 0: Add Receipts
        self.page_add = self.create_add_receipts_page()
        self.pages.addWidget(self.page_add)

        # Page 1: Processed Files
        self.page_processed = ProcessedPage()
        self.pages.addWidget(self.page_processed)

        # Page 2: Data Table
        self.page_table = ReceiptTablePage()
        self.pages.addWidget(self.page_table)

        # Page 3: Statistics
        self.page_stats = StatisticsPage()
        self.pages.addWidget(self.page_stats)

        right_layout.addWidget(self.pages)
        self.main_layout.addWidget(right_widget)

    def create_add_receipts_page(self):
        """Builds the layout for the main processing page."""
        page = QWidget()
        layout = QVBoxLayout(page)

        # 1. Drag & Drop Zone
        self.drop_area = DragDropArea()
        self.drop_area.files_dropped.connect(self.add_files_to_list)
        layout.addWidget(self.drop_area)

        # 2. File List
        self.file_list = QListWidget()
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.file_list.setFont(font)
        layout.addWidget(self.file_list)

        # 3. Action Buttons (Side by Side)
        btn_layout = QHBoxLayout()

        # Import Button
        self.btn_import = QPushButton("Import & Convert")
        self.btn_import.setFixedHeight(45)
        self.btn_import.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; font-weight: bold; border-radius: 5px; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.btn_import.clicked.connect(self.start_import)
        self.btn_import.setEnabled(False)
        btn_layout.addWidget(self.btn_import)

        # Process Button
        self.btn_process = QPushButton("Start Processing")
        self.btn_process.setFixedHeight(45)
        self.btn_process.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; border-radius: 5px; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.btn_process.clicked.connect(self.start_processing)
        self.btn_process.setEnabled(False)
        btn_layout.addWidget(self.btn_process)

        layout.addLayout(btn_layout)
        return page

    # --- LOGIC & WORKFLOW ---

    def on_nav_button_clicked(self, index):
        self.switch_page(index)

        if index == 1:
            self.page_processed.load_headers()
        elif index == 2:
            self.page_table.load_data()
        elif index == 3:
            self.page_stats.refresh_stats() # Recalculate statistics

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    def add_files_to_list(self, file_paths):
        """Adds dropped files to the list with 'raw' status."""
        for path in file_paths:
            file_name = os.path.basename(path)
            
            # Prevent visual duplicates
            exists = False
            for i in range(self.file_list.count()):
                if file_name in self.file_list.item(i).text():
                    exists = True
                    break
            
            if not exists:
                # Status: [Raw] [Unprocessed]
                display_text = f"⬜ ⬜   {file_name}"
                item = QListWidgetItem(display_text)
                
                # Store the FULL source path hidden in the item
                item.setData(Qt.ItemDataRole.UserRole, path)
                
                self.file_list.addItem(item)
        
        self.update_button_states()

    def update_button_states(self):
        """Enable buttons based on item status."""
        has_raw = False
        has_imported = False

        for i in range(self.file_list.count()):
            text = self.file_list.item(i).text()
            if text.startswith("⬜ ⬜"):
                has_raw = True
            if text.startswith("✅ ⬜"):
                has_imported = True

        self.btn_import.setEnabled(has_raw)
        self.btn_process.setEnabled(has_imported)

    def start_import(self):
        """Collect raw files and start worker."""
        items_to_import = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.text().startswith("⬜ ⬜"):
                items_to_import.append((i, item.data(Qt.ItemDataRole.UserRole)))
        
        if items_to_import:
            self.run_worker("import", items_to_import)

    def start_processing(self):
        """Collect imported files and start processing."""
        items_to_process = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.text().startswith("✅ ⬜"):
                items_to_process.append((i, item.data(Qt.ItemDataRole.UserRole)))
        
        if items_to_process:
            self.run_worker("process", items_to_process)

    def run_worker(self, task_type, items):
        """Initialize and start the worker thread."""
        # Lock UI during execution
        self.btn_import.setEnabled(False)
        self.btn_process.setEnabled(False)
        self.drop_area.setEnabled(False)

        self.worker = ReceiptWorker(task_type, items, INPUT_FOLDER)
        self.worker.item_updated.connect(self.on_item_updated)
        self.worker.finished_all.connect(self.on_worker_finished)
        self.worker.start()

    def on_item_updated(self, row_index, new_text, new_path):
        """Triggered when a single file is finished."""
        item = self.file_list.item(row_index)
        item.setText(new_text)
        item.setData(Qt.ItemDataRole.UserRole, new_path)

    def on_worker_finished(self):
        """Triggered when batch is finished."""
        self.drop_area.setEnabled(True)
        self.update_button_states()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReceiptManagerGUI()
    window.show()
    sys.exit(app.exec())