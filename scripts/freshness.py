#!/usr/bin/env python3
from __future__ import annotations

import email.utils
from datetime import datetime, timedelta, timezone


def parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        parsed = None
    if parsed is None:
        iso_value = str(value).strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(iso_value)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_within_age(value: str | None, max_age_days: int, now: datetime) -> bool:
    parsed = parse_published_at(value)
    if parsed is None:
        return False
    return parsed >= now - timedelta(days=max_age_days)
