# utils.py
import pytz
from datetime import datetime

def convert_utc_to_est(utc_dt):
    utc = pytz.utc
    est = pytz.timezone('America/New_York')
    utc_dt = utc.localize(utc_dt)
    est_dt = utc_dt.astimezone(est)
    return est_dt
