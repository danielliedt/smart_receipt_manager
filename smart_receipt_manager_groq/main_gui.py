import sys
import os

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QStackedWidget, 
                             QLabel, QListWidget, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Custom modules
from ui_components import DragDropArea
from worker import ReceiptWorker
from processed_page import ProcessedPage
from table_page import ReceiptTablePage
from statistics_page import StatisticsPage
from settings_page import SettingsPage

from path_config import INPUT_FOLDER

class ReceiptManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Receipt Manager v1.5")
        self.resize(1100, 700)

        # Main Container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main Layout: [Sidebar] | [Content Area]
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Initialize UI components
        self.setup_sidebar()
        self.setup_content_area()

    def setup_sidebar(self):
        """Creates the left navigation sidebar."""
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(80)
        self.sidebar_widget.setStyleSheet("background-color: #2c3e50;")
        
        layout = QVBoxLayout(self.sidebar_widget)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(20)

        # Navigation Buttons Definition
        buttons_config = [
            ("➕", "Add Receipts", 0),
            ("📂", "Processed Files", 1),
            ("📄", "Data Table", 2),
            ("📊", "Statistics", 3),
            ("⚙️", "Settings", 4) # Index 4 for Groq Key
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
        """Creates the right content area with switchable pages."""
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(20, 20, 20, 20)

        # Top bar
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        lbl_version = QLabel("v1.5 Cloud")
        lbl_version.setStyleSheet("color: #bdc3c7; font-size: 10px;")
        top_bar.addWidget(lbl_version)
        self.right_layout.addLayout(top_bar)

        # StackedWidget for page management
        self.pages = QStackedWidget()
        
        # --- Page Initialization ---
        
        # Index 0: Add Receipts
        self.page_add = self.create_add_receipts_page()
        self.pages.addWidget(self.page_add)

        # Index 1: Processed Files
        self.page_processed = ProcessedPage()
        self.pages.addWidget(self.page_processed)

        # Index 2: Data Table
        self.page_table = ReceiptTablePage()
        self.pages.addWidget(self.page_table)

        # Index 3: Statistics
        self.page_stats = StatisticsPage()
        self.pages.addWidget(self.page_stats)

        # Index 4: Settings
        self.page_settings = SettingsPage()
        self.pages.addWidget(self.page_settings)

        # --- Final layout assembly ---
        self.right_layout.addWidget(self.pages)
        self.main_layout.addWidget(self.right_widget)

    def create_add_receipts_page(self):
        """Builds the main processing page (drop zone)."""
        page = QWidget()
        layout = QVBoxLayout(page)

        self.drop_area = DragDropArea()
        self.drop_area.files_dropped.connect(self.add_files_to_list)
        layout.addWidget(self.drop_area)

        self.file_list = QListWidget()
        font = QFont("Consolas", 10)
        self.file_list.setFont(font)
        layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()

        self.btn_import = QPushButton("Import & Convert")
        self.btn_import.setFixedHeight(45)
        self.btn_import.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_import.clicked.connect(self.start_import)
        self.btn_import.setEnabled(False)
        btn_layout.addWidget(self.btn_import)

        self.btn_process = QPushButton("Start Processing")
        self.btn_process.setFixedHeight(45)
        self.btn_process.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_process.clicked.connect(self.start_processing)
        self.btn_process.setEnabled(False)
        btn_layout.addWidget(self.btn_process)

        layout.addLayout(btn_layout)
        return page

    # --- LOGIC & NAVIGATION ---

    def on_nav_button_clicked(self, index):
        """Triggered when a sidebar button is clicked."""
        self.pages.setCurrentIndex(index)

        # Refresh data on page change
        if index == 1:
            self.page_processed.load_headers()
        elif index == 2:
            self.page_table.load_data()
        elif index == 3:
            self.page_stats.refresh_stats()

    def add_files_to_list(self, file_paths):
        for path in file_paths:
            file_name = os.path.basename(path)
            exists = False
            for i in range(self.file_list.count()):
                if file_name in self.file_list.item(i).text():
                    exists = True
                    break
            if not exists:
                item = QListWidgetItem(f"⬜ ⬜   {file_name}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.file_list.addItem(item)
        self.update_button_states()

    def update_button_states(self):
        has_raw = any(self.file_list.item(i).text().startswith("⬜ ⬜") for i in range(self.file_list.count()))
        has_imported = any(self.file_list.item(i).text().startswith("✅ ⬜") for i in range(self.file_list.count()))
        self.btn_import.setEnabled(has_raw)
        self.btn_process.setEnabled(has_imported)

    def start_import(self):
        items = [(i, self.file_list.item(i).data(Qt.ItemDataRole.UserRole)) 
                 for i in range(self.file_list.count()) if self.file_list.item(i).text().startswith("⬜ ⬜")]
        if items: self.run_worker("import", items)

    def start_processing(self):
        items = [(i, self.file_list.item(i).data(Qt.ItemDataRole.UserRole)) 
                 for i in range(self.file_list.count()) if self.file_list.item(i).text().startswith("✅ ⬜")]
        if items: self.run_worker("process", items)

    def run_worker(self, task_type, items):
        self.btn_import.setEnabled(False)
        self.btn_process.setEnabled(False)
        self.drop_area.setEnabled(False)
        self.worker = ReceiptWorker(task_type, items, INPUT_FOLDER)
        self.worker.item_updated.connect(self.on_item_updated)
        self.worker.finished_all.connect(self.on_worker_finished)
        self.worker.start()

    def on_item_updated(self, row_index, new_text, new_path):
        item = self.file_list.item(row_index)
        item.setText(new_text)
        item.setData(Qt.ItemDataRole.UserRole, new_path)

    def on_worker_finished(self):
        self.drop_area.setEnabled(True)
        self.update_button_states()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReceiptManagerGUI()
    window.show()
    sys.exit(app.exec())