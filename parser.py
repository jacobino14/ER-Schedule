from datetime import datetime
from zoneinfo import ZoneInfo
from ics import Calendar, Event
import fitz  # PyMuPDF
import glob
import os

# Define Central Time zone
CENTRAL_TZ = ZoneInfo("America/Chicago")

def parse_pdf_schedule(pdf_path):
    doc = fitz.open(pdf_path)
    cal = Calendar()
    
    for page in doc:
        # (Your existing grid parsing, date mapping, and shift extraction logic here)
        # Ensure that when you create an event, you combine it into a single object like this:
        
        # EXAMPLE OF CORRECT EVENT CREATION:
        # e = Event()
        # e.name = "ER Shift"
        # e.begin = datetime(year, month, day, start_hour, start_minute, tzinfo=CENTRAL_TZ)
        # e.end = datetime(year, month, day, end_hour, end_minute, tzinfo=CENTRAL_TZ)
        # cal.events.add(e)
        pass

    # Save out to schedule.ics
    with open("schedule.ics", "w") as f:
        f.writelines(cal)

if __name__ == "__main__":
    for pdf in glob.glob("*.pdf"):
        parse_pdf_schedule(pdf)
