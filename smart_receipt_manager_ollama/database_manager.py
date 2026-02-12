import os
import csv
from path_config import CSV_FOLDER

def save_to_csv(header_data, items_data):
    base_path = CSV_FOLDER

    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    receipt_id = header_data[1][0]
    # Partition files by year and month based on receipt ID
    year = receipt_id[:4] 
    year_month = receipt_id[:6] 

    header_file = os.path.join(base_path, f"header_{year}.csv")

    # Check for duplicate IDs in the header file
    if os.path.isfile(header_file):
        with open(header_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            if any(row and row[0] == receipt_id for row in reader):
                print(f"Skipping: ID {receipt_id} already exists in database.")
                return False

    items_file = os.path.join(base_path, f"items_{year_month}.csv")

    def write_csv(file_path, data):
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header only for new files
            if not file_exists:
                writer.writerow(data[0])

            # Append data rows
            writer.writerows(data[1:]) 
    
    # Save partitioned data
    write_csv(header_file, header_data)
    write_csv(items_file, items_data)

    print(f"Data saved to {header_file} and {items_file}")

    return True