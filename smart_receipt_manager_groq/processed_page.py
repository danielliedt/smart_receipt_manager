import csv
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QAbstractItemView, QLabel)
from PyQt6.QtCore import Qt

from path_config import CSV_FOLDER

# --- HELPERS FOR CORRECT SORTING ---

class SortableDateItem(QTableWidgetItem):
    """Sorts dates in DD.MM.YYYY format chronologically."""
    def __lt__(self, other):
        try:
            date1 = datetime.strptime(self.text(), "%d.%m.%Y")
            date2 = datetime.strptime(other.text(), "%d.%m.%Y")
            return date1 < date2
        except:
            return super().__lt__(other)

class SortablePriceItem(QTableWidgetItem):
    """Sorts prices (1.99 €) numerically."""
    def __lt__(self, other):
        try:
            val1 = float(self.text().replace('€', '').replace(',', '.').strip())
            val2 = float(other.text().replace('€', '').replace(',', '.').strip())
            return val1 < val2
        except:
            return super().__lt__(other)

# --- MAIN CLASS ---

class ProcessedPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_headers()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_title = QLabel("📂 Processed Receipts Archive")
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(self.lbl_title)

        self.table = QTableWidget()
        columns = ["Date", "Time", "Store", "Total Sum", "Filename / ID"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Enable sorting via header click
        self.table.setSortingEnabled(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff; color: #000000;
                gridline-color: #eeeeee;
                selection-background-color: #3498db; selection-color: #ffffff;
            }
            QTableWidget::item { color: #000000; padding: 5px; }
            QHeaderView::section {
                background-color: #f0f0f0; color: #000000;
                padding: 8px; border: none; font-weight: bold;
            }
        """)
        
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

    def load_headers(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        all_receipts = []
        if not CSV_FOLDER.exists():
            return

        for header_file in CSV_FOLDER.glob("header_*.csv"):
            try:
                with open(header_file, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Ensure string format
                        raw_date = str(row.get('date', '00000000')).split('.')[0]
                        raw_time = str(row.get('time', '0000')).split('.')[0].zfill(4)
                        
                        # Format date (safety check)
                        if len(raw_date) == 8 and raw_date != "00000000":
                            fmt_date = f"{raw_date[6:8]}.{raw_date[4:6]}.{raw_date[0:4]}"
                        else:
                            fmt_date = "00.00.0000"
                        
                        fmt_time = f"{raw_time[:2]}:{raw_time[2:]}"
                        
                        all_receipts.append([
                            fmt_date,
                            fmt_time,
                            row.get('store_name', 'UNKNOWN'),
                            f"{float(row.get('total_sum', 0)):.2f} €",
                            f"{row.get('receipt_id', 'UNKNOWN')}.pdf"
                        ])
            except Exception as e:
                print(f"Error reading header file {header_file}: {e}")

        # --- CRASH-SAFE SORTING ---
        def safe_sort_key(x):
            try:
                return datetime.strptime(x[0], "%d.%m.%Y")
            except:
                return datetime.min # Push invalid dates to the bottom

        all_receipts.sort(key=safe_sort_key, reverse=True)

        self.table.setRowCount(len(all_receipts))
        for row_idx, data in enumerate(all_receipts):
            for col_idx, value in enumerate(data):
                if col_idx == 0:
                    item = SortableDateItem(str(value))
                elif col_idx == 3:
                    item = SortablePriceItem(str(value))
                else:
                    item = QTableWidgetItem(str(value))
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.table.setSortingEnabled(True)