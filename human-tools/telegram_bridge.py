"""Telegram bot: routes incoming messages into conversation YAML files
and delivers bot replies back to Telegram users via watchdog.

Each Telegram chat gets conversations named {chat_id}_{nonce}.yaml.
Send /new in Telegram to start a fresh conversation (increments the nonce).
"""

import asyncio
import logging
import sys
from pathlib import Path

import yaml
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

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


def _parse_chat_id(stem: str) -> int | None:
    """Extract chat_id from '{chat_id}_{nonce}', or None if not that format."""
    parts = stem.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit() and parts[0].lstrip("-").isdigit():
        return int(parts[0])
    return None


# ---------------------------------------------------------------------------
# Watchdog: watch for bot replies and forward to Telegram
# ---------------------------------------------------------------------------


class BotReplyWatcher(FileSystemEventHandler):
    def __init__(self, bot: Bot, loop: asyncio.AbstractEventLoop) -> None:
        self.bot = bot
        self.loop = loop
        # Pre-seed sent counts from existing files to avoid re-sending on restart
        self._sent: dict[str, int] = {}
        for path in CONVERSATIONS_DIR.glob("*.yaml"):
            if _parse_chat_id(path.stem) is None:
                continue
            try:
                with open(path) as f:
                    data = yaml.safe_load(f)
                self._sent[path.stem] = len(data.get("history", [])) if data else 0
            except Exception:
                pass

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
        if event.is_directory or isinstance(event, DirModifiedEvent):
            return
        path = Path(str(event.src_path))
        if path.suffix != ".yaml":
            return
        chat_id = _parse_chat_id(path.stem)
        if chat_id is None:
            return
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except Exception:
            return
        if not data:
            return

        history = data.get("history", [])
        conv_id = path.stem
        sent = self._sent.get(conv_id, 0)
        new_lines = history[sent:]
        self._sent[conv_id] = len(history)

        for line in new_lines:
            if line.startswith("$$BOT$$ "):
                text = line[len("$$BOT$$ ") :]
                asyncio.run_coroutine_threadsafe(
                    self.bot.send_message(chat_id=chat_id, text=text),
                    self.loop,
                )
                log.info("[%s] → Telegram %d: %s", conv_id, chat_id, text)


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
# Lifecycle: start/stop watchdog alongside the app
# ---------------------------------------------------------------------------


async def post_init(app: Application) -> None:
    loop = asyncio.get_event_loop()
    watcher = BotReplyWatcher(app.bot, loop)
    observer = Observer()
    observer.schedule(watcher, str(CONVERSATIONS_DIR), recursive=False)
    observer.start()
    app.bot_data["observer"] = observer
    log.info("Watchdog started on %s/", CONVERSATIONS_DIR)


async def post_shutdown(app: Application) -> None:
    observer = app.bot_data.get("observer")
    if observer:
        observer.stop()
        observer.join()
    log.info("Watchdog stopped")


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

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("new", handle_new))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Telegram bot running. Conversations stored in {CONVERSATIONS_DIR}/")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
