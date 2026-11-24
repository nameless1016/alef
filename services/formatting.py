"""Small pure helpers for dates, estimates and labels."""
import re
import time
from datetime import date, datetime
from typing import Optional

_EST = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([mhd])\s*$", re.I)
HOURS_PER_DAY = 8


def parse_estimate(text: str) -> Optional[float]:
    """'30m' / '2h' / '1d' -> hours. None if the text isn't a valid estimate."""
    m = _EST.match(text or "")
    if not m:
        return None
    value, unit = float(m.group(1)), m.group(2).lower()
    return value / 60 if unit == "m" else value * (HOURS_PER_DAY if unit == "d" else 1)


def fmt_due(iso: Optional[str]) -> str:
    if not iso:
        return "Unscheduled"
    d = date.fromisoformat(iso)
    return f"{d:%b} {d.day}"


def fmt_long_date(d: date) -> str:
    return f"{d:%A} · {d:%B} {d.day}"


def greeting(hour: int) -> str:
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def rel_short(ts: float, now: Optional[float] = None) -> str:
    """Compact label for the changes list: Now / 18m / 3h / Yesterday / 4d."""
    secs = max(0, (now or time.time()) - ts)
    if secs < 60:
        return "Now"
    if secs < 3600:
        return f"{int(secs // 60)}m"
    if secs < 86400:
        return f"{int(secs // 3600)}h"
    days = int(secs // 86400)
    return "Yesterday" if days == 1 else f"{days}d"


def rel_synced(ts: float, now: Optional[float] = None) -> str:
    label = rel_short(ts, now)
    if label == "Now":
        return "Synced just now"
    if label == "Yesterday":
        return "Synced yesterday"
    return f"Synced {label} ago"


def number_word(n: int) -> str:
    words = ["No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    return words[n] if 0 <= n < len(words) else str(n)


def initials(name: str) -> str:
    parts = [p for p in re.split(r"\s+", name.strip()) if p]
    return ("".join(p[0] for p in parts[:2]) or "?").upper()
