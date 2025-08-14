#!/usr/bin/env python3
import os, json, argparse, time
import praw
from dotenv import load_dotenv
load_dotenv()

for k in ["REDDIT_CLIENT_ID","REDDIT_CLIENT_SECRET","REDDIT_USERNAME","REDDIT_PASSWORD","REDDIT_USER_AGENT"]:
    if not os.getenv(k):
        raise SystemExit(f"Missing env var: {k} (did you create .env and load it?)")

DEFAULT_SUBS = [
    "MachineLearning", "MLQuestions",
    "artificial", "ArtificialIntelligence",
    "deeplearning", "MediaSynthesis",
    "lectures"
]

def get_reddit():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "agent1 (by u/yourname)")
    )

from prawcore.exceptions import NotFound, Forbidden, Redirect, ResponseException, RequestException

def try_hot(sr_name, limit, mode):
    try:
        sr = reddit.subreddit(sr_name)
        it = getattr(sr, mode)(limit=limit)
        return list(it), None
    except (NotFound, Forbidden, Redirect) as e:
        return [], f"{sr_name}: {e.__class__.__name__} (private/quarantined/missing?)"
    except (ResponseException, RequestException) as e:
        return [], f"{sr_name}: API/network error: {type(e).__name__}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--subs", nargs="*", default=DEFAULT_SUBS)
    ap.add_argument("--post_limit", type=int, default=30)
    ap.add_argument("--mode", choices=["hot","new","top"], default="hot")
    ap.add_argument("--with_comments", action="store_true")
    ap.add_argument("--output", default="data/reddit_payload.json")
    args = ap.parse_args()

    os.makedirs("data", exist_ok=True)
    reddit = get_reddit()

    payload, skips = [], []
    for sub in args.subs:
        posts, err = try_hot(sub, args.post_limit, args.mode)
        if err:
            skips.append(err); continue
        for s in posts:
            if getattr(s, "stickied", False):
                continue
            payload.append({
                "id": s.id,
                "subreddit": str(s.subreddit),
                "type": "post",
                "title": s.title or "",
                "selftext": s.selftext or "",
                "url": s.url if (s.url and not s.is_self) else None,
                "score": int(s.score or 0),
                "num_comments": int(s.num_comments or 0),
                "created_utc": int(s.created_utc or 0)
            })
        if args.with_comments:
            # light pause to be polite to API
            time.sleep(0.5)
            comments, err = try_hot(sub, min(10, args.post_limit), "hot") # comments are always hot
            if err:
                skips.append(err); continue
            for s in comments:
                s.comments.replace_more(limit=0)
                for c in s.comments[:15]: # comment_limit=15
                    payload.append({
                        "id": c.id,
                        "subreddit": str(s.subreddit),
                        "type": "comment",
                        "title": None,
                        "body": c.body or "",
                        "url": f"https://www.reddit.com{c.permalink}",
                        "score": int(c.score or 0),
                        "num_comments": 0,
                        "created_utc": int(c.created_utc or 0)
                    })
    print("Skipped:", skips)

    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {len(payload)} items to {args.output}")