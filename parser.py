import os
import re
import fitz  # PyMuPDF
from ics import Calendar, Event
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

# Define Central Time Zone
CENTRAL_TZ = ZoneInfo("America/Chicago")

def parse_schedule():
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and f.upper() != 'SCHEDULE.PDF']
    if not pdf_files:
        print("Error: No schedule PDFs found.")
        return

    cal = Calendar()

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

    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }

    for pdf_path in pdf_files:
        print(f"Processing schedule: {pdf_path}")
        
        # Extract month and year from filename
        match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\D*(\d{4})', pdf_path.upper())
        if not match:
            print(f"Could not parse month/year from filename {pdf_path}, skipping.")
            continue
            
        month_str, year_str = match.groups()
        month = month_map[month_str]
        year = int(year_str)

        doc = fitz.open(pdf_path)
        page = doc[0]
        words = page.get_text("words")
        
        # Dynamically locate ROBB's row wherever positioned
        robb_box = None
        for w in words:
            if "ROBB" in w[4].upper():
                robb_box = (w[0], w[1], w[2], w[3])
                break

        if robb_box is None:
            print(f"Could not locate ROBB in {pdf_path}.")
            continue

        row_top = robb_box[1] - 4
        row_bottom = robb_box[3] + 4

        # Dynamically map date columns from header row
        header_words = [w for w in words if w[3] < robb_box[1]]
        date_columns = {}
        for w in header_words:
            text = w[4].strip()
            if text.isdigit():
                day_num = int(text)
                if 1 <= day_num <= 31:
                    x_center = (w[0] + w[2]) / 2
                    date_columns[day_num] = x_center

        robb_words = [w for w in words if row_top <= ((w[1] + w[3]) / 2) <= row_bottom]
        robb_words = [w for w in robb_words if "ROBB" not in w[4].upper()]
        drawings = page.get_drawings()

        for w in robb_words:
            token = w[4].strip().upper()
            x_pos = (w[0] + w[2]) / 2
            
            if date_columns and token in shift_times:
                closest_day = min(date_columns.keys(), key=lambda d: abs(date_columns[d] - x_pos))
                
                if abs(date_columns[closest_day] - x_pos) < 30:
                    # Check for diagonal slash vector (PTO)
                    w_rect = fitz.Rect(w[0]-2, w[1]-2, w[2]+2, w[3]+2)
                    has_slash = False
                    for d in drawings:
                        if "items" in d:
                            for item in d["items"]:
                                if item[0] == "l":
                                    p1, p2 = item[1], item[2]
                                    if w_rect.intersects(fitz.Rect(min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y))):
                                        has_slash = True
                                        break
                        if has_slash:
                            break

                    if has_slash:
                        print(f"Skipping slashed PTO shift '{token}' for Day {closest_day}")
                        continue

                    start_t, end_t = shift_times[token]
                    try:
                        shift_date = datetime(year, month, closest_day).date()
                    except ValueError:
                        continue 
                        
                    e = Event()
                    e.name = f"Work - Shift {token}"
                    
                    # Attach Central Time Zone and handle overnight spans cleanly
                    if end_t < start_t:
                        e.begin = datetime.combine(shift_date, start_t, tzinfo=CENTRAL_TZ)
                        e.end = datetime.combine(shift_date + timedelta(days=1), end_t, tzinfo=CENTRAL_TZ)
                    else:
                        e.begin = datetime.combine(shift_date, start_t, tzinfo=CENTRAL_TZ)
                        e.end = datetime.combine(shift_date, end_t, tzinfo=CENTRAL_TZ)
                    
                    # Assign a stable UID to prevent calendar splitting/duplicates
                    e.uid = f"er-shift-{shift_date.isoformat()}-{token}@er-schedule"
                    
                    cal.events.add(e)
                    print(f"Added shift {token} for {shift_date}")

    ics_path = "schedule.ics"
    with open(ics_path, 'w') as f:
        f.writelines(cal)
    
    print(f"Successfully generated combined {ics_path}")

if __name__ == "__main__":
    parse_schedule()
