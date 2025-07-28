#reddit_poster.py
#
#
#You can drop it into your /tools or /plugins directory (depending on how your MCP agent resolves #toolpaths), then register it in your brain.py or agent_config.yaml like so:
#from tools.reddit_poster import RedditPosterTool
#self.tools.append(RedditPosterTool())
"""
Reddit Posting Tool for MCP Agent
Requirements: praw (Python Reddit API Wrapper)
"""

import praw
import os

class RedditPoster:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD")
        )

    def use(self, task):
        """
        Task format:
        {
          "tool": "reddit",
          "subreddit": "NameOfSubreddit",
          "title": "Post Title",
          "body": "Post content here."
        }
        """
        if task.get("tool") != "reddit":
            return None  # Not our job

        try:
            subreddit = self.reddit.subreddit(task["subreddit"])
            submission = subreddit.submit(
                title=task["title"],
                selftext=task["body"]
            )
            return f"✅ Posted to r/{task['subreddit']}: {submission.url}"
        except Exception as e:
            return f"❌ Reddit post failed: {str(e)}"

# Example use
if __name__ == "__main__":
    poster = RedditPoster()
    test_task = {
        "tool": "reddit",
        "subreddit": "test",
        "title": "Hello from MCP",
        "body": "This is a test post."
    }
    print(poster.use(test_task))
