"""
Morning Brief with Memory
--------------------------
A scheduled loop's SINGLE run. Meant to be triggered by cron / Task
Scheduler once a day (see README). Each run:

  1. Reads .brief_state.json  <- THE SPINE (what we saw last time)
  2. Scans the repo for TODO comments right now
  3. Diffs against the spine to find what's NEW since last run
  4. Appends a short dated entry to progress.md (only the new stuff)
  5. Overwrites the spine with the current full picture, for next time

This is what makes the second run "remember" the first: the spine file
persists between runs, so nothing gets reported twice.
"""

import json
import os
import re
from datetime import datetime

REPO_DIR = "sample_repo"
STATE_FILE = ".brief_state.json"
PROGRESS_FILE = "progress.md"

TODO_PATTERN = re.compile(r"TODO[:\s](.*)")


def scan_todos(repo_dir):
    """Return a dict of {'file::todo text': line_number} for every TODO found.

    Keyed by content, not line number, so an unrelated edit above a TODO
    (which shifts its line number) doesn't make it look resolved+new.
    """
    todos = {}
    for root, _, files in os.walk(repo_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(root, fname)
            with open(path, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, start=1):
                    match = TODO_PATTERN.search(line)
                    if match:
                        text = match.group(1).strip()
                        key = f"{path}::{text}"
                        todos[key] = lineno
    return todos


def load_state(state_file):
    if not os.path.exists(state_file):
        return {}
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state_file, todos):
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, sort_keys=True)


def append_progress(progress_file, new_todos, resolved_todos):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [f"\n## {today}\n"]

    if new_todos:
        lines.append(f"**New TODOs found ({len(new_todos)}):**\n")
        for key, lineno in new_todos.items():
            path, text = key.split("::", 1)
            lines.append(f"- `{path}:{lineno}` — {text}\n")
    else:
        lines.append("No new TODOs since last run.\n")

    if resolved_todos:
        lines.append(f"\n**Resolved since last run ({len(resolved_todos)}):**\n")
        for key, lineno in resolved_todos.items():
            path, text = key.split("::", 1)
            lines.append(f"- `{path}:{lineno}` — {text}\n")

    entry = "".join(lines)

    if not os.path.exists(progress_file):
        with open(progress_file, "w", encoding="utf-8") as f:
            f.write("# Progress Log\n")

    with open(progress_file, "a", encoding="utf-8") as f:
        f.write(entry)

    return entry


def main():
    previous = load_state(STATE_FILE)
    current = scan_todos(REPO_DIR)

    new_todos = {k: v for k, v in current.items() if k not in previous}
    resolved_todos = {k: v for k, v in previous.items() if k not in current}

    entry = append_progress(PROGRESS_FILE, new_todos, resolved_todos)
    save_state(STATE_FILE, current)

    print("=== Morning Brief ===")
    print(entry)
    print(f"(Total TODOs tracked now: {len(current)}. Spine updated: {STATE_FILE})")


if __name__ == "__main__":
    main()
