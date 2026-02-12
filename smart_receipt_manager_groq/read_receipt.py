# Purpose: This module reads and processes PDF receipts, extracting structured data.
import re
from pypdf import PdfReader
import rules_config 

def normalize_ocr_text(line: str) -> str:
    """
    Corrects common OCR misinterpretations and standardizes decimal separators.
    """
    replacements = {"€": "", "O": "0", "o": "0", "l": "1", "I": "1"}
    for char, digit in replacements.items():
        if char in ["l", "I", "O", "o"]:
            line = re.sub(r'(?<=[\d,])' + char + r'(?=[\d,])', digit, line)
        else:
            line = line.replace(char, digit)

    # Standardize decimal separator to dot
    line = re.sub(r"(\d),(\d{2})", r"\1.\2", line)
    return line.strip()


def validate_and_fix_math(unit, qty, total):
    """
    Validates Unit Price * Quantity = Total Price. Recalculates unit price if discrepancy exists.
    """
    try:
        u, q, t = float(unit), float(qty), float(total)
        if q == 1.0: 
            return t, q, t
            
        if abs((u * q) - t) > 0.03:
            if q != 0: 
                u = round(t / q, 2)
        return u, q, t
    except (ValueError, ZeroDivisionError):
        return 0.0, 1.0, 0.0


def is_junk_line(line: str) -> bool:
    """
    Filters lines that should not be interpreted as product names.
    """
    line_lower = line.strip().lower()
    if not line_lower: return True

    # Check against junk keywords and store names
    if any(k in line_lower for k in rules_config.JUNK_KEYWORDS): return True
    if line_lower in rules_config.STORE_SHORT_NAMES: return True

    # Deposits/Pfand are never junk
    if any(k in line_lower for k in ["pfand", "leergut"]): return False

    # Filter address patterns and zip codes
    if re.search(r'\d+[-\s/]+\d+', line): return True 
    if re.match(r'^\d{5}\s+', line): return True 
    
    return False


def scan_receipt(file_path):
    """
    Parses PDF to extract header info and line items.
    """
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text: full_text += text + "\n"

    lines = full_text.splitlines()

    # --- Header Extraction ---
    store_name = "UNKNOWN"
    for store in rules_config.STORES:
        if store.lower() in full_text.lower():
            store_name = store.upper()
            break
            
    # Extract date and format to YYYYMMDD
    date_match = re.search(r"\d{2}\.\d{2}\.(?:\d{4}|\d{2})", full_text)
    clean_date = "00000000"
    if date_match:
        d_parts = date_match.group().split(".")
        year = d_parts[2] if len(d_parts[2]) == 4 else f"20{d_parts[2]}"
        clean_date = f"{year}{d_parts[1]}{d_parts[0]}"

    # Extract time
    time_match = re.search(r"\d{2}:\d{2}", full_text)
    clean_time = time_match.group().replace(":", "") if time_match else "0000"

    receipt_id = f"{clean_date}_{clean_time}_{store_name}"

    # Initialize data structures with column headers
    header_data = [["receipt_id", "date", "time", "store_name", "total_sum"]]
    current_header_row = [receipt_id, clean_date, clean_time, store_name, "0.00"]
    
    items_data = [["receipt_id", "item_name", "unit_price", "quantity", "category"]]

    pending_item_name = ""
    
    for raw_line in lines:
        line = normalize_ocr_text(raw_line).strip()
        lower_line = line.lower()

        if not line:
            pending_item_name = "" 
            continue

        # A) Total Sum Detection
        if any(x in lower_line for x in ["summe", "gesamt", "total", "zu zahlen"]):
            prices = re.findall(r"-?\d+\.\d{2}", line)
            if prices: 
                current_header_row[4] = prices[-1]
            pending_item_name = "" 
            continue

        # B) Product Line Detection (Tax Marker A, B, or W)
        tax_match = re.search(r'\s+([ABW])$', line)
        if tax_match:
            content = line[:tax_match.start()].strip()
            all_prices = re.findall(r"-?\d+\.\d{2}", content)
            
            if all_prices:
                total_price = float(all_prices[-1])
                qty_match = re.search(r'(?<![.,])\b(\d+)\s*[x\*]|[x\*]\s*(\d+)\b(?![,.])', content)
                
                quantity = 1.0
                if qty_match:
                    q_str = qty_match.group(1) if qty_match.group(1) else qty_match.group(2)
                    quantity = float(q_str)
                    unit_price = float(all_prices[0]) if len(all_prices) >= 2 else round(total_price / quantity, 2)
                    unit_price, quantity, total_price = validate_and_fix_math(unit_price, quantity, total_price)
                else:
                    unit_price = total_price

                # Clean item name from prices and quantity markers
                clean_name = content
                for p in all_prices: 
                    clean_name = clean_name.replace(p, "")
                clean_name = re.sub(r'(?<![.,])\b\d+\s*[x\*]|[x\*]\s*\d+\b', "", clean_name).strip()

                # Merge with previous line if it was a partial name
                final_name = clean_name
                if pending_item_name and pending_item_name.lower() not in clean_name.lower():
                    final_name = f"{pending_item_name} {clean_name}".strip()
                
                # Normalize deposit naming
                if any(x in final_name.lower() for x in ["pfand", "leergut"]) and "PFAND" not in final_name.upper():
                    final_name = f"PFAND {final_name}".upper()

                items_data.append([receipt_id, final_name.strip(" .,-*"), f"{unit_price:.2f}", f"{int(quantity)}", ""])
                pending_item_name = "" 
                continue

        # C) Buffer Handling: current line might be the first part of a name on the next line
        if is_junk_line(line):
            pending_item_name = "" 
        else:
            pending_item_name = line

    header_data.append(current_header_row)
    
    return header_data, items_data