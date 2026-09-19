'''
Utility helpers for Budget Tracker: formatting and parsing values and dates.
'''
from datetime import date, datetime
from typing import Optional
def format_currency(value: float, symbol: str = "$") -> str:
    try:
        v = float(value)
    except Exception:
        v = 0.0
    sign = "-" if v < 0 else ""
    return f"{sign}{symbol}{abs(v):,.2f}"
def parse_float(text: str, default: float = 0.0) -> float:
    if text is None:
        return default
    try:
        # Remove common formatting
        t = str(text).replace(",", "").replace("$", "").strip()
        if not t:
            return default
        return float(t)
    except Exception:
        return default
def parse_date(text: str, default: Optional[date] = None) -> date:
    if isinstance(text, date):
        return text
    if isinstance(text, datetime):
        return text.date()
    if text:
        t = str(text).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(t, fmt).date()
            except Exception:
                continue
    return default or date.today()
def date_to_str(d: date) -> str:
    return d.strftime("%Y-%m-%d")