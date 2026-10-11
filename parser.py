import glob
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ics import Calendar, Event
import fitz  # PyMuPDF

# Explicitly set Central Time zone
CENTRAL_TZ = ZoneInfo("America/Chicago")

# Shift Mapping Table based on standard ER schedule shift keys
# Standardizes start and end times in local Central Time
SHIFT_TIMES = {
    "7A": ("07:00", "15:30"),
    "7A8": ("07:00", "15:30"),
    "8A": ("08:00", "16:30"),
    "9A": ("09:00", "17:30"),
    "10A": ("10:00", "18:30"),
    "11A": ("11:00", "19:30"),
    "3P": ("15:00", "23:30"),
    "3P11": ("15:00", "23:30"),
    "7P": ("19:00", "07:30"),  # Overnight shift
    "11P": ("23:00", "07:30"), # Overnight shift
}

def parse_time(time_str):
    """Parse HH:MM string to hour and minute integers."""
    hours, minutes = map(int, time_str.split(":"))
    return hours, minutes

def generate_ics():
    cal = Calendar()
    
    # Process all PDF schedule files in repository
    pdf_files = glob.glob("*.pdf")
    
    for pdf_file in pdf_files:
        doc = fitz.open(pdf_file)
        
        # Determine month and year from filename or first page text (default fallback: Nov 2026)
        year = 2026
        month = 11
        
        match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s*(\d{4})', pdf_file, re.IGNORECASE)
        if match:
            month_str, year_str = match.groups()
            year = int(year_str)
            month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
            month = month_names.index(month_str.upper()) + 1

        for page in doc:
            text = page.get_text("text")
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            
            # Simple grid iteration for day numbers and shift codes
            for i, line in enumerate(lines):
                if line.isdigit() and 1 <= int(line) <= 31:
                    day = int(line)
                    
                    # Look at adjacent lines for valid shift codes
                    for j in range(1, 4):
                        if i + j < len(lines):
                            candidate_code = lines[i + j].upper().replace(" ", "")
                            
                            if candidate_code in SHIFT_TIMES:
                                start_time_str, end_time_str = SHIFT_TIMES[candidate_code]
                                start_h, start_m = parse_time(start_time_str)
                                end_h, end_m = parse_time(end_time_str)
                                
                                # Construct continuous datetime objects in Central Time
                                start_dt = datetime(year, month, day, start_h, start_m, tzinfo=CENTRAL_TZ)
                                end_dt = datetime(year, month, day, end_h, end_m, tzinfo=CENTRAL_TZ)
                                
                                # Handle overnight shifts crossing midnight
                                if end_dt <= start_dt:
                                    end_dt += timedelta(days=1)
                                
                                # Single continuous Event creation
                                event = Event()
                                event.name = f"ER Shift ({candidate_code})"
                                event.begin = start_dt
                                event.end = end_dt
                                event.location = "Emergency Department"
                                event.uid = f"er-shift-{year}-{month:02d}-{day:02d}-{candidate_code}@schedule"
                                
                                cal.events.add(event)
                                break

    # Write out updated schedule.ics
    with open("schedule.ics", "w") as f:
        f.writelines(cal.serialize())

if __name__ == "__main__":
    generate_ics()
