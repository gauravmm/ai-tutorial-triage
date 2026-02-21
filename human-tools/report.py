"""Print the current state of every conversation as a table."""

import sys
from pathlib import Path

from tabulate import tabulate

sys.path.insert(0, str(Path(__file__).parent))
from _common import DIM, RESET, format_status, load_all


def main():
    if convs := load_all():
        print(
            tabulate(
                [
                    (
                        data.get("id", "?"),
                        len(data.get("history", [])),
                        format_status(data),
                    )
                    for data in convs
                ],
                headers=["ID", "Messages", "Status"],
                tablefmt="simple",
            )
        )
    else:
        print(f"{DIM}No conversations found.{RESET}")


if __name__ == "__main__":
    main()
