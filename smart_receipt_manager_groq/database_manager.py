import os
import csv
from path_config import CSV_FOLDER

def save_to_csv(header_data, items_data):
    base_path = CSV_FOLDER

    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    receipt_id = header_data[1][0]
    year = receipt_id[:4] # Extract year for header partitioning
    year_month = receipt_id[:6] # Extract month for item partitioning

    # Define filenames
    header_file = os.path.join(base_path, f"header_{year}.csv")

    # Duplicate Check: Verify if ID already exists in header file
    if os.path.isfile(header_file):
        with open(header_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            if any(row and row[0] == receipt_id for row in reader):
                print(f"Skipping: ID {receipt_id} already exists in database.")
                return False

    items_file = os.path.join(base_path, f"items_{year_month}.csv")

    # Helper function to write/append data to CSV
    def write_csv(file_path, data):
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(data[0]) # Write header only if file is new

            writer.writerows(data[1:]) # Write data rows
    
    # Save header and item data
    write_csv(header_file, header_data)
    write_csv(items_file, items_data)

    print(f"Data saved to {header_file} and {items_file}")

    return True