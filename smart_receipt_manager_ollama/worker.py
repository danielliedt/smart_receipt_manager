# File: worker.py
import time
import shutil
from pathlib import Path
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal

# Import core processing logic from main
import main as logic_processor 

class ReceiptWorker(QThread):
    item_updated = pyqtSignal(int, str, str) 
    finished_all = pyqtSignal()

    def __init__(self, task_type, items_to_process, target_folder):
        super().__init__()
        self.task_type = task_type
        self.items = items_to_process
        self.target_folder = Path(target_folder)

    def run(self):
        if self.task_type == "import":
            self.run_import_task()
        elif self.task_type == "process":
            self.run_process_task() # Core logic execution
        
        self.finished_all.emit()

    def run_import_task(self):
        """Copies files to the local target folder and converts images to PDF."""
        self.target_folder.mkdir(parents=True, exist_ok=True)

        for row, source_path_str in self.items:
            source_path = Path(source_path_str)
            
            try:
                # Determine target filename
                if source_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    target_name = source_path.stem + ".pdf"
                    is_image = True
                else:
                    target_name = source_path.name
                    is_image = False
                
                target_path = self.target_folder / target_name

                # Copy or Convert
                if is_image:
                    image = Image.open(source_path)
                    image = image.convert('RGB')
                    image.save(target_path)
                else:
                    # Overwrite if file already exists
                    shutil.copy2(source_path, target_path)

                # GUI Update: First step completed
                new_display_text = f"✅ ⬜   {target_name}"
                self.item_updated.emit(row, new_display_text, str(target_path))
                
                time.sleep(0.1) # Visual feedback delay

            except Exception as e:
                print(f"Import Error: {e}")

    def run_process_task(self):
        """Invokes the offline main.py logic for each file."""
        
        for row, file_path_str in self.items:
            try:
                # 1. Execute processing function from main.py
                # Steps: Scan -> Clean -> AI Categorization -> CSV Export -> Move
                logic_processor.process_single_file(file_path_str)
                
                # 2. Update path to the new processed location
                filename = Path(file_path_str).name
                processed_path = logic_processor.PROCESSED_FOLDER / filename
                
                # 3. GUI Update: Full processing completed
                new_display_text = f"✅ ✅   {filename}"
                self.item_updated.emit(row, new_display_text, str(processed_path))

            except Exception as e:
                print(f"CRITICAL PROCESS ERROR: {e}")
                # Optional: Indicate error in GUI
                self.item_updated.emit(row, f"✅ ❌   Error: {str(e)}", file_path_str)