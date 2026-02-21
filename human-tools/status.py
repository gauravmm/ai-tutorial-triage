"""Print the current state of every conversation as a table."""

import sys
from pathlib import Path

from tabulate import tabulate

sys.path.insert(0, str(Path(__file__).parent))
from _common import DIM, GREEN, RESET, YELLOW, format_status, load_all

REPORTS_DIR = Path("reports")


def fmt_last(history: list[str]):
    last_msg = history[-1] if history else "# No Messages #"
    msg = last_msg.replace("$$BOT$$ ", "🤖›").replace("$$HUMAN$$ ", "💬›")
    return msg if len(msg) <= 40 else msg[:39] + "…"


def fmt_report(data: dict) -> str:
    terminated = (
        data.get("escalated") or data.get("no_further_action") or data.get("scheduled")
    )
    if not terminated:
        return f"{DIM}ongoing{RESET}"
    if (REPORTS_DIR / f"{data.get('id', '?')}.yaml").exists():
        return f"{GREEN}✅ reported{RESET}"
    return f"{YELLOW}⏳ pending{RESET}"


def main():
    if convs := load_all():
        print(
            tabulate(
                [
                    (
                        data.get("id", "?"),
                        len(data.get("history", [])),
                        format_status(data),
                        fmt_report(data),
                        fmt_last(data.get("history", [])),
                    )
                    for data in convs
                ],
                headers=["ID", "Len", "Status", "Report", "Last message"],
                tablefmt="presto",
            )
        )
    else:
        print(f"{DIM}No conversations found.{RESET}")


if __name__ == "__main__":
    main()
