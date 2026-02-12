# File: settings_page.py
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from path_config import SETTINGS_FILE

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Groq API Key:"))
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password) # Mask API key as a password
        self.key_input.setPlaceholderText("gsk_...")
        
        # Load existing key
        current_key = self.load_key()
        if current_key:
            self.key_input.setText(current_key)
            
        layout.addWidget(self.key_input)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(save_btn)
        
        layout.addStretch() # Push elements to top

    def load_key(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f).get("groq_key", "")
            except: return ""
        return ""

    def save_settings(self):
        new_key = self.key_input.text().strip()
        data = {"groq_key": new_key}
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f)
        QMessageBox.information(self, "Saved", "API key saved successfully!")
