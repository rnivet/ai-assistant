#!/usr/bin/env python3
"""
CLI client for the AI Memory API.
Usage:
    ./memory.py store "Remi préfère Python pour le backend" --category user
    ./memory.py search "préférences langage de programmation"
    ./memory.py recent --limit 10
    ./memory.py delete 42
    ./memory.py sql "SELECT * FROM structured.notes ORDER BY created_at DESC"
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = os.environ.get("MEMORY_API_URL", "http://localhost:8765")


def _request(method: str, path: str, data: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("MEMORY_API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return {}
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        print(f"Error {e.code}: {error.get('detail', e.reason)}", file=sys.stderr)
        sys.exit(1)


def cmd_store(args):
    payload = {"content": args.content, "category": args.category, "source": "manual"}
    if args.summary:
        payload["summary"] = args.summary
    if args.tags:
        payload["tags"] = args.tags
    mem = _request("POST", "/memories", payload)
    print(f"Stored memory #{mem['id']}: {mem['content'][:80]}")


def cmd_search(args):
    params = f"q={urllib.parse.quote(args.query)}&limit={args.limit}"
    if args.category:
        params += f"&category={args.category}"
    result = _request("GET", f"/memories/search?{params}")
    for m in result["memories"]:
        sim = f" [{m['similarity']:.2f}]" if m.get("similarity") else ""
        print(f"#{m['id']} [{m['category']}]{sim} {m['content'][:120]}")
    if not result["memories"]:
        print("No memories found.")


def cmd_recent(args):
    params = f"limit={args.limit}"
    if args.category:
        params += f"&category={args.category}"
    result = _request("GET", f"/memories/recent?{params}")
    for m in result["memories"]:
        ts = m["created_at"][:19]
        print(f"#{m['id']} [{m['category']}] {ts}  {m['content'][:100]}")
    if not result["memories"]:
        print("No memories found.")


def cmd_delete(args):
    _request("DELETE", f"/memories/{args.id}")
    print(f"Deleted memory #{args.id}")


def cmd_sql(args):
    result = _request("POST", "/structured/query", {"sql": args.sql})
    if result["rows"]:
        for row in result["rows"]:
            print(json.dumps(row, default=str))
    else:
        print(f"Query OK, {result['count']} rows.")


def cmd_tables(args):
    result = _request("GET", "/structured/tables")
    for t in result["tables"]:
        print(f"{t['table_name']}  ({t['size']})")
    if not result["tables"]:
        print("No structured tables yet.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Memory CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # store
    p = sub.add_parser("store", help="Save a memory")
    p.add_argument("content")
    p.add_argument("--category", default="general",
                   choices=["general", "user", "feedback", "project", "reference", "fact"])
    p.add_argument("--summary")
    p.add_argument("--tags", nargs="*", default=[])
    p.set_defaults(func=cmd_store)

    # search
    p = sub.add_parser("search", help="Semantic search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--category")
    p.set_defaults(func=cmd_search)

    # recent
    p = sub.add_parser("recent", help="Recent memories (chronological)")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--category")
    p.set_defaults(func=cmd_recent)

    # delete
    p = sub.add_parser("delete", help="Delete a memory by ID")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_delete)

    # sql
    p = sub.add_parser("sql", help="Run SQL in structured schema")
    p.add_argument("sql")
    p.set_defaults(func=cmd_sql)

    # tables
    p = sub.add_parser("tables", help="List structured schema tables")
    p.set_defaults(func=cmd_tables)

    args = parser.parse_args()
    args.func(args)
