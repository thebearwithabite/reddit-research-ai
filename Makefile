VENV?=.venv
PY?=$(VENV)/bin/python

fetch:
	$(PY) agents/scripts/fetch_reddit.py --subs MachineLearning MLQuestions --post_limit 15 --mode hot --with_comments --output data/reddit_payload.json

triage:
	$(PY) agents/scripts/triage_agent.py --input data/reddit_payload.json --output data/agent_instruction.json

qc:
	$(PY) agents/scripts/qc_preflight.py data/agent_instruction.json

run-dry:
	DRY_RUN=1 $(PY) -m agents.agent1_main

run:
	$(PY) -m agents.agent1_main