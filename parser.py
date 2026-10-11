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
    
    # Locate ROBB's exact bounding box (x0, y0, x1, y1)
    robb_box = None
    for w in words:
        if "ROBB" in w[4].upper():
            robb_box = (w[0], w[1], w[2], w[3])
            break

    if robb_box is None:
        print("Error: Could not locate ROBB in the grid.")
        return

    # Define strict vertical boundaries for ROBB's specific row
    row_top = robb_box[1] - 3
    row_bottom = robb_box[3] + 3
    print(f"Strict row band for ROBB: Y between {row_top} and {row_bottom}")

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

    # Filter words strictly inside ROBB's exact row vertical band, excluding the name "ROBB" itself
    robb_words = [w for w in words if row_top <= ((w[1] + w[3]) / 2) <= row_bottom]
    robb_words = [w for w in robb_words if "ROBB" not in w[4].upper()]
    
    # Sort strictly left-to-right across the page
    robb_words.sort(key=lambda x: x[0])

    print(f"Found {len(robb_words)} shift tokens strictly in ROBB's row.")

    # Map detected tokens sequentially to days 1 through 30
    for i, w in enumerate(robb_words):
        text = w[4].strip().upper()
        day_num = i + 1
        
        if day_num > 30:
            break
            
        if text in shift_times:
            start_t, end_t = shift_times[text]
            shift_date = datetime(year, month, day_num).date()
            
            e = Event()
            e.name = f"Work - Shift {text}"
            
            if end_t < start_t:
                end_datetime = datetime.combine(shift_date + timedelta(days=1), end_t)
            else:
                end_datetime = datetime.combine(shift_date, end_t)
                
            e.begin = datetime.combine(shift_date, start_t)
            e.end = end_datetime
            cal.events.add(e)
            
            print(f"Day {day_num} (X={w[0]:.1f}): Added shift {text} for {shift_date}")
        else:
            print(f"Day {day_num} (X={w[0]:.1f}): Non-shift token ({text}) / Off")

    # Save output .ics file
    ics_path = "schedule.ics"
    with open(ics_path, 'w') as f:
        f.writelines(cal)
    
    print(f"Successfully generated {ics_path}")

if __name__ == "__main__":
    parse_schedule()
