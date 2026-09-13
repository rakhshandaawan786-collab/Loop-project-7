"""
Morning Brief with Memory — now with failure handling.

Every run writes ONE clear log line to run.log, whether it succeeds or
fails. On failure, it also writes a "NEEDS HUMAN" note into progress.md
itself, so the spine (log + progress.md) tells the whole story without
anyone needing to replay the run.
"""

import json
import os
import re
import sys
from datetime import datetime

REPO_DIR = "sample_repo"
STATE_FILE = ".brief_state.json"
PROGRESS_FILE = "progress.md"
LOG_FILE = "run.log"

TODO_PATTERN = re.compile(r"TODO[:\s](.*)")


def log(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {level}: {message}\n")


def scan_todos(repo_dir):
    if not os.path.isdir(repo_dir):
        raise FileNotFoundError(f"REPO_DIR does not exist: '{repo_dir}'")

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
                        todos[f"{path}::{text}"] = lineno
    return todos


def load_state(state_file):
    if not os.path.exists(state_file):
        return {}
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state_file, todos):
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, sort_keys=True)


def append_progress(progress_file, text):
    if not os.path.exists(progress_file):
        with open(progress_file, "w", encoding="utf-8") as f:
            f.write("# Progress Log\n")
    with open(progress_file, "a", encoding="utf-8") as f:
        f.write(text)


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        previous = load_state(STATE_FILE)
        current = scan_todos(REPO_DIR)

        new_todos = {k: v for k, v in current.items() if k not in previous}
        resolved_todos = {k: v for k, v in previous.items() if k not in current}

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

        append_progress(PROGRESS_FILE, "".join(lines))
        save_state(STATE_FILE, current)

        log("OK", f"run succeeded — {len(current)} TODOs tracked, "
                   f"{len(new_todos)} new, {len(resolved_todos)} resolved")
        print(f"Run succeeded. See {PROGRESS_FILE} and {LOG_FILE}.")
        sys.exit(0)

    except Exception as e:
        # THE KEY PART: never fail silently. Log it, and leave a note
        # in progress.md itself — the next reader of the spine sees it
        # without needing to re-run anything.
        log("ERROR", f"run FAILED — {type(e).__name__}: {e}")
        append_progress(
            PROGRESS_FILE,
            f"\n## {today}\n**⚠️ NEEDS HUMAN — run failed:** {type(e).__name__}: {e}\n"
        )
        print(f"Run FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
