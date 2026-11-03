def late_fee(days_late: int) -> int:
    """Library policy: 25 cents per day, capped at 10 dollars."""
    return min(days_late * 25, 1000)

def parking_fee(hours: int) -> int:
    """City parking: 25 cents per hour, capped at 10 dollars per day."""
    return min(hours * 25, 1000)
