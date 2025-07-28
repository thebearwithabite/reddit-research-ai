# agent_loop.py — Core loop for running MCP agents

import time
import argparse
import yaml
from agents.core import Agent


def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='mcp_config.yaml')
    args = parser.parse_args()

    config = load_config(args.config)
    agent = Agent(config)

    print("[MCP] Agent starting main loop...")
    while True:
        try:
            agent.step()
        except Exception as e:
            print("[MCP] Error in step:", e)
        time.sleep(config.get('poll_interval', 300))  # default: every 5 minutes


if __name__ == '__main__':
    main()