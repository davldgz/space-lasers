#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# tasks.json lives in the repo root
DATA_FILE = Path(__file__).resolve().parents[2] / "tasks.json"

def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def _load() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def _save(tasks: List[Dict[str, Any]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def _next_id(tasks: List[Dict[str, Any]]) -> int:
    return (max((t["id"] for t in tasks), default=0) + 1)

def cmd_add(args: argparse.Namespace) -> None:
    tasks = _load()
    new_task = {
        "id": _next_id(tasks),
        "title": args.title.strip(),
        "status": "open",
        "created_at": _now_iso(),
        "done_at": None
    }
    tasks.append(new_task)
    _save(tasks)
    print(f"✅ added #{new_task['id']}: {new_task['title']}")

def cmd_list(args: argparse.Namespace) -> None:
    tasks = _load()
    if args.all:
        view = tasks
    elif args.done:
        view = [t for t in tasks if t["status"] == "done"]
    else:
        view = [t for t in tasks if t["status"] == "open"]

    if not view:
        print("🟡 no tasks to show.")
        return

    for t in view:
        status = "✅" if t["status"] == "done" else "📝"
        print(f"{status} #{t['id']:>3}  {t['title']}")

def cmd_done(args: argparse.Namespace) -> None:
    tasks = _load()
    tid = args.id
    for t in tasks:
        if t["id"] == tid:
            if t["status"] == "done":
                print(f"ℹ️ task #{tid} already done.")
            else:
                t["status"] = "done"
                t["done_at"] = _now_iso()
                _save(tasks)
                print(f"✅ completed #{tid}: {t['title']}")
            return
    print(f"❌ no task with id #{tid} found.")

def cmd_delete(args: argparse.Namespace) -> None:
    tasks = _load()
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != args.id]
    if len(tasks) == before:
        print(f"❌ no task with id #{args.id} found.")
    else:
        _save(tasks)
        print(f"🗑️ deleted task #{args.id}")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="task-tracker",
        description="A simple CLI task tracker that stores tasks in tasks.json"
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a new task")
    p_add.add_argument("title", help="task title (in quotes if it has spaces)")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list tasks")
    g = p_list.add_mutually_exclusive_group()
    g.add_argument("--done", action="store_true", help="show completed tasks only")
    g.add_argument("--all", action="store_true", help="show all tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="mark a task as done by id")
    p_done.add_argument("id", type=int, help="task id")
    p_done.set_defaults(func=cmd_done)

    p_del = sub.add_parser("delete", help="delete a task by id")
    p_del.add_argument("id", type=int, help="task id")
    p_del.set_defaults(func=cmd_delete)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    _ = _load()
    args.func(args)

if __name__ == "__main__":
    main()

