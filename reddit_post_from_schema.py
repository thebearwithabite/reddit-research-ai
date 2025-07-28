import praw
import os
import yaml
import traceback
from datetime import datetime, timedelta
import time

OUTBOX_DIR = "outbox"
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5 # seconds

def create_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="MCP Agent Bot"
    )

def log_to_outbox(content, suffix="log"):
    if not os.path.exists(OUTBOX_DIR):
        os.makedirs(OUTBOX_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTBOX_DIR}/{timestamp}.{suffix}"
    with open(filename, "w") as f:
        f.write(content)

def load_schema(filepath="schemas/post_schema.yaml"):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

def post_to_reddit(schema, reddit, publish=False):
    # Check scheduled_at
    scheduled_at_str = schema.get("scheduled_at")
    if scheduled_at_str:
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str)
            if datetime.now() < scheduled_at:
                log_to_outbox(f"Post \"{schema['title']}\" is scheduled for {scheduled_at}. Skipping for now.", "info")
                return f"Post scheduled for {scheduled_at}."
        except ValueError:
            log_to_outbox(f"Invalid scheduled_at format: {scheduled_at_str}", "err")
            return f"Error: Invalid scheduled_at format."

    for attempt in range(MAX_RETRIES):
        try:
            subreddit = reddit.subreddit(schema["subreddit"])

            # Flair
            flair_text = schema.get("flair_text")
            flair_id = None
            if flair_text:
                for flair in subreddit.flair.link_templates:
                    if flair["text"].lower() == flair_text.lower():
                        flair_id = flair["id"]
                        break

            # Post body or crosspost
            if "crosspost_to" in schema:
                parent = subreddit.submit(
                    title=schema["title"],
                    selftext=schema["body"] if "body" in schema else ""
                )
                results = [f"✅ Original post: r/{schema['subreddit']} → {parent.url}"]
                for sub in schema["crosspost_to"]:
                    cp = reddit.subreddit(sub).submit_crosspost(parent)
                    results.append(f"↪️ Crossposted to r/{sub}: {cp.url}")
                log_to_outbox("\n".join(results))
                return "\n".join(results)

            else:
                if publish:
                    submission = subreddit.submit(
                        title=schema["title"],
                        selftext=schema["body"],
                        flair_id=flair_id
                    )
                    log_to_outbox(f"✅ Posted to r/{schema['subreddit']}: {submission.url}")
                    return f"✅ Posted to r/{schema['subreddit']}: {submission.url}"
                else:
                    # Draft Mode
                    draft_preview = (
                        f" Draft mode: no post submitted.\n"
                        f"Title: {schema['title']}\n"
                        f"Subreddit: {schema['subreddit']}\n"
                        f"Body:\n{schema['body']}\n"
                    )
                    if schema.get("markdown_draft"):
                        with open(schema["markdown_draft"], "w") as f:
                            f.write(schema["body"])
                        draft_preview += f"( Markdown saved to {schema['markdown_draft']})\n"
                    log_to_outbox(draft_preview, "draft")
                    return draft_preview

        except Exception as e:
            error_log = f"❌ Reddit post failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}\n{traceback.format_exc()}"
            log_to_outbox(error_log, "err")
            if attempt < MAX_RETRIES - 1:
                time.sleep(INITIAL_RETRY_DELAY * (2 ** attempt)) # Exponential backoff
            else:
                return error_log # All retries failed

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("schema_path", help="Path to post_schema.yaml")
    parser.add_argument("--publish", action="store_true", help="Force publish")
    args = parser.parse_args()

    schema = load_schema(args.schema_path)
    reddit = create_reddit_client()
    publish = args.publish or schema.get("publish", False)

    result = post_to_reddit(schema, reddit, publish=publish)
    print(result)
