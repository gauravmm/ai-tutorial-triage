# Reference

These tools are only for use by the `triage-bot` skill. The skills are relevant to interacting with a simulated message channel.

Always invoke the `message.py` tool with the root of the repository as the working directory.

## Incoming and Outgoing

`uv run message.py incoming` reads messages from the message queue.

It produces output following:

```yaml
id: <conversation id>
history:
  - $$BOT$$ <message>
  - $$HUMAN$$ <message>
```

Messages are emitted in chronological order ending with latest. Messages are tagged by whether a `$$HUMAN$$` or a `$$BOT$$` has produced them (AI or otherwise).

You should respond to messages with:

```sh
uv run message.py outgoing "<conversation id>" "<message string>"
```

## Terminating conversations

Once the conversation is complete, you can end it by either scheduling an appointment or escalating to the emergency department.

To schedule an appointment, call this tool with a specific date and with either `am` or `pm`:

```sh
uv run message.py schedule "<conversation id>" "<YYYY-mm-dd>" "<am|pm>"
```

To escalate to the emergency department, you can call this tool:

```sh
uv run message.py escalate "<conversation id>"
```
