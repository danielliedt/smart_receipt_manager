import csv
from datetime import datetime

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QListWidget, QHeaderView, 
                             QSplitter, QLabel, QAbstractItemView, QPushButton,
                             QComboBox, QMessageBox)
from PyQt6.QtCore import Qt

# Custom configuration imports
import rules_config 
from path_config import CSV_FOLDER

# --- HELPER CLASS FOR NUMERIC PRICE SORTING ---
class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            val1 = float(self.text().replace('€', '').replace(',', '.').strip())
            val2 = float(other.text().replace('€', '').replace(',', '.').strip())
            return val1 < val2
        except ValueError:
            return super().__lt__(other)

class ReceiptTablePage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_by_month = {}
        self.is_editing = False # Status flag for Edit Mode
        self.setup_ui()
        self.load_data() 

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- LEFT: Sidebar ---
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #2c3e50;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_months = QLabel("📅   History")
        lbl_months.setStyleSheet("""
            background-color: #34495e; color: white; font-weight: bold; 
            padding: 12px; font-size: 14px;
        """)
        left_layout.addWidget(lbl_months)

        self.month_list = QListWidget()
        self.month_list.setStyleSheet("""
            QListWidget { border: none; background-color: #2c3e50; color: white; font-size: 13px; outline: none; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #34495e; }
            QListWidget::item:selected { background-color: #3498db; color: white; font-weight: bold; border-left: 4px solid white; }
            QListWidget::item:hover { background-color: #3e5871; }
        """)
        self.month_list.itemClicked.connect(self.on_month_clicked)
        left_layout.addWidget(self.month_list)
        splitter.addWidget(left_widget)

        # --- RIGHT: Content Area ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # -- Toolbar --
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #ddd;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        self.btn_edit = QPushButton("✏️ Edit Mode")
        self.btn_edit.setCheckable(True) 
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0; border: 1px solid #ccc; 
                padding: 5px 15px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:checked {
                background-color: #27ae60; color: white; border: 1px solid #219150;
            }
        """)
        self.btn_edit.clicked.connect(self.toggle_edit_mode)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_edit)
        right_layout.addWidget(toolbar)

        # -- Table --
        self.table = QTableWidget()
        columns = ["Day - Time", "Item", "Price", "Qty", "Category", "Store"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff; color: #000000;
                gridline-color: #eeeeee;
                selection-background-color: #3498db; selection-color: #ffffff;
            }
            QTableWidget::item { color: #000000; padding: 5px; }
            QHeaderView::section {
                background-color: #f0f0f0; color: #000000;
                padding: 5px; border: none; font-weight: bold;
            }
        """)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        right_layout.addWidget(self.table)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([220, 780])
        splitter.setCollapsible(0, False)
        layout.addWidget(splitter)

    def load_data(self):
        """Loads headers and items from CSVs and groups them by month."""
        self.data_by_month = {}
        self.month_list.clear()
        
        if not CSV_FOLDER.exists(): return

        # 1. Load Header Map for metadata
        header_map = {}
        for header_file in CSV_FOLDER.glob("header_*.csv"):
            try:
                with open(header_file, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rid = row.get('receipt_id')
                        if rid:
                            header_map[rid] = {
                                'date': str(row.get('date', '')).split('.')[0],
                                'time': str(row.get('time', '')).split('.')[0],
                                'store': row.get('store_name')
                            }
            except: pass

        # 2. Load Item data
        for item_file in CSV_FOLDER.glob("items_*.csv"):
            try:
                with open(item_file, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rid = row.get('receipt_id')
                        meta = header_map.get(rid)
                        
                        date_str = meta['date'] if meta else "19700101"
                        time_str = meta['time'] if meta else "0000"
                        store_name = meta['store'] if meta else "Unknown"

                        try:
                            if len(date_str) == 8:
                                dt = datetime.strptime(date_str, "%Y%m%d")
                                month_key = dt.strftime("%B %Y")
                                clean_time = time_str.zfill(4) 
                                formatted_time = f"{clean_time[:2]}.{clean_time[2:]}"
                                day_time_display = f"{dt.day:02d} - {formatted_time}"
                            else: raise ValueError
                        except:
                            month_key = "Unknown Date"
                            day_time_display = "??"

                        item_data = {
                            'display': (day_time_display, row.get('item_name'), row.get('unit_price'), 
                                        row.get('quantity'), row.get('category'), store_name),
                            'hidden': {
                                'receipt_id': rid,
                                'source_file': str(item_file),
                                'original_name': row.get('item_name')
                            }
                        }

                        if month_key not in self.data_by_month:
                            self.data_by_month[month_key] = []
                        self.data_by_month[month_key].append(item_data)

            except Exception as e: print(f"Error loading {item_file}: {e}")

        # 3. Populate Sidebar
        sorted_months = sorted(
            self.data_by_month.keys(),
            key=lambda d: datetime.strptime(d, "%B %Y") if d != "Unknown Date" else datetime.min,
            reverse=True
        )
        for m in sorted_months: self.month_list.addItem(m)
        
        if self.month_list.count() > 0:
            self.month_list.setCurrentRow(0)
            self.on_month_clicked(self.month_list.item(0))

    def on_month_clicked(self, item):
        self.current_month = item.text()
        if self.current_month not in self.data_by_month: return

        if self.is_editing:
            self.btn_edit.setChecked(False)
            self.toggle_edit_mode()

        rows = self.data_by_month[self.current_month]
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.table.setRowCount(len(rows))
        
        for row_idx, data_dict in enumerate(rows):
            data = data_dict['display']
            hidden = data_dict['hidden']

            for col_idx, value in enumerate(data):
                if col_idx == 2 or col_idx == 3:
                    table_item = NumericTableWidgetItem(str(value))
                else:
                    table_item = QTableWidgetItem(str(value))
                
                if col_idx == 1: 
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                else:
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if col_idx == 2:
                    try:
                        f_price = float(str(value).replace(',', '.'))
                        table_item.setText(f"{f_price:.2f} €")
                    except: pass

                # Read-Only by default
                table_item.setFlags(table_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                
                # Store metadata in Column 0 UserRole
                if col_idx == 0:
                    table_item.setData(Qt.ItemDataRole.UserRole, hidden)

                self.table.setItem(row_idx, col_idx, table_item)

        self.table.setSortingEnabled(True)

    def toggle_edit_mode(self):
        """Switches between view mode and live editing mode."""
        self.is_editing = self.btn_edit.isChecked()
        
        if self.is_editing:
            self.btn_edit.setText("💾 Save Changes")
            self.table.setSortingEnabled(False) 
        else:
            self.save_changes() 
            self.btn_edit.setText("✏️ Edit Mode")
            self.table.setSortingEnabled(True)

        for row in range(self.table.rowCount()):
            # Make specific columns editable
            for col in [1, 2, 3]:
                item = self.table.item(row, col)
                if self.is_editing:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    if col == 2: item.setText(item.text().replace(' €', ''))
                else:
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)

            # Column 4: Category Selection via ComboBox
            if self.is_editing:
                current_cat = self.table.item(row, 4).text()
                combo = QComboBox()
                cats = rules_config.CATEGORIES.copy()
                if "UNCATEGORIZED" not in cats: cats.append("UNCATEGORIZED")
                combo.addItems(cats)
                combo.setCurrentText(current_cat)
                self.table.setCellWidget(row, 4, combo)

    def save_changes(self):
        """Extracts data from the table and persists it to CSV."""
        updates_by_file = {} 

        for row in range(self.table.rowCount()):
            hidden = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if not hidden: continue

            source_file = hidden['source_file']
            receipt_id = hidden['receipt_id']
            original_name = hidden['original_name']

            new_name = self.table.item(row, 1).text()
            
            try:
                price_text = self.table.item(row, 2).text().replace(',', '.')
                new_price = float(price_text)
            except ValueError:
                QMessageBox.warning(self, "Input Error", f"Invalid price in row {row+1}")
                return

            try:
                qty_text = self.table.item(row, 3).text()
                new_qty = int(float(qty_text))
            except ValueError:
                QMessageBox.warning(self, "Input Error", f"Invalid quantity in row {row+1}")
                return

            # Extract value from combo before destroying it
            combo = self.table.cellWidget(row, 4)
            if combo:
                new_cat = combo.currentText()
                self.table.removeCellWidget(row, 4)
                self.table.item(row, 4).setText(new_cat)
            else:
                new_cat = self.table.item(row, 4).text()

            if source_file not in updates_by_file:
                updates_by_file[source_file] = []
            
            updates_by_file[source_file].append({
                'id': receipt_id,
                'orig_name': original_name,
                'new_name': new_name,
                'price': new_price,
                'qty': new_qty,
                'cat': new_cat
            })

        # Commit updates to CSV
        success_count = 0
        for file_path, updates in updates_by_file.items():
            if self.update_csv_file(file_path, updates):
                success_count += 1
        
        self.load_data() 
        print(f"Updates saved to {success_count} files.")

    def update_csv_file(self, file_path, updates):
        """Helper to safely rewrite a single CSV file with updated values."""
        try:
            temp_rows = []
            updated_flags = [False] * len(updates)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header: temp_rows.append(header)
                
                for row in reader:
                    if len(row) < 5: 
                        temp_rows.append(row)
                        continue

                    r_id = row[0]
                    r_name = row[1]
                    
                    matched = False
                    for i, up in enumerate(updates):
                        if up['id'] == r_id and up['orig_name'] == r_name and not updated_flags[i]:
                            new_row = [r_id, up['new_name'], str(up['price']), str(up['qty']), up['cat']]
                            temp_rows.append(new_row)
                            updated_flags[i] = True 
                            matched = True
                            break
                    
                    if not matched:
                        temp_rows.append(row)

            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(temp_rows)
            
            return True
        except Exception as e:
            print(f"Error saving CSV {file_path}: {e}")
            return False