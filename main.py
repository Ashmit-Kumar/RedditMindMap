"""Main script to generate a Reddit user persona from a profile URL."""

import sys
from persona_utils import (
    extract_username,
    scrape_user_data,
    generate_persona,
    save_persona,
)


def main():
    """Main execution function for generating Reddit user persona."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <Reddit User Profile URL>")
        sys.exit(1)

    profile_url = sys.argv[1]
    username = extract_username(profile_url)

    posts, comments = scrape_user_data(username)
    persona = generate_persona(posts, comments)

    save_persona(username, persona)
    print(f"Persona generated: {username}_persona.txt")


if __name__ == "__main__":
    main()
