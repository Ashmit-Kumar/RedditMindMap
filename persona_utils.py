"""
Utility helpers for generating a Reddit user persona.

Functions
---------
extract_username(url: str) -> str | None
    Extract the username from a Reddit profile URL.

scrape_user_data(username: str, limit: int = 30)
    Return the user's recent posts and comments.

generate_persona(posts: list[dict], comments: list[dict]) -> str
    Use Google Gemini to build a persona with citations.

save_persona(username: str, persona: str) -> None
    Persist the generated persona to a text file.
"""

from __future__ import annotations

import os
import re
from typing import Tuple, List, Dict

import google.generativeai as genai
import praw
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Environment & client setup
# --------------------------------------------------------------------------- #

load_dotenv()  # Loads GOOGLE_API_KEY, REDDIT_CLIENT_ID, etc.

# Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
_GEMINI_MODEL = genai.GenerativeModel("models/gemini-1.5-flash")

# Reddit (PRAW)
_reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="persona-generator-script",
)

# --------------------------------------------------------------------------- #
# Public helpers
# --------------------------------------------------------------------------- #


def extract_username(url: str) -> str | None:
    """
    Extract a Reddit username from the supplied profile URL.

    Parameters
    ----------
    url : str
        Full profile URL, e.g. ``https://www.reddit.com/user/example/``.

    Returns
    -------
    str | None
        The username portion or ``None`` if no match is found.
    """
    match = re.search(r"reddit\.com/user/([^/]+)", url)
    return match.group(1) if match else None


def scrape_user_data(
    username: str, limit: int = 30
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Fetch a user's most recent posts and comments.

    Parameters
    ----------
    username : str
        Reddit username (without the ``u/`` prefix).
    limit : int, optional
        Maximum number of posts and comments to pull for each type.

    Returns
    -------
    tuple[list[dict], list[dict]]
        Two lists containing post dicts and comment dicts respectively.
    """
    user = _reddit.redditor(username)

    posts = [
        {
            "text": f"{submission.title}\n{submission.selftext}",
            "url": f"https://reddit.com{submission.permalink}",
        }
        for submission in user.submissions.new(limit=limit)
    ]

    comments = [
        {
            "text": comment.body,
            "url": f"https://reddit.com{comment.permalink}",
        }
        for comment in user.comments.new(limit=limit)
    ]

    return posts, comments


def generate_persona(posts: List[Dict[str, str]], comments: List[Dict[str, str]]) -> str:
    """
    Build a persona description (with citations) via Gemini.

    Notes
    -----
    To keep the token count manageable, the first 50 items are used.

    Returns
    -------
    str
        Formatted persona text.
    """
    # Flatten content into prompt snippets
    snippets = [
        f"{item['text']}\nSource: {item['url']}" for item in (posts + comments)
    ][:50]

    if not snippets:
        return "No content available to generate a persona."    
    prompt = f"""
    You are an AI tasked with analyzing a Reddit user's personality based on their recent posts and comments.

    Generate a well-formatted TEXT-ONLY persona report (not markdown or HTML). Use plain formatting with:
    - Emoji headers (e.g. 🎯 Goals & Needs)
    - Clear section titles with dashes or lines
    - No asterisks, hashes, or markdown symbols
    - Indent or format citations clearly

    Each section should include relevant insights with citations from the user's content.

    Sections to include:
    1. 🎯 Interests
    2. 🤔 Personality Traits
    3. 🗣️ Tone of Writing
    4. 👨‍🎓 Profession or Education (if inferred)
    5. 😂 Humor or Style
    6. 🌎 Political/Social Leanings (if any)
    7. 🚫 Limitations
    8. 💬 Representative Quote (optional)
    9. ✅ Goals & Needs (optional)

    Here are their Reddit posts and comments:
    {'=' * 80}
    {chr(10).join(snippets)}
    """

    response = _GEMINI_MODEL.generate_content(prompt)
    return response.text


def save_persona(username: str, persona: str) -> None:
    """
    Write the generated persona to ``<username>_persona.txt``.

    Parameters
    ----------
    username : str
        Reddit username.
    persona : str
        Text returned by ``generate_persona``.
    """
    outfile = f"{username}_persona.txt"
    with open(outfile, "w", encoding="utf-8") as handle:
        handle.write(persona)
