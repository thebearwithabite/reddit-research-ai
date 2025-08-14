import os
from datetime import datetime, timezone
from .core import process_agent_prompt  # assume this handles prompt construction and LLM call
from .brain import reddit_post_from_instruction  # optionally splits logic
from .scripts.vector_indexer import retrieve_context
import json
import praw  # or other Reddit API wrapper

# Load configuration
AGENT_SUBREDDIT = os.getenv("TARGET_SUBREDDIT", "MachineLearning")
MAX_CONTEXT = int(os.getenv("MAX_CONTEXT", 3))

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "agent1 (by u/unknown)")
)

from praw.exceptions import RedditAPIException

def fetch_submission_flairs(reddit, sub_name: str):
    """Return [{'id': ..., 'text': ...}, ...] for submission (link) flairs."""
    sr = reddit.subreddit(sub_name)
    templates = []
    # Try official PRAW accessor first
    try:
        templates = list(sr.flair.link_templates)
    except Exception:
        # Fallback to raw v2 endpoint (works even if not a mod)
        try:
            templates = reddit._core._requestor.request("GET", f"/r/{sub_name}/api/link_flair_v2")
        except Exception:
            templates = []
    norm = []
    for t in templates or []:
        if isinstance(t, dict):
            tid = t.get("id") or t.get("template_id")
            txt = t.get("text") or t.get("flair_text")
        else:
            tid = getattr(t, "id", None)
            txt = getattr(t, "text", None)
        if tid and txt:
            norm.append({"id": tid, "text": txt})
    return norm

def choose_flair(templates, desired_text=None):
    """Pick a sensible flair by text match; fall back to first available."""
    wishlist = []
    if desired_text:
        wishlist.append(desired_text)
    env_wish = os.getenv("DEFAULT_FLAIR_TEXT")
    if env_wish:
        wishlist.append(env_wish)
    # common safe choices
    wishlist += ["Discussion", "Research", "Project", "Education", "Resource"]

    lw = [w.lower() for w in wishlist if w]
    for w in lw:
        for t in templates:
            if t["text"] and w in t["text"].lower():
                return t
    return templates[0] if templates else None

def main():
    # 1. Load prepared prompt context
    instruction_payload_path = "data/agent_instruction.json"
    if not os.path.exists(instruction_payload_path):
        print("Instruction bundle not found:", instruction_payload_path)
        return

    with open(instruction_payload_path, "r") as f:
        data = json.load(f)

    # accept either a single dict or a list of bundles
    if isinstance(data, list):
        # pick the first bundle for the target subreddit, prefer a post over a comment
        bundle = next((b for b in data if b.get("subreddit") == AGENT_SUBREDDIT and b.get("type") == "post"), None)
        bundle = bundle or data[0]
    else:
        bundle = data

    post_title = bundle["title"]
    post_body  = bundle.get("body") or bundle.get("selftext", "")
    link       = bundle.get("link")

    # 2. Retrieve memory context
    past_context = retrieve_context(AGENT_SUBREDDIT, post_body, top_k=MAX_CONTEXT)

    # 3. Combine into final prompt package
    final_prompt = process_agent_prompt(
        title=post_title,
        body=post_body,
        link=link,
        context_snippets=past_context
    )

    # 4. Generate output from core agent
    try:
        output = reddit_post_from_instruction(final_prompt)
        if not isinstance(output, dict) or "title" not in output:
            raise ValueError("Unexpected output from reddit_post_from_instruction")
    except Exception as e:
        # fallback: just use the prepared bundle
        output = {
            "title": post_title,
            "body": post_body + ("\n\n" + "\n".join(f"> {s}" for s in past_context) if past_context else ""),
            "link": link
        }

    # 5. Submit post
    print(f"DEBUG: output['title'] = {output['title']}")
    print(f"DEBUG: output['body'] = {output['body']}")
    print(f"DEBUG: output.get('link_based_on_structure') = {output.get('link_based_on_structure')}")

    post_params = {
        "title": output["title"],
    }

    submission_url = output.get("link_based_on_structure")
    if submission_url and not "reddit.com" in submission_url: # External URL, make it a link post
        post_params["url"] = submission_url
    else: # No URL or Reddit internal URL, make it a self-post
        post_params["selftext"] = output["body"]

    try:
        submission = reddit.subreddit(AGENT_SUBREDDIT).submit(**post_params)
    except RedditAPIException as e:
        needs_flair = any(getattr(err, "error_type", "") == "SUBMIT_VALIDATION_FLAIR_REQUIRED" for err in getattr(e, "items", []))
        if needs_flair:
            # Fetch available flairs and pick one
            flairs = fetch_submission_flairs(reddit, AGENT_SUBREDDIT)
            print("Available flairs:", [f"{t['text']} ({t['id']})" for t in flairs])
            picked = choose_flair(flairs, desired_text=os.getenv("DEFAULT_FLAIR_TEXT"))
            if not picked:
                raise  # nothing to pick; let it bubble up
            # attach flair_id and resubmit
            post_params["flair_id"] = picked["id"]
            post_params.pop("flair_text", None)
            submission = reddit.subreddit(AGENT_SUBREDDIT).submit(**post_params)
        else:
            raise

    print(f"Posted to r/{AGENT_SUBREDDIT}: {submission.id})")

    with open("logs/submissions.log","a") as f:
        f.write(f"{submission.id}\t{submission.permalink}\t{output['title']}\n")

    # 6. Log into vector memory store as new context
    from .scripts.vector_indexer import index_items
    index_items([{
        "id": submission.id,
        "text": output["title"] + "\n" + output["body"],
        "subreddit": AGENT_SUBREDDIT,
        "type": "post",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }])

if __name__ == "__main__":
    main()

