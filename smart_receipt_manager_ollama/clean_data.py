# clean_data.py

def clean_numbers(data):
    """
    Step 1: Generic cleaning.
    Converts numeric strings to floats and protects 8-digit IDs.
    """
    cleaned_data = []
    
    for row in data:
        new_row = []
        for cell in row:
            cell_str = str(cell).strip()
            
            # --- PROTECT 8-DIGIT IDs ---
            # If length is exactly 8 and all numeric, keep as string (e.g., YYYYMMDD)
            if len(cell_str) == 8 and cell_str.isdigit():
                new_row.append(cell_str)
                continue

            # Keep as text if characters are present
            if any(c.isalpha() for c in cell_str):
                new_row.append(cell_str)
            else:
                # Attempt numeric conversion
                try:
                    # Replace comma with dot
                    temp_val = cell_str.replace(",", ".")
                    
                    # Handle leading/trailing minus signs
                    if temp_val.endswith("-"):
                        temp_val = "-" + temp_val[:-1]
                    
                    if temp_val:
                        new_row.append(float(temp_val))
                    else:
                        new_row.append(cell_str)
                    
                except (ValueError, TypeError):
                    new_row.append(cell)
                    
        cleaned_data.append(new_row)

    print("Step 1: Data cleaned (Numbers converted to Float, IDs protected).")
    return cleaned_data


def consolidate_items(data_rows):
    """
    Step 2: Aggregation & Integer fixing.
    Merges items with identical Name and Price, then sums quantity.
    """
    if not data_rows:
        return []

    # Separate Header from Data
    header = data_rows[0]
    items = data_rows[1:]
    
    aggregated = {}
    order_list = [] # Preserves original receipt order

    for row in items:
        if len(row) < 5: 
            continue

        r_id = row[0]
        name = row[1]
        price = row[2]
        qty = row[3]
        cat = row[4]

        # Group by Name and Price
        key = (name, price)

        if key in aggregated:
            try:
                current_qty = float(aggregated[key]['count'])
                add_qty = float(qty)
                aggregated[key]['count'] = current_qty + add_qty
            except ValueError:
                pass 
        else:
            try:
                initial_qty = float(qty)
            except ValueError:
                initial_qty = 1.0
            
            aggregated[key] = {
                'count': initial_qty,
                'id': r_id,
                'cat': cat
            }
            order_list.append(key)

    # Reconstruct the list
    final_data = [header]
    
    for key in order_list:
        name, price = key
        data = aggregated[key]
        
        # Convert float sum to integer
        final_qty = int(data['count'])
        
        # Build row in original order
        new_row = [
            data['id'],   # 0: ID
            name,         # 1: Name
            price,        # 2: Price
            final_qty,    # 3: Quantity
            data['cat']   # 4: Category
        ]
        final_data.append(new_row)

    print(f"Step 2: Consolidation complete. Rows: {len(items)} -> {len(final_data)-1}.")
    return final_data