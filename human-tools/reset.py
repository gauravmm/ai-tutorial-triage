"""Reset all conversations by deleting every YAML file in conversations/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import CONVERSATIONS_DIR

files = list(CONVERSATIONS_DIR.glob("*.yaml"))
for f in files:
    f.unlink()

print(f"Reset: deleted {len(files)} conversation(s).")
