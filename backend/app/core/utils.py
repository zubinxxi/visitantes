from datetime import datetime, timezone, timedelta
from typing import Optional


TIMEZONE_PANAMA = timezone(timedelta(hours=-5))


def now_panama() -> datetime:
    return datetime.now(TIMEZONE_PANAMA)


def today_start_panama() -> datetime:
    now = now_panama()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)