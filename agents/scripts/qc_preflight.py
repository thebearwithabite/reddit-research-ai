import sys, json, re

BANNED = [
  r"\bsubscribe\b", r"\bnewsletter\b", r"\bCTR\b", r"\bad spend\b",
  r"\bgrowth hacking\b", r"\bpromo code\b"
]

def main(path):
    data = json.load(open(path))
    if isinstance(data, dict):
        items = [data]
    else:
        items = data
    for item in items:
        text = (item.get("title","") + " " + item.get("body","")).lower()
        for pattern in BANNED:
            if re.search(pattern, text):
                raise SystemExit(f"QC BLOCK: matched '{pattern}'")
    print("QC PASS:", path)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "data/agent_instruction.json")