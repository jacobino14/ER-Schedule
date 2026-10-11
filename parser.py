import os
import fitz  # PyMuPDF
from ics import Calendar, Event
from datetime import datetime, time, timedelta

def parse_schedule():
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("Error: No schedule PDF found in root directory.")
        return

    pdf_path = pdf_files[0]
    print(f"Processing schedule: {pdf_path}")

    doc = fitz.open(pdf_path)
    page = doc[0]
    words = page.get_text("words")
    
    # Locate ROBB's row coordinate
    robb_y = None
    for w in words:
        if "ROBB" in w[4].upper():
            robb_y = (w[1] + w[3]) / 2
            break

    if robb_y is None:
        print("Warning: Could not locate ROBB in grid.")
    else:
        print(f"Successfully located ROBB at vertical coordinate: {robb_y}")

    # Initialize Calendar
    cal = Calendar()
    
    # Save output .ics file
    ics_path = "schedule.ics"
    with open(ics_path, 'w' ) as f:
        f.writelines(cal)
    
    print(f"Successfully generated {ics_path}")

if __name__ == "__main__":
    parse_schedule()
