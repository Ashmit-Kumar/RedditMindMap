import google.generativeai as genai
import praw
import os
import re

# Setup Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Setup Reddit
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="persona-generator-script"
)

def extract_username(url):
    match = re.search(r'reddit.com/user/([^/]+)', url)
    return match.group(1) if match else None

def scrape_user_data(username):
    user = reddit.redditor(username)
    posts = [{
        "text": post.title + "\n" + post.selftext,
        "url": f"https://reddit.com{post.permalink}"
    } for post in user.submissions.new(limit=30)]

    comments = [{
        "text": comment.body,
        "url": f"https://reddit.com{comment.permalink}"
    } for comment in user.comments.new(limit=30)]

    return posts, comments

def generate_persona(posts, comments):
    examples = []
    for p in posts + comments:
        examples.append(f"{p['text']}\nSource: {p['url']}")

    prompt = f"""You are an AI assistant tasked with analyzing a Reddit user based on their posts and comments.
Create a user persona that includes:

- Interests
- Personality traits
- Tone of writing
- Political or social leanings (if any)
- Possible profession or education
- Language style or humor
- Citations for each trait (use URLs from posts/comments)

Content:
{'-'*80}
{chr(10).join(examples[:50])}
"""

    response = model.generate_content(prompt)
    return response.text

def save_persona(username, persona):
    with open(f"{username}_persona.txt", "w") as f:
        f.write(persona)
