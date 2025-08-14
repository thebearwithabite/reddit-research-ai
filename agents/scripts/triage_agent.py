import json
from datetime import datetime, timezone
from typing import List, Dict

# Adjust these filters as needed
MIN_COMMENTS = 3
MIN_SCORE = 1
KEY_SUBREDDITS = ["MachineLearning", "artificial", "lectures", "ArtificialIntelligence"]

def load_reddit_payload(path: str) -> List[Dict]:
    """Load scraped subreddits/posts JSON file for triaging."""
    with open(path, "r") as f:
        return json.load(f)

def is_relevant(item: Dict) -> bool:
    """Basic filtering based on subreddit, score, comments, and type."""
    if item.get("subreddit") not in KEY_SUBREDDITS:
        return False
    if item.get("type") == "post" and (
        item.get("score", 0) < MIN_SCORE or item.get("num_comments", 0) < MIN_COMMENTS
    ):
        return False
    # Accept all comments for context relevance
    return True

def format_instruction_bundle(item: Dict) -> Dict:
    """Convert a Reddit post/comment into agent instruction components."""
    title = item.get("title") or f"Comment in {item.get('subreddit')}"
    body = item.get("selftext") or item.get("body", "")
    link = item.get("url") if item.get("type") == "post" else None

    return {
        "id": f"{item.get('subreddit')}_{item.get('id')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subreddit": item.get("subreddit"),
        "type": item.get("type"),
        "title": title[:300],
        "body": body,
        "link": link
    }

def triage_and_write(input_path: str, output_path: str):
    items = load_reddit_payload(input_path)
    bundles = [format_instruction_bundle(i) for i in items if is_relevant(i)]

    if not bundles:
        print("No relevant items found.")
        return

    with open(output_path, "w") as f:
        json.dump(bundles, f, indent=2)

    print(f"Wrote {len(bundles)} instruction bundles to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Triage Reddit data into agent instruction bundles")
    parser.add_argument("--input", default="data/reddit_payload.json")
    parser.add_argument("--output", default="data/agent_instruction.json")
    args = parser.parse_args()

    triage_and_write(args.input, args.output)

