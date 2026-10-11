import os
import fitz  # PyMuPDF
from ics import Calendar, Event
from datetime import datetime, time, timedelta

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

    # Filter text tokens in ROBB's row band and sort left-to-right
    robb_words = [w for w in words if abs(((w[1] + w[3]) / 2) - robb_y) < 12]
    robb_words.sort(key=lambda x: x[0])

    day_counter = 1
    for w in robb_words:
        text = w[4].strip().upper()
        
        # Check for shift letters or slash-off notation (e.g., A/ / or standard shift)
        if text in shift_times and day_counter <= 30:
            start_t, end_t = shift_times[text]
            shift_date = datetime(year, month, day_counter).date()
            
            e = Event()
            e.name = f"Work - Shift {text}"
            
            # Handle overnight shifts crossing midnight
            if end_t < start_t:
                end_datetime = datetime.combine(shift_date + timedelta(days=1), end_t)
            else:
                end_datetime = datetime.combine(shift_date, end_t)
                
            e.begin = datetime.combine(shift_date, start_t)
            e.end = end_datetime
            cal.events.add(e)
            
            print(f"Added shift {text} for {shift_date}")
            day_counter += 1

    # Save output .ics file
    ics_path = "schedule.ics"
    with open(ics_path, 'w') as f:
        f.writelines(cal)
    
    print(f"Successfully generated {ics_path}")

if __name__ == "__main__":
    parse_schedule()
