from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ics import Calendar, Event
import fitz  # PyMuPDF
import glob

# Central Time Zone Definition
CENTRAL_TZ = ZoneInfo("America/Chicago")

def create_shift_event(title, start_dt_local, end_dt_local):
    """
    Creates a single continuous ICS Event object with Central Time.
    """
    event = Event()
    event.name = title
    event.begin = start_dt_local
    event.end = end_dt_local
    # Generate a unique ID per event to force calendar apps to update clean cache
    event.uid = f"{title}-{start_dt_local.strftime('%Y%m%dT%H%M%S')}@er-schedule"
    return event

# --- YOUR ORIGINAL GRID & SHIFT EXTRACTION LOGIC ---
# In your shift creation step inside parser.py, update the event instantiation to:

# 1. Build naive datetime objects from your extracted year, month, day, and shift hours
#    start_dt = datetime(year, month, day, start_hour, start_minute, tzinfo=CENTRAL_TZ)
#    end_dt = datetime(year, month, day, end_hour, end_minute, tzinfo=CENTRAL_TZ)

# 2. Handle overnight shifts crossing midnight (if end time is earlier than start time)
#    if end_dt <= start_dt:
#        end_dt += timedelta(days=1)

# 3. Instantiate a single Event and assign both begin and end:
#    shift_event = Event()
#    shift_event.name = f"Work Shift ({shift_key})"
#    shift_event.begin = start_dt
#    shift_event.end = end_dt
#    cal.events.add(shift_event)
