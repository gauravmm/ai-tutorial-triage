"""Telegram bot: routes incoming messages into conversation YAML files.

Each Telegram chat gets conversations named {chat_id}_{nonce}.yaml.
Send /new in Telegram to start a fresh conversation (increments the nonce).
"""

import logging
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

sys.path.insert(0, str(Path(__file__).parent))
from _common import CONVERSATIONS_DIR, human_conversation

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

TOKEN_FILE = Path("telegram.key")

DISCLAIMER = (
    "⚠️ *Simulator*\n\n"
    "This is a training simulation and not a real medical service\\. "
    "Do not send real personal or medical information\\. "
    "In an emergency, call 999 immediately\\.\n\n"
)

HELP_TEXT = (
    "🤖 *Triage bot simulator*\n\n"
    "Send a message to start a simulated triage conversation\\.\n\n"
    "*Commands:*\n"
    "/new  — start a fresh conversation\n"
    "/help — show this message"
)


# ---------------------------------------------------------------------------
# Nonce helpers
# ---------------------------------------------------------------------------


def _current_nonce(chat_id: int) -> int:
    """Return the highest existing nonce for this chat_id (0 if none)."""
    prefix = f"{chat_id}_"
    nonces = [
        int(p.stem[len(prefix) :])
        for p in CONVERSATIONS_DIR.glob(f"{chat_id}_*.yaml")
        if p.stem[len(prefix) :].isdigit()
    ]
    return max(nonces, default=0)


def get_conv_id(chat_id: int) -> str:
    nonce = _current_nonce(chat_id)
    if nonce == 0:
        nonce = 1  # first conversation
    return f"{chat_id}_{nonce}"


def next_conv_id(chat_id: int) -> str:
    nonce = _current_nonce(chat_id) + 1
    return f"{chat_id}_{nonce}"


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


async def handle_help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(HELP_TEXT, parse_mode="MarkdownV2")


async def handle_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message:
        return

    chat_id = update.effective_chat.id
    conv_id = next_conv_id(chat_id)
    # Touch the file so the nonce is committed even before a message arrives
    with human_conversation(conv_id, create=True):
        pass  # creates file, sets last=HUMAN (no history yet)
    log.info("New conversation started: %s", conv_id)
    await update.message.reply_text(DISCLAIMER, parse_mode="MarkdownV2")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message:
        return

    chat_id = update.effective_chat.id
    text = update.message.text or ""
    is_first = _current_nonce(chat_id) == 0

    CONVERSATIONS_DIR.mkdir(exist_ok=True)
    conv_id = get_conv_id(chat_id)
    with human_conversation(conv_id, create=True) as data:
        data.setdefault("history", []).append(f"$$HUMAN$$ {text}")

    log.info("[%s] HUMAN: %s", conv_id, text)

    if is_first:
        await update.message.reply_text(DISCLAIMER, parse_mode="MarkdownV2")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    if not TOKEN_FILE.exists():
        print(
            f"Error: {TOKEN_FILE} not found. Copy telegram.key.EXAMPLE and add your token."
        )
        return

    token = TOKEN_FILE.read_text().strip()
    CONVERSATIONS_DIR.mkdir(exist_ok=True)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("new", handle_new))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Telegram bot running. Conversations stored in {CONVERSATIONS_DIR}/")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
