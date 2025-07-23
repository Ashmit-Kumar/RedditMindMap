"""Main script to generate a Reddit user persona from a profile URL.

Run either of these:

1) CLI usage:
   $ python main.py https://www.reddit.com/user/example/

2) VS Code / no‑arg execution:
   $ python main.py
   ▶︎ (the script will then ask for the URL interactively)
"""

from __future__ import annotations
import sys


from supabase_utils import fetch_usernames, mark_username_processed
from persona_utils import (
    extract_username,
    scrape_user_data,
    generate_persona,
    save_persona,
)


def get_profile_url() -> str:
    """
    Return a Reddit profile URL from argv or interactive prompt.

    If the script is executed without exactly one CLI argument,
    the user is prompted to paste a URL or plain username.
    """
    if len(sys.argv) == 2:
        return sys.argv[1]

    # Interactive fallback
    # print("No URL supplied on the command line.")
    raw = input("Paste the Reddit profile URL (or just the username): ").strip()

    # Allow users to paste only the username
    if not raw.startswith("http"):
        raw = f"https://www.reddit.com/user/{raw}/"

    return raw


def main() -> None:
    """Generate a Reddit user persona and save it to <username>_persona.txt."""
    profile_url = get_profile_url()
    username = extract_username(profile_url)

    if username is None:
        print("❌  Could not parse a username from that input. Exiting.")
        sys.exit(1)

    try:
        posts, comments = scrape_user_data(username)
    except Exception as exc:  # pragma: no cover
        print(f"❌  Failed to scrape data: {exc}")
        sys.exit(1)

    persona = generate_persona(posts, comments)
    if not persona:
        print("❌  Failed to generate a persona. Exiting.")
        sys.exit(1)
    
    # Save the persona to a text file
    # The function also saves it to .md and .json formats
    # so we don't need to call those functions separately.
    save_persona(username, persona, posts, comments)

    print(f"✅  Persona generated → {username}_persona.txt")


if __name__ == "__main__":
    main()
