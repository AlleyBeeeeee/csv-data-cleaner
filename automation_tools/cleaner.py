import csv
import os
import re
from datetime import datetime

def log_event(message):
    """Writes internal tracking logs to a separate file for auditing."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("cleaning_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def clean_name(name):
    """Trims trailing spaces and forces proper Title Case capitalization."""
    return name.strip().title()

def clean_email(email):
    """Strips whitespace, converts to lowercase, and validates email format."""
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    return None

def clean_phone(phone):
    """Removes common formatting characters and returns a clean digit string."""
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    return cleaned if cleaned.isdigit() else "INVALID_PHONE"

def process_csv(input_file, output_file):
    """Reads a business CSV, handles operational exceptions, and audits records."""
    # Reset log file for a fresh execution run
    with open("cleaning_log.txt", "w", encoding="utf-8") as f:
        f.write("--- AUTOMATED DATA CLEANING AUDIT INITIALIZED ---\n")

    if not os.path.exists(input_file):
        error_msg = f"CRITICAL: Source file '{input_file}' not found."
        print(f"[-] {error_msg}")
        log_event(error_msg)
        return

    print(f"[+] Initializing advanced audit on: {input_file}")
    log_event(f"System scanned source file: {input_file}")
    
    cleaned_rows = []
    skipped_count = 0

    try:
        with open(input_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Defensive check: Ensure required business headers exist
            required_headers = ['name', 'company', 'email', 'phone']
            if not all(header in reader.fieldnames for header in required_headers):
                raise KeyError(f"Missing one or more required columns: {required_headers}")

            for row_idx, row in enumerate(reader, start=2): # Header row is line 1
                original_name = row.get('name', '')
                original_email = row.get('email', '')
                original_phone = row.get('phone', '')

                validated_email = clean_email(original_email)
                validated_phone = clean_phone(original_phone)

                # If email is corrupt, reject row and log the incident to our audit ledger
                if not validated_email:
                    skipped_count += 1
                    log_event(f"ROW REJECTED (Line {row_idx}): Invalid email schema format for target '{original_name}' [{original_email}]")
                    continue

                # Apply data transformations
                row['name'] = clean_name(original_name)
                row['email'] = validated_email
                row['phone'] = validated_phone
                row['company'] = row.get('company', '').strip()

                cleaned_rows.append(row)

        # Write the pristine dataset out
        with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)

        print(f"[+] Automation complete.")
        print(f"[+] Pristine records written to: {output_file}")
        print(f"[!] Skipped/Corrupt records isolated: {skipped_count} (Check cleaning_log.txt for data breakdown)")
        log_event(f"SUCCESS: Pipeline completed. {len(cleaned_rows)} records saved, {skipped_count} records isolated.")

    except KeyError as ke:
        print(f"[-] Data Schema Error: {ke}")
        log_event(f"CRITICAL DATA ERROR: {ke}")
    except Exception as e:
        print(f"[-] Unexpected Pipeline Exception: {e}")
        log_event(f"UNEXPECTED SYSTEM ERROR: {e}")

if __name__ == "__main__":
    process_csv('messy_contacts.csv', 'pristine_contacts.csv')