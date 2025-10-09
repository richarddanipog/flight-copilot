from datetime import date, datetime
import calendar
import re

_MONTH = {m[:3].lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], start=1)}


def normalize_departure(value: str, default_day: int = 15) -> str:
    """
    Accepts 'april' or '2025-09-15' (also '2025-9-5') → returns YYYY-MM-DD.
    If only month given, choose the next occurrence of that month (never past).
    """
    v = value.strip()
    # month-only (e.g., "april")
    if v.isalpha():
        m = _MONTH.get(v[:3].lower())
        if not m:
            raise ValueError(f"Unknown month: {v}")
        today = date.today()
        year = today.year if m >= today.month else today.year + 1
        # safe day (handles Feb)
        day = 28 if m == 2 and default_day > 28 else min(default_day, 30)
        return date(year, m, day).isoformat()
    # ISO-ish date
    try:
        y, mo, d = [int(x) for x in v.split("-")]
        return f"{y:04d}-{mo:02d}-{d:02d}"
    except Exception:
        raise ValueError(f"Bad date format: {v}")


def ensure_future(iso: str) -> None:
    """Raise if date is in the past."""
    if datetime.fromisoformat(iso).date() < date.today():
        return roll_to_future(_to_date(iso))
        # raise ValueError("The departure date is in the past.")
    return iso


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    # common typos/short
    "oct": 10, "nov": 11, "dec": 12, "octuber": 10, "sep": 9
}


def _to_date(value) -> date:
    """Accepts date/datetime or strings like 'april' or '2023-11-01'."""
    if isinstance(value, date):
        return value
    s = str(value).strip().lower()
    if s.isalpha():
        m = _MONTHS.get(s)
        if not m:
            raise ValueError(f"Unknown month: {value}")
        # pick a safe middle day (28 for Feb)
        day = 28 if m == 2 else 15
        return date(date.today().year, m, day)
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)


def roll_to_future(d: date) -> date:
    """If d is in the past, roll it forward by whole years until it's today or later."""
    today = date.today()
    while d < today:
        y2 = d.year + 1
        d = date(y2, d.month, min(d.day, calendar.monthrange(y2, d.month)[1]))
    return d


class PastDateError(ValueError):
    pass


def validate_dates_in_query(query: str) -> None:
    """
    Look for YYYY-MM-DD dates in query string and validate them.
    Raises PastDateError if any date is in the past
    or if return_date <= departure_date.
    """
    today = date.today()

    # match yyyy-mm-dd
    matches = re.findall(r"\d{4}-\d{1,2}-\d{1,2}", query)
    if not matches:
        return  # nothing to check, let LLM handle

    dates = []
    for m in matches:
        try:
            d = datetime.fromisoformat(m).date()
            dates.append(d)
        except Exception:
            continue

    if not dates:
        return

    # check past
    for d in dates:
        if d < today:
            raise PastDateError(f"Date {d} is in the past (today is {today}).")

    # if two dates found, treat as depart + return
    if len(dates) >= 2:
        depart, ret = dates[0], dates[1]
        if ret <= depart:
            raise PastDateError(
                f"Return date {ret} must be after departure {depart}."
            )


def coerce_future_iso(iso_or_text) -> str:
    """
    Ensure a given YYYY-MM-DD (or datetime/date) is not in the past.
    If it's in the past, roll it forward to next year (same month/day).
    """
    if iso_or_text is None:
        return None

    # Already a date/datetime
    if hasattr(iso_or_text, "isoformat"):
        parts = iso_or_text.isoformat().split("T")[0]
    else:
        parts = str(iso_or_text).strip()

    y, m, d = [int(x) for x in parts.split("-")]
    dt = date(y, m, d)
    today = date.today()

    # Roll forward until it's >= today
    while dt < today:
        y += 1
        d = min(d, calendar.monthrange(y, m)[1])
        dt = date(y, m, d)

    return dt


def get_time_minutes(dt: datetime) -> int:
    return int(dt.timestamp() // 60)
