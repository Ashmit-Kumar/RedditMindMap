import os
import time
import uuid
import logging
from supabase import create_client, Client
from persona_utils import scrape_user_data, generate_persona
from github_utils import push_to_github
from vector_db import push_to_vector_db
from env_loader import load_env

config = load_env()

# Example usage:
github_token = config["GITHUB_TOKEN"]
supabase_url = config["SUPABASE_URL"]

# ENV VARS
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GITHUB_REPO =  os.getenv("GITHUB_REPO")  # e.g. "username/repo"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REDDIT_TABLE = os.getenv("REDDIT_TABLE")
LOCK_ID = str(uuid.uuid4())

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logging.basicConfig(level=logging.INFO)

BATCH_SIZE = 2
SLEEP_SECONDS = 5

def fetch_usernames():
    response = (
        supabase.table(f"{REDDIT_TABLE}")
        .select("*")
        .eq("processed", False)
        .eq("locked", False)
        .limit(BATCH_SIZE)
        .execute()
    )
    return response.data if response.data else []

def lock_user(user):
    supabase.table(f"{REDDIT_TABLE}").update({
        "locked": True,
        "lock_id": LOCK_ID
    }).eq("id", user["id"]).execute()

def unlock_user(user):
    supabase.table(f"{REDDIT_TABLE}").update({
        "locked": False,
        "lock_id": None
    }).eq("id", user["id"]).execute()

def mark_processed(user):
    supabase.table(f"{REDDIT_TABLE}").update({
        "processed": True,
        "locked": False,
        "lock_id": None
    }).eq("id", user["id"]).execute()

def process_user(user):
    username = user["username"]
    try:
        logging.info(f"Scraping data for {username}...")
        scraped_data = scrape_user_data(username)

        logging.info(f"Generating persona for {username}...")
        persona_files = generate_persona(scraped_data, username)
        # persona_files = { "json": path, "md": path, "txt": path }

        logging.info(f"Pushing files to GitHub for {username}...")
        push_to_github(persona_files, username, GITHUB_REPO, GITHUB_TOKEN)

        logging.info(f"Pushing to vector DB for {username}...")
        
        push_to_vector_db(username, scraped_data["summary"], metadata={"traits": scraped_data["traits"]})

        mark_processed(user)
        logging.info(f"Done: {username}")
    except Exception as e:
        logging.error(f"Error processing {username}: {str(e)}")
        unlock_user(user)

def main():
    logging.info("Starting RedditMindMap worker...")
    while True:
        users = fetch_usernames()
        if not users:
            logging.info("No usernames to process. Sleeping...")
            time.sleep(SLEEP_SECONDS)
            continue

        for user in users:
            lock_user(user)
            process_user(user)

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
