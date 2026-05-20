import csv
import os
import re

def clean_email(email):
    """Strips whitespace, converts to lowercase, and validates email format."""
    email = email.strip().lower()
    # Simple regex for baseline email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    return None

def clean_phone(phone):
    """Removes common formatting characters and returns a clean digit string."""
    # Removes spaces, dashes, parentheses, and extensions for standard formatting
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    return cleaned if cleaned.isdigit() else "INVALID_PHONE"

def process_csv(input_file, output_file):
    """Reads a messy business contact CSV, cleans fields, and writes a pristine copy."""
    if not os.path.exists(input_file):
        print(f"[-] Error: Source file '{input_file}' not found.")
        return

    print(f"[+] Initializing audit on: {input_file}")
    
    cleaned_rows = []
    skipped_count = 0

    with open(input_file, mode='r', encoding='utf-8') as infile:
        # Using DictReader so we can track columns by their business headers safely
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        for row in reader:
            # Clean the email field safely
            original_email = row.get('email', '')
            validated_email = clean_email(original_email)
            
            # Clean the phone field safely
            original_phone = row.get('phone', '')
            validated_phone = clean_phone(original_phone)

            if not validated_email:
                # If the email is completely corrupt, we flag it or skip to protect dataset integrity
                skipped_count += 1
                continue

            # Update the row with pristine, standardized data
            row['email'] = validated_email
            row['phone'] = validated_phone
            
            # Trim trailing spaces from names or company text fields
            for key in row:
                if row[key]:
                    row[key] = row[key].strip()

            cleaned_rows.append(row)

    # Write the pristine dataset out
    with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"[+] Automation complete.")
    print(f"[+] Pristine records written to: {output_file}")
    print(f"[!] Skipped/Corrupt records removed: {skipped_count}")

if __name__ == "__main__":
    # This matches the sample files we will create next
    process_csv('messy_contacts.csv', 'pristine_contacts.csv')