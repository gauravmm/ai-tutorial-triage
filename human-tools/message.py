"""Interactive shell simulator: type messages as a human patient."""

import sys
import threading
import uuid
from pathlib import Path

import yaml
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    BOLD,
    DIM,
    GREEN,
    RED,
    RESET,
    YELLOW,
    CONVERSATIONS_DIR,
    format_status,
    human_conversation,
    load_all,
    print_history,
)


# ---------------------------------------------------------------------------
# Watchdog handler: prints new BOT lines when the file changes
# ---------------------------------------------------------------------------


class ConversationWatcher(FileSystemEventHandler):
    def __init__(self, conv_id: str) -> None:
        self.conv_id = conv_id
        self._last_len: int = 0
        self._lock = threading.Lock()
        # Initialise baseline length
        path = CONVERSATIONS_DIR / f"{conv_id}.yaml"
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f)
            self._last_len = len(data.get("history", [])) if data else 0

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
        if event.is_directory or isinstance(event, DirModifiedEvent):
            return
        path = Path(event.src_path)
        if path.name != f"{self.conv_id}.yaml":
            return
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except Exception:
            return
        if not data:
            return
        history = data.get("history", [])
        with self._lock:
            new_lines = history[self._last_len :]
            self._last_len = len(history)
        for line in new_lines:
            if line.startswith("$$BOT$$"):
                print(f"\r  {YELLOW}{line}{RESET}")
                print(f"[{self.conv_id}] > ", end="", flush=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def new_conv_id() -> str:
    return uuid.uuid4().hex[:8]


def show_conversations() -> None:
    convs = load_all()
    active = [c for c in convs if not c.get("escalated") and not c.get("scheduled")]
    terminated = [c for c in convs if c.get("escalated") or c.get("scheduled")]

    if not convs:
        print(f"{DIM}No conversations yet. Type /new to start one.{RESET}")
        return

    if active:
        print(f"{BOLD}Active conversations:{RESET}")
        for c in active:
            print(f"  {BOLD}{c['id']}{RESET}  {format_status(c)}")
    if terminated:
        print(f"{DIM}Terminated:{RESET}")
        for c in terminated:
            print(f"  {DIM}{c['id']}  {format_status(c)}{RESET}")


def enter_conversation(conv_id: str, create: bool = False) -> None:
    """Run the REPL for a single conversation, watching for bot replies."""
    path = CONVERSATIONS_DIR / f"{conv_id}.yaml"

    if not path.exists() and not create:
        print(f"{RED}Conversation '{conv_id}' not found.{RESET}")
        return

    # Print full history
    if path.exists():
        with open(path) as f:
            data = yaml.safe_load(f)
        if data:
            print_history(data)
    else:
        print(f"{DIM}(new conversation){RESET}")

    # Start watchdog
    watcher = ConversationWatcher(conv_id)
    observer = Observer()
    observer.schedule(watcher, str(CONVERSATIONS_DIR), recursive=False)
    observer.start()

    print(
        f"{DIM}Type a message, /new for a new conversation, or Ctrl+D to quit.{RESET}"
    )
    try:
        while True:
            try:
                text = input(f"[{conv_id}] > ").strip()
            except EOFError:
                print()
                break

            if not text:
                continue
            if text == "/new":
                break
            if text == "/quit":
                raise SystemExit(0)

            with human_conversation(conv_id, create=create) as data:
                data.setdefault("history", []).append(f"$$HUMAN$$ {text}")
            create = False  # file now exists
    finally:
        observer.stop()
        observer.join()

    # Return /new signal
    if text == "/new":
        run_repl(new_conv_id(), create=True)


def run_repl(initial_id: str | None = None, create: bool = False) -> None:
    if initial_id:
        enter_conversation(initial_id, create=create)
        return

    show_conversations()
    print()
    print(f"Enter a conversation ID, or {BOLD}/new{RESET} to start a new one:")
    try:
        choice = input("> ").strip()
    except EOFError:
        print()
        return

    if not choice:
        return
    if choice == "/new":
        conv_id = new_conv_id()
        print(f"{GREEN}Starting new conversation: {conv_id}{RESET}")
        enter_conversation(conv_id, create=True)
    else:
        enter_conversation(choice)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    CONVERSATIONS_DIR.mkdir(exist_ok=True)
    run_repl()
