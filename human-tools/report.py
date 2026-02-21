"""Print the current state of every conversation as a table."""

import sys
from pathlib import Path

from tabulate import tabulate

sys.path.insert(0, str(Path(__file__).parent))
from _common import DIM, RESET, format_status, load_all


def fmt_last(history: list[str]):
    last_msg = history[-1] if history else "# No Messages #"
    msg = last_msg.replace("$$BOT$$ ", "🤖›").replace("$$HUMAN$$ ", "💬›")
    return msg if len(msg) <= 40 else msg[:39] + "…"


def main():
    if convs := load_all():
        print(
            tabulate(
                [
                    (
                        data.get("id", "?"),
                        len(data.get("history", [])),
                        format_status(data),
                        fmt_last(data.get("history", [])),
                    )
                    for data in convs
                ],
                headers=["ID", "Len", "Status", "Last message"],
                tablefmt="simple",
            )
        )
    else:
        print(f"{DIM}No conversations found.{RESET}")


if __name__ == "__main__":
    main()
