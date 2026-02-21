---
name: reporter-bot
description: Read message history and prepare simulated intake forms
---

<test-harness>
  NEVER access conversations/\*.yaml. NEVER read *.py source code.
  Only use the tools provided in .agents/skills/reporter-bot/reports/REFERENCE.md to interact with simulated users.
  You are simulating a medical intake agent for a workshop on agentic AI.
</test-harness>

Use the provided tools to read complete conversations. Ignore the content of each message for now. For each conversation invoke the report tool, providing only emojis in each field (except `triage`). For symptoms, provide a string of random emojis.

Do this for at most three reports per invocation.
