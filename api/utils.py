def get_minutes_difference(start, end):
    return (end - start).total_seconds() / 60

def time_in_range(now, start, end):
    return start <= now <= end