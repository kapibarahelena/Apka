from datetime import timezone
from app.connectors.strava import parse_start_time

def test_parse_zulu_time():
    dt = parse_start_time("2024-01-02T03:04:05Z")
    assert dt.tzinfo is not None
    assert dt.utcoffset().total_seconds() == 0

def test_parse_offset_time():
    dt = parse_start_time("2024-01-02T04:04:05+01:00")
    assert dt.astimezone(timezone.utc).hour == 3
