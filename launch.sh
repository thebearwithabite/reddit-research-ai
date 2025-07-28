#!/bin/bash

#  LAUNCH.SH — Starts the MCP agent

CONFIG_FILE="mcp_config.yaml"
LOG_FILE="logs/agent.log"

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the main loop and log output
echo "Starting MCP agent with config: $CONFIG_FILE"
python3 agent_loop.py --config $CONFIG_FILE | tee $LOG_FILE