import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from persona_utils import (
    scrape_user_data,
    generate_persona,
    save_persona,
)


def get_month_date_ranges(months_back: int) -> List[tuple[datetime, datetime]]:
    today = datetime.utcnow()
    ranges = []
    for i in range(months_back):
        month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        ranges.append((month_start, month_end))
    return list(reversed(ranges))  # earliest to latest


def filter_by_month(posts_or_comments: list, start: datetime, end: datetime):
    return [item for item in posts_or_comments if start.timestamp() <= item["created_utc"] <= end.timestamp()]


def track_evolution(username: str, months_back: int = 3):
    print(f"📆 Tracking evolution for {username} over {months_back} months...\n")
    all_posts, all_comments = scrape_user_data(username, limit=300)

    month_ranges = get_month_date_ranges(months_back)

    for start, end in month_ranges:
        label = start.strftime("%Y-%m")
        print(f"🔹 Processing {label}...", end=" ")

        posts = filter_by_month(all_posts, start, end)
        comments = filter_by_month(all_comments, start, end)

        if not posts and not comments:
            print("No data.")
            continue

        persona = generate_persona(posts, comments)
        save_persona(f"{username}_{label}", persona, posts, comments)
        print("✅")

    print("\n✅ All months processed.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        username = input("Enter Reddit username: ").strip()
    else:
        username = sys.argv[1]

    months = int(sys.argv[2]) if len(sys.argv) >= 3 else 3

    track_evolution(username, months_back=months)
