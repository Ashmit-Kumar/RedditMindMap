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

def save_persona(username: str, persona: str, posts: List[dict], comments: List[dict]) -> None:
    Persist the generated persona to a text file,md and json.
"""

from __future__ import annotations

import os
import re
from typing import Tuple, List, Dict

import json
import google.generativeai as genai
import praw
from dotenv import load_dotenv
from datetime import datetime

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

    # posts = [
    #     {
    #         "text": f"{submission.title}\n{submission.selftext}",
    #         "url": f"https://reddit.com{submission.permalink}",
    #     }
    #     for submission in user.submissions.new(limit=limit)
    # ]

    # comments = [
    #     {
    #         "text": comment.body,
    #         "url": f"https://reddit.com{comment.permalink}",
    #     }
    #     for comment in user.comments.new(limit=limit)
    # ]
    posts = []
    for submission in user.submissions.new(limit=limit):
        posts.append({
            "text": f"{submission.title}\n{submission.selftext}",
            "url": f"https://reddit.com{submission.permalink}",
            "created_utc": submission.created_utc,
            "subreddit": str(submission.subreddit),
            "score": submission.score,
            "num_comments": submission.num_comments,
        })

    comments = []
    for comment in user.comments.new(limit=limit):
        comments.append({
            "text": comment.body,
            "url": f"https://reddit.com{comment.permalink}",
            "created_utc": comment.created_utc,
            "subreddit": str(comment.subreddit),
            "score": comment.score,
        })

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

def save_persona(username: str, persona: str, posts: List[dict], comments: List[dict]) -> None:
    """
    Save the generated persona to .txt, .md, and .json formats.

    Parameters
    ----------
    username : str
        Reddit username.
    persona : str
        Full text of the persona generated by Gemini.
    """
    txt_file = f"{username}_persona.txt"
    md_file = f"{username}_persona.md"
    json_file = f"{username}_persona.json"

    # Save .json
    structured = {
    "username": username,
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "persona": parse_persona_to_json(persona),
    "personality_frameworks": map_to_frameworks(persona),
    "raw_data": {
        "posts": posts,       # <-- include scraped posts
        "comments": comments  # <-- include scraped comments
    }
    }


    with open(json_file, "w", encoding="utf-8") as json_handle:
        json.dump(structured, json_handle, indent=2, ensure_ascii=False)

    # Save .txt
    with open(txt_file, "w", encoding="utf-8") as txt_handle:
        txt_handle.write(f"👤 Reddit Username: {username}\n\n{persona}")

    # Save .md
    markdown_version = convert_to_markdown(persona)
    with open(md_file, "w", encoding="utf-8") as md_handle:
        md_handle.write(f"# 👤 Reddit Username: {username}\n\n{markdown_version}")

    print(f"✅ Persona saved as: {txt_file}, {md_file}, {json_file}")


def convert_to_markdown(text: str) -> str:
    """
    Convert a plain-text persona report into Markdown format.

    This includes:
    - Promoting emoji headers to Markdown-style headings.
    - Converting citation lines to link format.

    Parameters
    ----------
    text : str
        Plain text persona content.

    Returns
    -------
    str
        A Markdown-formatted version of the persona.
    """
    lines = text.splitlines()
    md_lines: list[str] = []

    section_emojis = (
        "🎯", "🤔", "🗣️", "👨‍🎓", "😂", "🌎", "🚫", "💬", "✅"
    )

    for line in lines:
        stripped = line.strip()

        if any(stripped.startswith(emoji) for emoji in section_emojis):
            md_lines.append(f"## {stripped}")
        elif "Source:" in line:
            parts = line.split("Source:")
            text_part = parts[0].strip()
            url_part = parts[1].strip()
            md_lines.append(
                f"- {text_part}  \n  **Source:** [{url_part}]({url_part})"
            )
        else:
            md_lines.append(line)

    return "\n".join(md_lines)

def score_by_citations(text: str) -> float:
    """
    Simple heuristic: More citations = higher confidence.
    Base score is 0.5, and each citation adds 0.1, capped at 1.0.
    """
    count = text.count("Citation:")
    return min(1.0, 0.5 + 0.1 * count)


def parse_persona_to_json(text: str) -> dict:
    """
    Parse the plain text persona into a structured JSON with confidence scores.

    Returns
    -------
    dict
        Structured version of the persona with "value" and "confidence" per section.
    """
    sections = {
        "🎯": "interests",
        "🤔": "personality_traits",
        "🗣️": "tone_of_writing",
        "👨‍🎓": "profession_or_education",
        "😂": "humor_or_style",
        "🌎": "political_or_social_leanings",
        "🚫": "limitations",
        "💬": "representative_quote",
        "✅": "goals_and_needs",
    }

    output = {}
    current_section = None
    buffer = []

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        for emoji, key in sections.items():
            if line.startswith(emoji):
                # Save previous section if applicable
                if current_section and buffer:
                    section_text = "\n".join(buffer).strip()
                    output[current_section] = {
                        "value": section_text,
                        "confidence": round(score_by_citations(section_text), 2)
                    }
                current_section = key
                buffer = [line]
                break
        else:
            buffer.append(line)

    # Save the last section
    if current_section and buffer:
        section_text = "\n".join(buffer).strip()
        output[current_section] = {
            "value": section_text,
            "confidence": round(score_by_citations(section_text), 2)
        }

    return output

def map_to_frameworks(persona_text: str) -> dict:
    """
    Ask Gemini to map the user's persona to MBTI and Big Five traits.

    Returns
    -------
    dict with keys: "MBTI", "BigFive", or {} on failure
    """
    prompt = f"""
    Analyze the following Reddit user persona and map it to psychological frameworks.

    Return only a JSON object in the format:
    {{
    "MBTI": "INTP",
    "BigFive": {{
        "openness": 0.85,
        "conscientiousness": 0.67,
        "extraversion": 0.22,
        "agreeableness": 0.74,
        "neuroticism": 0.44
    }}
    }}

    Avoid any explanation, markdown, or additional text.

    Persona:
    ----------------
    {persona_text}
    """

    try:
        response = _GEMINI_MODEL.generate_content(prompt)
        text = response.text.strip()
         # Remove markdown-style fences (e.g. ```json ... ```)
        if text.startswith("```"):
            text = text.strip("`")           # removes all backticks
            text = re.sub(r'^json\n', '', text, flags=re.IGNORECASE)  # remove 'json' if present
            text = text.strip()
        return json.loads(text)
    except Exception as e:
        print("⚠️ Gemini framework mapping failed:", e)
        print("📝 Raw response was:", response.text)
        return {}


