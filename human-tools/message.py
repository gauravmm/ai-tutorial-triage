#!/usr/bin/env python3
"""Textual TUI for the triage message system.

Run from the task/ directory:
    uv run human-tools/message_tui.py

Keybindings:
    Ctrl+N  — new conversation
    Escape  — focus conversation list
    Enter   — send message (when input is focused)
    Ctrl+D  — quit
"""

import sys
import uuid
from pathlib import Path

import yaml
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, ListItem, ListView, Static
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

sys.path.insert(0, str(Path(__file__).parent))
from _common import CONVERSATIONS_DIR, human_conversation, load_all


# ── Helpers ──────────────────────────────────────────────────────────────────


def status_markup(data: dict) -> str:
    if data.get("escalated"):
        return "[bold red]🚨 escalated[/]"
    if data.get("no_further_action"):
        return "[dim]✅ done[/]"
    if s := data.get("scheduled"):
        return f"[green]📅 {s['date']} {s['time']}[/]"
    last = data.get("last", "?")
    return "[cyan]💬 you[/]" if last == "HUMAN" else "[yellow]🤖 bot[/]"


def terminated_notice(data: dict) -> str | None:
    """Return a notice string if the conversation is closed, else None."""
    if data.get("escalated"):
        return "[bold red]🚨 Escalated — this conversation has been closed.[/]"
    if data.get("no_further_action"):
        return "[dim]✅ No further action required — this conversation is closed.[/]"
    if s := data.get("scheduled"):
        return f"[green]📅 Appointment scheduled for {s['date']} at {s['time']} — this conversation is closed.[/]"
    return None


# ── File watcher ──────────────────────────────────────────────────────────────


class _DirWatcher(FileSystemEventHandler):
    def __init__(self, callback) -> None:
        self._cb = callback

    def _handle(self, event) -> None:
        if not event.is_directory:
            p = Path(str(event.src_path))
            if p.suffix == ".yaml":
                self._cb(p.stem)

    def on_modified(self, event) -> None:
        self._handle(event)

    def on_created(self, event) -> None:
        self._handle(event)


# ── App ───────────────────────────────────────────────────────────────────────

CSS = """
Screen { background: $surface; }

#app-grid {
    layout: horizontal;
    height: 1fr;
}

/* ─── Sidebar ─────────────────────────────── */

#sidebar {
    width: 28;
    height: 100%;
    layout: vertical;
    border-right: solid $panel-lighten-1;
}

#sidebar-title {
    height: 1;
    background: $panel-lighten-1;
    padding: 0 1;
    text-style: bold;
    color: $text;
}

#conv-list {
    height: 1fr;
    padding: 0;
    margin: 0;
    background: $surface;
}

/* ─── Chat pane ───────────────────────────── */

#chat-area {
    width: 1fr;
    height: 100%;
    layout: vertical;
}

#chat-title {
    height: 1;
    background: $panel-lighten-1;
    padding: 0 1;
    color: $text;
}

#messages {
    height: 1fr;
    overflow-y: auto;
    padding: 1 2;
}

.msg-human {
    margin: 0 0 1 0;
    padding: 0 1;
    border-left: solid $primary;
    color: $text;
}

.msg-bot {
    margin: 0 0 1 0;
    padding: 0 1;
    border-left: solid $warning;
    color: $text;
}

.msg-terminated {
    margin: 1 0 0 0;
    padding: 0 1;
    border-top: solid $panel-lighten-2;
    text-style: italic;
    color: $text-muted;
}

/* ─── Input row ───────────────────────────── */

#input-row {
    height: 3;
    layout: horizontal;
    padding: 0 1;
    border-top: solid $panel-lighten-1;
    align: left middle;
}

#msg-input { width: 1fr; }
#send-btn   { width: 10; margin-left: 1; }
"""


class TriageApp(App):
    CSS = CSS
    TITLE = "Triage Chat"
    BINDINGS = [
        Binding("ctrl+n", "new_conv", "New Conv", show=True),
        Binding("escape", "focus_list", "Convs", show=True),
        Binding("ctrl+d", "quit", "Quit", show=True),
    ]

    selected_id: reactive[str | None] = reactive(None)

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="app-grid"):
            with Vertical(id="sidebar"):
                yield Static("Conversations", id="sidebar-title")
                yield ListView(id="conv-list")
            with Vertical(id="chat-area"):
                yield Static("← select a conversation", id="chat-title")
                yield ScrollableContainer(id="messages")
                with Horizontal(id="input-row"):
                    yield Input(
                        placeholder="Type a message…",
                        id="msg-input",
                        disabled=True,
                    )
                    yield Button(
                        "Send", id="send-btn", variant="primary", disabled=True
                    )
        yield Footer()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        CONVERSATIONS_DIR.mkdir(exist_ok=True)
        self._refresh_list()
        handler = _DirWatcher(
            lambda cid: self.call_from_thread(self._on_file_changed, cid)
        )
        self._observer = Observer()
        self._observer.schedule(handler, str(CONVERSATIONS_DIR), recursive=False)
        self._observer.start()

    def on_unmount(self) -> None:
        if hasattr(self, "_observer"):
            self._observer.stop()
            self._observer.join()

    # ── File-change callback (arrives on the UI thread via call_from_thread) ──

    def _on_file_changed(self, conv_id: str) -> None:
        self._refresh_list()
        if conv_id == self.selected_id:
            self._refresh_messages()

    # ── Conversation list ─────────────────────────────────────────────────────

    def _refresh_list(self) -> None:
        convs = load_all()
        lv = self.query_one("#conv-list", ListView)
        new_map = {c.get("id", "?"): c for c in convs}

        # Update or remove existing items in-place (no clear → no flash)
        for item in list(lv.query(ListItem)):
            cid = (item.id or "")[5:]  # strip "item-" prefix
            if cid in new_map:
                item.query_one(Static).update(
                    f"[bold]{cid}[/]\n{status_markup(new_map[cid])}"
                )
            else:
                item.remove()

        # Append conversations not yet in the list
        existing = {
            (it.id or "")[5:]
            for it in lv.query(ListItem)
            if (it.id or "").startswith("item-")
        }
        for c in convs:
            cid = c.get("id", "?")
            if cid not in existing:
                lv.append(
                    ListItem(
                        Static(f"[bold]{cid}[/]\n{status_markup(c)}", markup=True),
                        id=f"item-{cid}",
                    )
                )

    # ── Message view ──────────────────────────────────────────────────────────

    def _refresh_messages(self) -> None:
        container = self.query_one("#messages", ScrollableContainer)
        container.remove_children()
        if not self.selected_id:
            return
        path = CONVERSATIONS_DIR / f"{self.selected_id}.yaml"
        if not path.exists():
            # New unsaved conversation — input stays enabled
            self._set_input_locked(False)
            return
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data:
            self._set_input_locked(False)
            return
        for line in data.get("history", []):
            if line.startswith("$$HUMAN$$ "):
                text = line[10:]
                container.mount(
                    Static(
                        f"[bold cyan]You[/]  {text}", classes="msg-human", markup=True
                    )
                )
            elif line.startswith("$$BOT$$ "):
                text = line[8:]
                container.mount(
                    Static(
                        f"[bold yellow]Bot[/]  {text}", classes="msg-bot", markup=True
                    )
                )
        notice = terminated_notice(data)
        if notice:
            container.mount(Static(notice, classes="msg-terminated", markup=True))
            self._set_input_locked(True)
        else:
            self._set_input_locked(False)
        container.scroll_end(animate=False)

    def _set_input_locked(self, locked: bool) -> None:
        inp = self.query_one("#msg-input", Input)
        btn = self.query_one("#send-btn", Button)
        inp.disabled = locked
        btn.disabled = locked
        if locked:
            inp.placeholder = "Conversation closed — no further messages can be sent."
        else:
            inp.placeholder = "Type a message…"

    # ── Event handlers ────────────────────────────────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id and item_id.startswith("item-"):
            self._select_conv(item_id[5:])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            self._send()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "msg-input":
            self._send()

    # ── Core actions ──────────────────────────────────────────────────────────

    def _select_conv(self, conv_id: str) -> None:
        self.selected_id = conv_id
        self.query_one("#chat-title", Static).update(f"[bold]{conv_id}[/]")
        self._refresh_messages()  # sets input locked/unlocked based on state
        self.query_one("#msg-input", Input).focus()

    def _send(self) -> None:
        if not self.selected_id:
            return
        inp = self.query_one("#msg-input", Input)
        text = inp.value.strip()
        if not text:
            return
        path = CONVERSATIONS_DIR / f"{self.selected_id}.yaml"
        with human_conversation(self.selected_id, create=not path.exists()) as data:
            data.setdefault("history", []).append(f"$$HUMAN$$ {text}")
        inp.value = ""
        self._refresh_messages()

    def action_new_conv(self) -> None:
        conv_id = uuid.uuid4().hex[:8]
        self._select_conv(conv_id)
        self.query_one("#chat-title", Static).update(
            f"[bold]{conv_id}[/] [dim](new — send a message to start)[/]"
        )
        self.notify(f"New conversation: {conv_id}", severity="information")

    def action_focus_list(self) -> None:
        self.query_one("#conv-list", ListView).focus()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    TriageApp().run()
