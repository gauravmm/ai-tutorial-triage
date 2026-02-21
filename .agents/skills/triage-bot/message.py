"""Simulator tool for the triage-bot skill.

Always run from the repository root:
  uv run SKILLS/triage-bot/message.py <command> [args...]
"""

import argparse
import sys
from contextlib import contextmanager
from typing import Generator

import yaml
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore[assignment]

CONVERSATIONS_DIR = Path("conversations")


@contextmanager
def conversation(conv_id: str) -> Generator[dict, None, None]:
    """Load a conversation, and on exit set last=BOT and write it back."""
    if fcntl is None:
        print(
            "Fatal error: file locking (fcntl) is not supported on this platform",
            file=sys.stderr,
        )
        sys.exit(1)
    path = CONVERSATIONS_DIR / f"{conv_id}.yaml"
    if not path.exists():
        print(f"Error: conversation '{conv_id}' not found", file=sys.stderr)
        sys.exit(1)
    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        data = yaml.safe_load(f)
        yield data
        data["last"] = "BOT"
        f.seek(0)
        f.truncate()
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
    # lock released on file close


def cmd_incoming(_: argparse.Namespace) -> None:
    """Print the first active conversation where the human spoke last."""
    if not CONVERSATIONS_DIR.exists():
        return
    for path in sorted(CONVERSATIONS_DIR.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if (
            not data
            or data.get("escalated")
            or data.get("scheduled")
            or data.get("no_further_action")
            or data.get("last") != "HUMAN"
        ):
            continue
        print(
            yaml.dump(
                {"id": data["id"], "history": data.get("history", [])},
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        )
        break
    else:
        print("# NO MESSAGES")


def cmd_outgoing(args: argparse.Namespace) -> None:
    """Append a bot message to a conversation."""
    with conversation(args.id) as data:
        data.setdefault("history", []).append(f"$$BOT$$ {args.message}")


def cmd_schedule(args: argparse.Namespace) -> None:
    """Mark a conversation as scheduled for an appointment."""
    with conversation(args.id) as data:
        data["scheduled"] = {"date": args.date, "time": args.time}


def cmd_escalate(args: argparse.Namespace) -> None:
    """Mark a conversation as escalated to the emergency department."""
    with conversation(args.id) as data:
        data["escalated"] = True


def cmd_no_further_action(args: argparse.Namespace) -> None:
    """Mark a conversation as requiring no further action."""
    with conversation(args.id) as data:
        data["no_further_action"] = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage-bot simulator tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("incoming", help="Read active messages from the queue")

    p_out = subparsers.add_parser("outgoing", help="Send a bot reply")
    p_out.add_argument("id", help="Conversation ID")
    p_out.add_argument("message", help="Message text")

    p_sched = subparsers.add_parser("schedule", help="Schedule an appointment")
    p_sched.add_argument("id", help="Conversation ID")
    p_sched.add_argument("date", help="Appointment date (YYYY-mm-dd)")
    p_sched.add_argument("time", choices=["am", "pm"], help="Appointment time")

    p_esc = subparsers.add_parser(
        "escalate", help="Escalate to the emergency department"
    )
    p_esc.add_argument("id", help="Conversation ID")

    p_nfa = subparsers.add_parser("no-further-action", help="Mark as no further action")
    p_nfa.add_argument("id", help="Conversation ID")

    args = parser.parse_args()
    {
        "incoming": cmd_incoming,
        "outgoing": cmd_outgoing,
        "schedule": cmd_schedule,
        "escalate": cmd_escalate,
        "no-further-action": cmd_no_further_action,
    }[args.command](args)


if __name__ == "__main__":
    main()
