import os
import fitz  # PyMuPDF
from ics import Calendar, Event
from datetime import datetime, time, timedelta

def parse_schedule():
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("Error: No schedule PDF found.")
        return

    doc = fitz.open(pdf_files[0])
    page = doc[0]
    words = page.get_text("words")
    
    # 1. Dynamically locate ROBB's row
    robb_box = None
    for w in words:
        if "ROBB" in w[4].upper():
            robb_box = (w[0], w[1], w[2], w[3])
            break

    if robb_box is None:
        print("Error: Could not locate ROBB in the grid.")
        return

    row_top = robb_box[1] - 4
    row_bottom = robb_box[3] + 4

    # 2. Dynamically map date columns from header row
    header_words = [w for w in words if w[3] < robb_box[1]]
    date_columns = {}
    for w in header_words:
        text = w[4].strip()
        if text.isdigit():
            day_num = int(text)
            if 1 <= day_num <= 31:
                x_center = (w[0] + w[2]) / 2
                date_columns[day_num] = x_center

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

    # 3. Extract text tokens in ROBB's row band
    robb_words = [w for w in words if row_top <= ((w[1] + w[3]) / 2) <= row_bottom]
    robb_words = [w for w in robb_words if "ROBB" not in w[4].upper()]

    # 4. Map tokens, ignoring any shift tokens containing a slash (PTO / slashed-off shifts)
    for w in robb_words:
        token = w[4].strip().upper()
        x_pos = (w[0] + w[2]) / 2
        
        if date_columns:
            closest_day = min(date_columns.keys(), key=lambda d: abs(date_columns[d] - x_pos))
            
            if abs(date_columns[closest_day] - x_pos) < 30:
                # If there's a slash in the token (e.g., A/ or /A), treat it as a PTO / off day
                if '/' in token:
                    print(f"Skipping slashed/PTO shift token '{token}' for Day {closest_day}")
                    continue
                
                if token in shift_times:
                    start_t, end_t = shift_times[token]
                    shift_date = datetime(year, month, closest_day).date()
                    
                    e = Event()
                    e.name = f"Work - Shift {token}"
                    
                    if end_t < start_t:
                        end_datetime = datetime.combine(shift_date + timedelta(days=1), end_t)
                    else:
                        end_datetime = datetime.combine(shift_date, end_t)
                        
                    e.begin = datetime.combine(shift_date, start_t)
                    e.end = end_datetime
                    cal.events.add(e)
                    print(f"Matched shift {token} at X={x_pos:.1f} to Day {closest_day} ({shift_date})")

    ics_path = "schedule.ics"
    with open(ics_path, 'w') as f:
        f.writelines(cal)
    
    print(f"Successfully generated {ics_path}")

if __name__ == "__main__":
    parse_schedule()
