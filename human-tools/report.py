"""Print the current state of every conversation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import BOLD, DIM, RESET, format_status, load_all, print_history

convs = load_all()
if not convs:
    print(f"{DIM}No conversations found.{RESET}")
    sys.exit(0)

for data in convs:
    conv_id = data.get("id", "?")
    status = format_status(data)
    count = len(data.get("history", []))
    print(f"{BOLD}{conv_id}{RESET}  {status}  {DIM}({count} message(s)){RESET}")
    print_history(data)
    print()
