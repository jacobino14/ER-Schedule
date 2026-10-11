import os
import fitz  # PyMuPDF
from ics import Calendar, Event
from datetime import datetime, time

def parse_schedule():
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("Error: No schedule PDF found.")
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
        print("Error: Could not locate ROBB in the grid.")
        return

    print(f"Successfully located ROBB at Y: {robb_y}")

    # Shift time definitions
    shift_times = {
        'A': (time(5, 0), time(15, 30)),
        'B': (time(6, 0), time(16, 30)),
        'C': (time(8, 0), time(18, 30)),
        'D': (time(11, 0), time(21, 30)),
        'E': (time(18, 30), time(5, 0)),
        'F': (time(21, 30), time(8, 0)),
        'M': (time(7, 30), time(15, 30))
    }

    cal = Calendar()
    year, month = 2026, 11

    # Filter text tokens in ROBB's row band
    robb_words = [w for w in words if abs(((w[1] + w[3]) / 2) - robb_y) < 12]
    robb_words.sort(key=lambda x: x[0])  # Sort left to right across days

    # Process each detected word token in the row
    for w in robb_words:
        text = w[4].strip().upper()
        if text in shift_times:
            # Note: We will map token position sequentially to calendar days
            start_t, end_t = shift_times[text]
            # Placeholder for day mapping corresponding to column index
            print(f"Found shift {text} at X coordinate {w[0]}")

    # Save output .ics file
    ics_path = "schedule.ics"
    with open(ics_path, 'w') as f:
        f.writelines(cal)
    
    print(f"Successfully generated {ics_path}")

if __name__ == "__main__":
    parse_schedule()
