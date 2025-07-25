import os
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
from typing import List, Optional

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_usernames(batch_size: int = 2, lock_id: Optional[str] = None) -> List[dict]:
    """
    Fetch a batch of unlocked usernames and lock them for processing.
    """
    lock_id = lock_id or str(uuid.uuid4())
    response = (
        supabase.table("reddit_usernames")
        .select("*")
        .eq("locked", False)
        .limit(batch_size)
        .execute()
    )

    users = response.data
    if not users:
        return []

    # Lock the users
    ids = [user["id"] for user in users]
    supabase.table("reddit_usernames").update({
        "locked": True,
        "lock_id": lock_id
    }).in_("id", ids).execute()

    return users


def unlock_usernames(lock_id: str):
    """
    Unlock previously locked usernames using the lock_id.
    """
    supabase.table("reddit_usernames").update({
        "locked": False,
        "lock_id": None
    }).eq("lock_id", lock_id).execute()


def mark_username_processed(username: str):
    """
    Optionally mark a username as processed (e.g., store status/timestamp).
    """
    supabase.table("reddit_usernames").update({
        "processed": True
    }).eq("username", username).execute()
