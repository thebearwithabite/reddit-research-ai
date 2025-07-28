# reddit_post_from_schema.py
# Production-ready Reddit posting agent with draft preview, error handling, flair, crossposting, logging, and markdown export.

import praw
import os
import yaml
from datetime import datetime
from slugify import slugify

# ========== Configuration ==========
REDDIT_LOG_FILE = "outbox/results.log"
REDDIT_ERROR_LOG = "outbox/errors.log"
POST_EXPORT_DIR = "outbox/posts"

# ========== Create Reddit Client ==========
def create_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="MCP Agent Bot"
    )

# ========== Markdown Export ==========
def export_markdown(schema):
    os.makedirs(POST_EXPORT_DIR, exist_ok=True)
    filename = f"{POST_EXPORT_DIR}/{slugify(schema['title'])}.md"
    with open(filename, "w") as f:
        f.write(f"# {schema['title']}\n\n{schema['body']}")

# ========== Logging ==========
def log_to_file(path, content):
    with open(path, "a") as log:
        log.write(f"[{datetime.now()}] {content}\n")

# ========== Load Schema ==========
def load_schema(schema_path):
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)

# ========== Post to Reddit ==========
def post_to_reddit(schema, draft_mode=True):
    reddit = create_reddit_client()
    subreddit = reddit.subreddit(schema["subreddit"])

    if draft_mode:
        print(" Draft mode: no post submitted.")
        print(f"Title: {schema['title']}")
        print(f"Subreddit: {schema['subreddit']}")
        print(f"Body:\n{schema['body']}")
        if schema.get("flair_text") or schema.get("flair_id"):
            print(f"Flair: {schema.get('flair_text') or schema.get('flair_id')}")
        export_markdown(schema)
        log_to_file(REDDIT_LOG_FILE, f" Draft preview: {schema['title']}")
        return

    try:
        if "crosspost_id" in schema:
            submission = reddit.submission(id=schema["crosspost_id"]).crosspost(
                subreddit=subreddit,
                title=schema["title"]
            )
        elif "url" in schema:
            submission = subreddit.submit(
                title=schema["title"],
                url=schema["url"]
            )
        else:
            submission = subreddit.submit(
                title=schema["title"],
                selftext=schema["body"]
            )

        if "flair_id" in schema or "flair_text" in schema:
            submission.flair.select(
                flair_template_id=schema.get("flair_id"),
                text=schema.get("flair_text")
            )

        log_to_file(REDDIT_LOG_FILE, f"✅ Posted: {schema['title']} to r/{schema['subreddit']} ({submission.id})")
        print(f"✅ Successfully posted: https://reddit.com{submission.permalink}")

    except Exception as e:
        print(f"❌ Error posting to Reddit: {e}")
        log_to_file(REDDIT_ERROR_LOG, f"❌ Error: {e} | Title: {schema['title']}")

# ========== Entry Point ==========
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("schema_path", help="Path to post_schema.yaml")
    parser.add_argument("--publish", action="store_true", help="Force publish")
    args = parser.parse_args()

    schema = load_schema(args.schema_path)
    draft_mode = not args.publish and schema.get("draft", True)

    post_to_reddit(schema, draft_mode=draft_mode)