from pytz import timezone, utc
from datetime import datetime
from flask import current_app


def convert_utc_to_edt(utc_dt: datetime) -> datetime:
    if utc_dt.tzinfo is None:
        utc_dt = utc.localize(utc_dt)  # Localize the datetime to UTC if it is not already timezone-aware
    eastern = timezone('US/Eastern')
    return utc_dt.astimezone(eastern)

def run_with_app_context(func, *args, **kwargs):
    app = current_app._get_current_object()
    def wrapped_func(*args, **kwargs):
        with app.app_context():
            with app.test_request_context():
                return func(*args, **kwargs)
    return wrapped_func
