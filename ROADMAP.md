# Reddit Research AI - MCP Integration Roadmap

This document outlines the steps to fully integrate the Reddit Research AI agent into your existing GitHub-based Mission Control Platform (MCP) server setup.

## Phase 1: Environment Setup & Credential Management

1.  **Secure API Keys:**
    *   Ensure `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `GEMINI_KEY` are securely set as environment variables on your MCP server.
    *   Set Reddit API credentials: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`. These should also be environment variables on your server.

2.  **Install Dependencies:**
    *   On your MCP server, navigate to the `reddit-research-ai` directory.
    *   Install Python dependencies: `pip install -r requirements.txt`

3.  **Verify Agent Core:**
    *   Create a test task: `echo "Hello MCP, tell me a joke." > inbox/task.txt`
    *   Run the agent in draft mode: `./launch.sh`
    *   Check `outbox/last_response.json` for the AI's response.

## Phase 2: Reddit Posting Integration

1.  **Test Reddit Poster Tool (Draft Mode):**
    *   Modify `schemas/post_schema.yaml` with a test post (set `publish: false`).
    *   Run the `reddit_post_from_schema.py` script in draft mode:
        `python3 reddit_post_from_schema.py schemas/post_schema.yaml`
    *   Verify the draft output in the console and the generated markdown file in `outbox/posts/`.

2.  **Live Reddit Posting (Controlled Test):**
    *   **Crucial:** Create a dedicated test subreddit where you have full posting permissions.
    *   Update `schemas/post_schema.yaml` with your test subreddit and set `publish: true`.
    *   Run the script with the `--publish` flag:
        `python3 reddit_post_from_schema.py schemas/post_schema.yaml --publish`
    *   Verify the post appears on your test subreddit.

## Phase 3: Automation & Scheduling

1.  **Integrate with MCP Task Queue:**
    *   Adapt your MCP's task distribution mechanism to place Reddit post schemas (YAML or JSON) into the `inbox/` directory of the `reddit-research-ai` agent.
    *   The `agent_loop.py` will pick up `inbox/task.txt` (which could contain the path to a schema file or the schema content itself, requiring a small modification to `get_task` in `agents/core.py` to parse this).

2.  **Scheduled Posting:**
    *   Utilize the `scheduled_at` field in `post_schema.yaml` for time-gated posts.
    *   Ensure your MCP's cron job or scheduler runs `launch.sh` periodically (e.g., every 5-15 minutes) to allow the agent to check for new tasks and scheduled posts.

3.  **Error Handling & Monitoring:**
    *   Monitor `outbox/results.log` and `outbox/errors.log` for successful posts and failures.
    *   Implement alerts within your MCP for critical errors logged by the Reddit agent.

## Phase 4: Advanced Features & Refinements

1.  **Dynamic Schema Generation:**
    *   Develop MCP modules that use AI (via `agents/brain.py`) to dynamically generate `post_schema.yaml` files based on research findings or other inputs.

2.  **Tool Integration:**
    *   Explore integrating `tools/web_search.py` and `tools/file_tools.py` into the agent's workflow for more complex tasks (e.g., researching a topic, then generating a post).

3.  **Memory Integration:**
    *   Leverage the `memory/agent_001.db` (SQLite) for persistent agent memory, allowing the agent to remember past interactions or posting history.

4.  **Schema Validation in MCP:**
    *   Integrate `schema_validator.py` into your MCP's pre-processing pipeline to validate schemas before they are passed to the Reddit agent, preventing malformed posts.

---
**Secret MCP Tip:** For highly sensitive operations or to prevent accidental live posts during development, consider implementing a "dry-run" mode at the MCP level that intercepts `publish: true` flags and only simulates the posting process without actual API calls.
