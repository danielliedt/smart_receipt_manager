# Smart Receipt V1 - Logic Module
import shutil
from pathlib import Path

# Custom modules
import read_receipt
import clean_data
import database_manager
from categorizer import ProductCategorizer
from path_config import INPUT_FOLDER, PROCESSED_FOLDER, BASE_DIR

# Initialize AI instance once
print("... Initializing AI Categorizer (Lazy Load) ...")
ai_boss = ProductCategorizer()

def process_single_file(file_path_str):
    """
    Process a single file: Scan -> Clean -> Filter -> AI -> Save -> Move
    """
    file_path = Path(file_path_str)
    
    if not file_path.exists():
        return "Error: File not found"

    print(f"--- Processing: {file_path.name} ---")

    # 1. Scan
    header_raw, items_raw = read_receipt.scan_receipt(str(file_path))
    
    # 2. Clean data (Applying the 8-digit rule for IDs)
    header_cleaned = clean_data.clean_numbers(header_raw)
    items_cleaned = clean_data.clean_numbers(items_raw)
    
    # 3. Consolidate
    final_data = clean_data.consolidate_items(items_cleaned)

    # --- VALIDATION ---
    # Verify if ID is valid. Discard "00000000" or "UNKNOWN".
    extracted_id = header_cleaned[1][0] if len(header_cleaned) > 1 else "UNKNOWN"
    
    if "UNKNOWN" in str(extracted_id) or str(extracted_id).startswith("0000") or len(final_data) <= 1:
        print(f"   [!] ABORT: No valid data found in {file_path.name}.")
        
        # Move failed/empty scans to error folder
        failed_folder = BASE_DIR / "Failed_OCR"
        failed_folder.mkdir(exist_ok=True)
        shutil.move(str(file_path), str(failed_folder / file_path.name))
        return "Failed: No data recognized"

    # 4. AI Categorization
    for row in final_data[1:]:
        item_name = row[1]
        if item_name:
            category, confidence = ai_boss.get_category(item_name)
            if confidence < 0.75:
                row[4] = "UNCATEGORIZED"
            else:
                row[4] = category

    # 5. Save
    database_manager.save_to_csv(header_cleaned, final_data)

    # 6. Move (Successful)
    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    destination = PROCESSED_FOLDER / file_path.name
    
    if destination.exists():
        destination.unlink() 
        
    shutil.move(str(file_path), str(destination))
    return "Processed & Moved ✅"

if __name__ == "__main__":
    for f in INPUT_FOLDER.glob("*.pdf"):
        process_single_file(str(f))