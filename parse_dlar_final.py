
import fitz  # PyMuPDF
import re
import json
from datetime import datetime, timedelta

def parse_dlar_pdf(file_path, processing_date):
    doc = fitz.open(file_path)
    data = []

    hour_pattern = re.compile(r'\d{2}:\d{2} - \d{2}:\d{2}')

    for page in doc:
        lines = []
        blocks = page.get_text("blocks")
        for block in blocks:
            lines.extend(block[4].split('\n'))

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if hour_pattern.match(line):
                hour = line
                try:
                    guest_count = int(lines[i + 2].strip())
                    sales = float(lines[i + 5].strip().replace('$', '').replace(',', ''))
                    labour_hours = float(lines[i + 8].strip())

                    # Assign business day logic (6am–5:59am business window)
                    start_hour = int(hour[:2])
                    business_day = processing_date
                    if start_hour < 6:
                        dt = datetime.strptime(processing_date, '%Y-%m-%d') + timedelta(days=1)
                        business_day = dt.strftime('%Y-%m-%d')

                    data.append({
                        "processing_date": processing_date,
                        "business_day": business_day,
                        "hour": hour,
                        "sales": sales,
                        "guest_count": guest_count,
                        "labour_hours": labour_hours
                    })
                except Exception as e:
                    # Optionally log: print(f"Skipping malformed row at line {i}: {e}")
                    pass

                i += 9  # Move to next time block after parsing its data
            else:
                i += 1

    return data

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python parse_dlar.py <PDF_FILE_PATH> <PROCESSING_DATE: YYYY-MM-DD>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    processing_date = sys.argv[2]

    parsed_data = parse_dlar_pdf(pdf_path, processing_date)
    print(json.dumps(parsed_data, indent=2))
