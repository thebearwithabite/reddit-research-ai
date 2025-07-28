import praw
import os
import yaml
import traceback
from datetime import datetime

OUTBOX_DIR = "outbox"

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

def load_schema(filepath="post_schema.yaml"):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

def post_to_reddit(schema, reddit, publish=False):
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
            return "\n".join(results)

        else:
            if publish:
                submission = subreddit.submit(
                    title=schema["title"],
                    selftext=schema["body"],
                    flair_id=flair_id
                )
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
                return draft_preview

    except Exception as e:
        error_log = f"❌ Reddit post failed: {str(e)}\n{traceback.format_exc()}"
        log_to_outbox(error_log, "err")
        return error_log

if __name__ == "__main__":
    schema = load_schema()
    reddit = create_reddit_client()
    publish = schema.get("publish", False)

    result = post_to_reddit(schema, reddit, publish=publish)
    log_to_outbox(result)
    print(result)