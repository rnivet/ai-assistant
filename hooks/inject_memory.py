#!/usr/bin/env python3
"""
UserPromptSubmit hook — searches the memory API for context relevant to the
user's message and injects it so Claude sees it before responding.

Claude Code passes the event as JSON on stdin.
Any text printed to stdout is injected into the conversation context.
Exit code 0 = proceed, non-zero = block (we never block).
"""
import json
import os
import sys
import urllib.request
import urllib.parse

BASE_URL = os.environ.get("MEMORY_API_URL", "http://localhost:8765")
SEARCH_LIMIT = 5
MIN_SIMILARITY = 0.25  # ignore low-relevance results


def search(query: str) -> list[dict]:
    url = f"{BASE_URL}/memories/search?q={urllib.parse.quote(query)}&limit={SEARCH_LIMIT}"
    headers = {}
    token = os.environ.get("MEMORY_API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            return [m for m in data["memories"] if (m.get("similarity") or 0) >= MIN_SIMILARITY]
    except Exception:
        return []


def main():
    try:
        event = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    message = event.get("prompt", "")
    if not message.strip():
        sys.exit(0)

    memories = search(message[:500])
    if not memories:
        sys.exit(0)

    lines = ["<memory>", "Relevant memories retrieved automatically:"]
    for m in memories:
        sim = f" [{m['similarity']:.2f}]" if m.get("similarity") else ""
        cat = m.get("category", "")
        lines.append(f"- [{cat}]{sim} {m['content']}")
    lines.append("</memory>")

    output = {
        "suppressOutput": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n".join(lines),
        },
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
