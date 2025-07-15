import praw
import openai
import re
import os

# Reddit API setup (put your keys here or use dotenv)
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="persona-generator-script"
)

openai.api_key = os.getenv("OPENAI_API_KEY")

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

    prompt = f"""You are an AI analyst. Based on the Reddit user's posts and comments below,
generate a detailed user persona. Include:
- Interests
- Writing style
- Tone
- Political or social leanings
- Any personal/professional clues
- Supported by citations (post or comment links)

Content:
{'-'*80}
{chr(10).join(examples[:50])}
"""

    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content

def save_persona(username, persona):
    with open(f"{username}_persona.txt", "w") as f:
        f.write(persona)
