# agents/core.py

import os
import json
from agents.brain import ask_model

class Agent:
    def __init__(self, config):
        self.config = config
        self.default_model = config.get("default_model", "gpt-4")
        self.tools = config.get("tools", [])
        self.memory = []

    def step(self):
        prompt = self.get_task()
        if not prompt:
            print("[MCP] No task found in inbox.")
            return

        print("[MCP] Task received:\n", prompt)
        try:
            response = ask_model(prompt, model=self.default_model)
        except Exception as e:
            print(f"[MCP] Model call failed: {e}")
            response = "[ERROR] No response generated."

        print("[MCP] Response:\n", response)

        # Save task + response to memory log
        self.memory.append({"prompt": prompt, "response": response})
        self.save_to_outbox(prompt, response)

    def get_task(self):
        inbox_path = "inbox/task.txt"
        if not os.path.exists(inbox_path):
            return None
        with open(inbox_path, "r") as f:
            task = f.read().strip()
        os.remove(inbox_path)
        return task

    def save_to_outbox(self, prompt, response):
        os.makedirs("outbox", exist_ok=True)
        with open("outbox/last_response.json", "w") as f:
            json.dump({"prompt": prompt, "response": response}, f, indent=2)
        print("[MCP] Response saved to outbox/last_response.json")

# --- lightweight prompt packer used by agent1_main.py ---
def process_agent_prompt(title: str, body: str, link: str | None, context_snippets: list[str] | None = None):
    """
    Combines the instruction fields with retrieved memory snippets into a single prompt
    that downstream LLM code can use. Returns a dict; downstream can return either
    a finalized post or echo this back unchanged.
    """
    context_snippets = context_snippets or []
    ctx = ""
    if context_snippets:
        ctx = "\n\n---\nPrior related context (for tone/framing only):\n" + "\n".join(
            f"- {s}" for s in context_snippets
        )
    return {
        "title": title.strip(),
        "body": (body.strip() + ctx).strip(),
        "link": link
    }