from datetime import datetime

def is_valid_date(text: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        date = datetime.strptime(text, fmt).date()
        return date > datetime.today().date()
    except ValueError:
        return False