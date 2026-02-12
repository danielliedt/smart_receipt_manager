# File: path_config.py
import os
import sys
from pathlib import Path

def get_base_dir():
    """Locates the documents folder (OneDrive or Local) and initializes the app directory."""
    home = Path.home()
    
    # Priority list for Documents folder
    options = [
        home / "OneDrive" / "Dokumente",
        home / "OneDrive" / "Documents",
        home / "Documents",
        home / "Dokumente"
    ]
    
    docs_folder = home # Absolute fallback
    for opt in options:
        if opt.exists():
            docs_folder = opt
            break
            
    app_dir = docs_folder / "SmartReceipts"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

# --- CENTRAL PATHS ---
BASE_DIR = get_base_dir()

# Define subfolders
INPUT_FOLDER = BASE_DIR / "Input"
PROCESSED_FOLDER = BASE_DIR / "Processed_PDFs"
CSV_FOLDER = BASE_DIR / "CSV_Database"
SETTINGS_FILE = BASE_DIR / "settings.json"

# Automatically create required folders
for folder in [INPUT_FOLDER, PROCESSED_FOLDER, CSV_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

# --- TESSERACT PATH & LOGIC (EXE COMPATIBILITY) ---
if getattr(sys, 'frozen', False):
    # If running as EXE: use the temporary bundle directory
    bundle_dir = Path(sys._MEIPASS)
else:
    # If running as script: use the project directory
    bundle_dir = Path(__file__).parent

# Tesseract executable path
TESSERACT_EXE = bundle_dir / "tesseract_bin" / "tesseract.exe"

# Set TESSDATA_PREFIX to ensure language data files are found
os.environ["TESSDATA_PREFIX"] = str(bundle_dir / "tesseract_bin" / "tessdata")

print(f"Paths initialized at: {BASE_DIR}")
