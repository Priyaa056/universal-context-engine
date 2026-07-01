from datetime import datetime


def format_file_size(size_in_bytes: int) -> str:
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Bytes"
    if size_in_bytes < 1024 * 1024:
        size_kb = size_in_bytes / 1024
        return f"{size_kb:.1f} KB" if not size_kb.is_integer() else f"{int(size_kb)} KB"

    size_mb = size_in_bytes / (1024 * 1024)
    return f"{size_mb:.1f} MB" if not size_mb.is_integer() else f"{int(size_mb)} MB"


def format_uploaded_at(dt: datetime) -> str:
    return dt.strftime("%d %b %Y, %I:%M %p")


def now_utc() -> datetime:
    return datetime.utcnow()
