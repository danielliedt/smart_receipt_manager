# File: statistics_page.py
import csv
from datetime import datetime

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Custom paths
from path_config import CSV_FOLDER

class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_stats()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f5f5f5; }")
        
        self.container = QWidget()
        self.content_layout = QVBoxLayout(self.container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(30)

        # --- 1. KPI Cards ---
        kpi_layout = QHBoxLayout()
        self.card_total = self.create_kpi_card("Total Spending", "0.00 €")
        self.card_month = self.create_kpi_card("This Month", "0.00 €")
        self.card_avg = self.create_kpi_card("Avg per Receipt", "0.00 €")
        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_month)
        kpi_layout.addWidget(self.card_avg)
        self.content_layout.addLayout(kpi_layout)

        # --- 2. Pie Chart & Legend ---
        pie_section = QFrame()
        pie_section.setMinimumHeight(450)
        pie_section.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #ddd;")
        pie_h_layout = QHBoxLayout(pie_section)
        
        self.canvas_pie = FigureCanvas(Figure(figsize=(5, 5)))
        self.ax_pie = self.canvas_pie.figure.add_subplot(111)
        pie_h_layout.addWidget(self.canvas_pie, stretch=3)
        
        self.legend_list = QListWidget()
        self.legend_list.setMaximumWidth(250)
        self.legend_list.setStyleSheet("border: none; background: #f9f9f9; color: #2c3e50; font-size: 12px;")
        pie_h_layout.addWidget(self.legend_list, stretch=1)
        
        self.content_layout.addWidget(QLabel("<b>Expense Distribution (%)</b>"))
        self.content_layout.addWidget(pie_section)

        # --- 3. Horizontal Bar Chart ---
        cat_bar_section = QFrame()
        cat_bar_section.setMinimumHeight(500)
        cat_bar_section.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #ddd;")
        cat_bar_layout = QVBoxLayout(cat_bar_section)
        self.canvas_cat_bar = FigureCanvas(Figure(figsize=(8, 6)))
        self.ax_cat_bar = self.canvas_cat_bar.figure.add_subplot(111)
        cat_bar_layout.addWidget(self.canvas_cat_bar)
        self.content_layout.addWidget(QLabel("<b>Spending per Category (€)</b>"))
        self.content_layout.addWidget(cat_bar_section)

        # --- 4. Monthly Trend ---
        trend_section = QFrame()
        trend_section.setMinimumHeight(400)
        trend_section.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #ddd;")
        trend_layout = QVBoxLayout(trend_section)
        self.canvas_bar = FigureCanvas(Figure(figsize=(8, 4)))
        self.ax_bar = self.canvas_bar.figure.add_subplot(111)
        trend_layout.addWidget(self.canvas_bar)
        self.content_layout.addWidget(QLabel("<b>Monthly Trend</b>"))
        self.content_layout.addWidget(trend_section)

        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)

    def create_kpi_card(self, title, value):
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px; padding: 15px;")
        layout = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8c8d; font-size: 11px; font-weight: bold; border: none;")
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: #2c3e50; font-size: 18px; font-weight: bold; border: none;")
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        frame.value_label = lbl_value
        return frame

    def refresh_stats(self):
        total_sum_overall = 0.0
        month_sum = 0.0
        receipt_count = 0
        category_data = {} 
        monthly_data = {}  
        current_month_str = datetime.now().strftime("%Y%m")

        if not CSV_FOLDER.exists(): return

        # 1. Process header data
        for f in CSV_FOLDER.glob("header_*.csv"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Filter invalid IDs
                        if row['receipt_id'].startswith("0000"): continue
                        amount = float(row['total_sum'])
                        date_raw = str(row['date']).split('.')[0]
                        if len(date_raw) == 8:
                            total_sum_overall += amount
                            receipt_count += 1
                            month_key = date_raw[:6]
                            monthly_data[month_key] = monthly_data.get(month_key, 0) + amount
                            if month_key == current_month_str: month_sum += amount
            except: pass

        # 2. Process item data
        for f in CSV_FOLDER.glob("items_*.csv"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        try:
                            line_sum = float(row['unit_price']) * float(row['quantity'])
                            cat = row['category']
                            category_data[cat] = category_data.get(cat, 0) + line_sum
                        except: pass
            except: pass

        # Update KPIs
        self.card_total.value_label.setText(f"{total_sum_overall:.2f} €")
        self.card_month.value_label.setText(f"{month_sum:.2f} €")
        avg = total_sum_overall / receipt_count if receipt_count > 0 else 0
        self.card_avg.value_label.setText(f"{avg:.2f} €")

        # Color management
        sorted_cats_desc = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        cmap = plt.get_cmap('tab20')
        color_map = {cat[0]: cmap(i % 20) for i, cat in enumerate(sorted_cats_desc)}

        # Update Pie Chart
        self.ax_pie.clear()
        self.legend_list.clear()
        if category_data:
            values = [x[1] for x in sorted_cats_desc]
            labels = [x[0] for x in sorted_cats_desc]
            colors = [color_map[l] for l in labels]
            self.ax_pie.pie(values, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.8)
            for cat, val in sorted_cats_desc:
                c = color_map[cat]
                hex_c = '#%02x%02x%02x' % (int(c[0]*255), int(c[1]*255), int(c[2]*255))
                item = QListWidgetItem(f"{cat}: {val:.2f} €")
                item.setIcon(self.create_color_icon(hex_c))
                self.legend_list.addItem(item)
        self.canvas_pie.figure.tight_layout()
        self.canvas_pie.draw()

        # Update Category Bar Chart
        self.ax_cat_bar.clear()
        if category_data:
            sorted_asc = sorted(category_data.items(), key=lambda x: x[1], reverse=False)
            l_asc = [x[0] for x in sorted_asc]
            v_asc = [x[1] for x in sorted_asc]
            c_asc = [color_map[l] for l in l_asc]
            self.ax_cat_bar.barh(l_asc, v_asc, color=c_asc)
            self.ax_cat_bar.set_title("Spending per Category (€)")
        self.canvas_cat_bar.figure.tight_layout()
        self.canvas_cat_bar.draw()

        # Update Monthly Trend
        self.ax_bar.clear()
        if monthly_data:
            sorted_m = sorted(monthly_data.keys())
            d_m = [datetime.strptime(m, "%Y%m").strftime("%b %y") for m in sorted_m]
            v_m = [monthly_data[m] for m in sorted_m]
            self.ax_bar.bar(d_m, v_m, color='#3498db')
        self.canvas_bar.figure.tight_layout()
        self.canvas_bar.draw()

    def create_color_icon(self, hex_color):
        from PyQt6.QtGui import QPixmap, QColor, QIcon
        pixmap = QPixmap(12, 12)
        pixmap.fill(QColor(hex_color))
        return QIcon(pixmap)
