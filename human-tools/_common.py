"""Shared utilities for human-facing tools."""

import fcntl
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import yaml

CONVERSATIONS_DIR = Path("conversations")

# ANSI colors
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_all() -> list[dict]:
    """Return all conversations, sorted by filename."""
    convs = []
    for path in sorted(CONVERSATIONS_DIR.glob("*.yaml")):
        with open(path) as f:
            if data := yaml.safe_load(f):
                convs.append(data)
    return convs


@contextmanager
def human_conversation(
    conv_id: str, *, create: bool = False
) -> Generator[dict, None, None]:
    """Load a conversation; on exit set last=HUMAN and write it back (locked)."""
    path = CONVERSATIONS_DIR / f"{conv_id}.yaml"
    if not path.exists():
        if not create:
            print(f"Error: conversation '{conv_id}' not found", file=sys.stderr)
            sys.exit(1)
        path.touch()

    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        raw = f.read()
        data = yaml.safe_load(raw) if raw.strip() else {"id": conv_id, "history": []}
        yield data
        data["last"] = "HUMAN"
        f.seek(0)
        f.truncate()
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
    # lock released on file close


def format_status(data: dict) -> str:
    if data.get("escalated"):
        return f"{RED}escalated{RESET}"
    if data.get("no_further_action"):
        return f"{DIM}no further action{RESET}"
    if s := data.get("scheduled"):
        return f"{GREEN}scheduled {s['date']} {s['time']}{RESET}"
    last = data.get("last", "?")
    color = CYAN if last == "HUMAN" else YELLOW
    return f"active ({color}{last}{RESET} spoke last)"


def print_history(data: dict) -> None:
    for line in data.get("history", []):
        if line.startswith("$$HUMAN$$"):
            print(f"  {CYAN}{line}{RESET}")
        elif line.startswith("$$BOT$$"):
            print(f"  {YELLOW}{line}{RESET}")
        else:
            print(f"  {line}")
