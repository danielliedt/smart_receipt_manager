import os
from pathlib import Path
import pytesseract
from PIL import Image, ImageOps, ImageEnhance

from path_config import INPUT_FOLDER, TESSERACT_EXE

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)

folder_path = INPUT_FOLDER

# Check for Tesseract executable
if TESSERACT_EXE.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)
else:
    # Fallback safety check for the tesseract_bin folder
    print(f"CRITICAL ERROR: Tesseract not found at {TESSERACT_EXE}")
    print("Please ensure the 'tesseract_bin' folder is in the program directory.")

def process_receipt_folder(folder_path):
    valid_extensions = ('.png', '.jpg', '.jpeg')
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} not found.")
        return

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(valid_extensions):
            image_path = os.path.join(folder_path, filename)
            base_name = os.path.splitext(filename)[0]
            output_pdf_path = os.path.join(folder_path, f"{base_name}.pdf")
            
            try:
                # 1. Open image
                img = Image.open(image_path)
                
                # --- OPTIMIZATION ---
                # Improve image quality for better OCR results
                
                # Step A: Convert to grayscale
                img = ImageOps.grayscale(img)
                
                # Step B: Maximize contrast
                img = ImageOps.autocontrast(img)
                
                # Optional: Sharpening for clarity
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(2.0)
                
                # Convert to searchable PDF
                # --psm 6 forces Tesseract to treat the image as a uniform text block
                pdf_data = pytesseract.image_to_pdf_or_hocr(
                    img, 
                    extension='pdf', 
                    lang='deu', 
                    config='--psm 6' 
                )
                
                with open(output_pdf_path, "wb") as f:
                    f.write(pdf_data)
                
                if os.path.exists(output_pdf_path):
                    img.close()
                    os.remove(image_path)
                    print(f"   [OK] Converted & Optimized: {base_name}.pdf")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")