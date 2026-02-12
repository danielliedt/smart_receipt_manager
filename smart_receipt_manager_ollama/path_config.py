# File: path_config.py
import os
import sys
from pathlib import Path

def get_base_dir():
    """Locates the Documents folder, supporting both OneDrive and local paths."""
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

# Automatically create directories
for folder in [INPUT_FOLDER, PROCESSED_FOLDER, CSV_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

# --- TESSERACT PATH & LOGIC (EXE COMPATIBILITY) ---
if getattr(sys, 'frozen', False):
    # Running as EXE: Use temporary bundle folder
    bundle_dir = Path(sys._MEIPASS)
else:
    # Running as script: Use project folder
    bundle_dir = Path(__file__).parent

# Path to Tesseract executable
TESSERACT_EXE = bundle_dir / "tesseract_bin" / "tesseract.exe"

# IMPORTANT: Define location of language data to prevent OCR errors
os.environ["TESSDATA_PREFIX"] = str(bundle_dir / "tesseract_bin" / "tessdata")

print(f"Paths initialized at: {BASE_DIR}")