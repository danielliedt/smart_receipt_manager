# File: worker.py
import time
import shutil
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

# Import core processing logic and paths
import main as logic_processor 
from path_config import TESSERACT_EXE, INPUT_FOLDER
from jpg_png_2_pdf import ReceiptProcessor

class ReceiptWorker(QThread):
    item_updated = pyqtSignal(int, str, str) 
    finished_all = pyqtSignal()

    def __init__(self, task_type, items_to_process, target_folder):
        super().__init__()
        self.task_type = task_type
        self.items = items_to_process
        self.target_folder = Path(target_folder)
        
        # Initialize our OCR processor specifically for the import step
        if self.task_type == "import":
            self.pdf_processor = ReceiptProcessor(TESSERACT_EXE, INPUT_FOLDER)

    def run(self):
        if self.task_type == "import":
            self.run_import_task()
        elif self.task_type == "process":
            self.run_process_task() # Core processing action
        
        self.finished_all.emit()

    def run_import_task(self):
        """Copies files to the Input folder and uses Tesseract to create searchable PDFs."""
        self.target_folder.mkdir(parents=True, exist_ok=True)

        for row, source_path_str in self.items:
            source_path = Path(source_path_str)
            
            try:
                # 1. First, copy the original file to the Input folder
                temp_target_path = self.target_folder / source_path.name
                shutil.copy2(source_path, temp_target_path)

                # 2. Check if it's an image that needs OCR conversion
                if temp_target_path.suffix.lower() in self.pdf_processor.valid_extensions:
                    # Use our robust Tesseract converter to make a readable PDF
                    final_pdf_path = self.pdf_processor._convert_to_searchable_pdf(temp_target_path)
                    
                    if not final_pdf_path:
                        raise Exception("OCR Conversion failed or file locked.")
                else:
                    # It is already a PDF, no conversion needed
                    final_pdf_path = temp_target_path

                target_name = final_pdf_path.name

                # GUI Update: First checkmark
                new_display_text = f"✅ ⬜   {target_name}"
                self.item_updated.emit(row, new_display_text, str(final_pdf_path))
                
                time.sleep(0.1) # Brief visual feedback

            except Exception as e:
                print(f"Import Error: {e}")
                self.item_updated.emit(row, f"❌ ⬜   Error: {str(e)}", source_path_str)

    def run_process_task(self):
        """Invokes logic from main.py for each verified PDF file."""
        for row, file_path_str in self.items:
            try:
                # 1. Start processing (Scan -> Clean -> AI -> CSV -> Move)
                result_msg = logic_processor.process_single_file(file_path_str)
                
                # 2. Adjust path (file has been moved to PROCESSED_FOLDER)
                filename = Path(file_path_str).name
                processed_path = logic_processor.PROCESSED_FOLDER / filename
                
                # 3. GUI Update: Second checkmark & status
                if "Failed" in result_msg or "Error" in result_msg:
                     self.item_updated.emit(row, f"✅ ❌   {filename} (Failed)", file_path_str)
                else:
                     new_display_text = f"✅ ✅   {filename}"
                     self.item_updated.emit(row, new_display_text, str(processed_path))

            except Exception as e:
                print(f"CRITICAL PROCESS ERROR: {e}")
                # Update GUI with error status
                self.item_updated.emit(row, f"✅ ❌   Error: {str(e)}", file_path_str)
