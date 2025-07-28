import yaml
import praw
import os
from datetime import datetime

# --- Load Schema ---
def load_schema(path="post_schema.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# --- Validate Fields (basic) ---
def validate_schema(data):
    required = ["title", "subreddit"]
    if not (data.get("body") or data.get("url") or data.get("crosspost_id")):
        raise ValueError("One of 'body', 'url', or 'crosspost_id' is required.")
    return True

# --- Create Reddit Client ---
def create_reddit_client():
    return praw.Reddit(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        username="YOUR_USERNAME",
        password="YOUR_PASSWORD",
        user_agent="MCP Agent Bot"
    )

# --- Logging ---
def log_to_outbox(entry):
    os.makedirs("outbox", exist_ok=True)
    with open("outbox/results.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z :: {entry}\n")

# --- Post to Reddit ---
def post_to_reddit(schema):
    try:
        reddit = create_reddit_client()
        subreddit = reddit.subreddit(schema["subreddit"])

        # Determine post type
        if "crosspost_id" in schema:
            submission = reddit.submission(id=schema["crosspost_id"])
            post = subreddit.crosspost(submission, title=schema["title"])
        elif "url" in schema:
            post = subreddit.submit(title=schema["title"], url=schema["url"])
        else:
            post = subreddit.submit(title=schema["title"], selftext=schema["body"])

        # Add flair if specified
        if "flair_id" in schema:
            post.flair.select(schema["flair_id"])
        elif "flair_text" in schema:
            # Tries to match flair text automatically
            for flair in subreddit.flair.link_templates:
                if flair["text"].lower() == schema["flair_text"].lower():
                    post.flair.select(flair["id"])
                    break

        print(f"✅ Posted: {post.title} → {post.url}")
        log_to_outbox(f"Posted to r/{schema['subreddit']}: {post.url}")
        return post

    except Exception as e:
        error_msg = f"❌ Error posting to r/{schema.get('subreddit')}: {e}"
        print(error_msg)
        log_to_outbox(error_msg)

# --- Main Run ---
if __name__ == "__main__":
    schema = load_schema()

    try:
        validate_schema(schema)
    except ValueError as ve:
        print(f"❗Schema validation error: {ve}")
        log_to_outbox(f"❗Schema validation error: {ve}")
        exit(1)

    if schema.get("visibility", "draft").lower() == "public":
        post_to_reddit(schema)
    else:
        print(" Draft mode: post not submitted.")
        print(f"Title: {schema.get('title')}")
        print(f"Subreddit: {schema.get('subreddit')}")
        print("Body:")
        print(schema.get("body"))
        log_to_outbox(f" Draft preview – Title: {schema.get('title')}")