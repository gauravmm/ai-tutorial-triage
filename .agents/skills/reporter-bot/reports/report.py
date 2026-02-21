"""Simulator tool for the reporter-bot skill.

Always run from the repository root:
  uv run .agents/skills/reporter-bot/reports/report.py <command> [args...]
"""

import argparse
import sys
from pathlib import Path

import yaml

CONVERSATIONS_DIR = Path("conversations")
REPORTS_DIR = Path("reports")


def _is_terminated(data: dict) -> bool:
    return bool(
        data.get("escalated") or data.get("no_further_action") or data.get("scheduled")
    )


def cmd_next(_: argparse.Namespace) -> None:
    """Print the first terminated conversation that has no report yet."""
    if not CONVERSATIONS_DIR.exists():
        print("# NO PENDING REPORTS")
        return

    REPORTS_DIR.mkdir(exist_ok=True)

    for path in sorted(CONVERSATIONS_DIR.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data or not _is_terminated(data):
            continue
        conv_id = data.get("id", path.stem)
        if (REPORTS_DIR / f"{conv_id}.yaml").exists():
            continue
        # Found one — print it and stop
        print(
            yaml.dump(
                data, default_flow_style=False, allow_unicode=True, sort_keys=False
            ),
            end="",
        )
        return

    print("# NO PENDING REPORTS")


REQUIRED_KEYS = {"name", "sex", "age", "symptoms", "triage"}
TRIAGE_VALUES = {"Minor", "Moderate", "Severe"}


def cmd_report(args: argparse.Namespace) -> None:
    """Write a report YAML for the given conversation id."""
    REPORTS_DIR.mkdir(exist_ok=True)

    yaml_text: str = str(args.yaml_text).replace("\\n", "\n")
    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        print(f"Error: invalid YAML — {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(parsed, dict):
        print("Error: report must be a YAML mapping", file=sys.stderr)
        sys.exit(1)

    missing = REQUIRED_KEYS - parsed.keys()
    if missing:
        print(
            f"Error: missing required keys: {', '.join(sorted(missing))}",
            file=sys.stderr,
        )
        sys.exit(1)

    if parsed["triage"] not in TRIAGE_VALUES:
        print(
            f"Error: triage must be one of: {', '.join(sorted(TRIAGE_VALUES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    out_path = REPORTS_DIR / f"{args.id}.yaml"
    with open(out_path, "w") as f:
        yaml.dump(
            parsed, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Reporter-bot simulator tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "next", help="Print the next unreported terminated conversation"
    )

    p_rep = subparsers.add_parser("report", help="Write a report for a conversation")
    p_rep.add_argument("id", type=str, help="Conversation ID")
    p_rep.add_argument("yaml_text", type=str, help="Report contents as a YAML string")

    args = parser.parse_args()
    {"next": cmd_next, "report": cmd_report}[args.command](args)


if __name__ == "__main__":
    main()
