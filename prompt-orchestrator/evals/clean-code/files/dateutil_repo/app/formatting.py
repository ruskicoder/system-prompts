from datetime import date

def format_iso_date(d: date) -> str:
    """Format a date as YYYY-MM-DD for API payloads."""
    return d.isoformat()
