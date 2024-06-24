from pytz import timezone, utc
from datetime import datetime

def convert_utc_to_edt(utc_dt: datetime) -> datetime:
    if utc_dt.tzinfo is None:
        utc_dt = utc.localize(utc_dt)  # Localize the datetime to UTC if it is not already timezone-aware
    eastern = timezone('US/Eastern')
    return utc_dt.astimezone(eastern)
