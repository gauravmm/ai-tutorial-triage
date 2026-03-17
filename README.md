# Multiagent Triage Bot Simulation

Users will contact your chatbot with their symptoms. You have to develop two AIs: one that triages them and schedules appointments, and one that prepares intake documents for each day.

Each agent has access to its own specific prompt and tools in the `.agents/skills/` folder. These are implemented as skills here, but in reality would be separate bots running on the cloud.

## Triage Bot

You need to prepare a `triage-bot` which interacts with patients:

1. Ask patients for symptoms (not just schedule appointments)
2. Triage the patients. If the symptoms are:
    a. Minor (cuts and scrapes, runny nose, etc.): schedule them for an appointment
    b. Moderate (fever, long coughing, etc.): schedule them for an appointment
    c. Severe (bleeding, etc.): tell them to go to the emergency room.

### Getting Started

To start the bot, you need to:

1. Contact `@BotFather` on telegram to create a new bot. Copy the secret key and paste it into a new file called `telegram.key`.
2. In the Run and Debug menu on the left, select the `telegram` option in the drop-down and then click "Start".
    a. Read the output and look for `Application Started`.
3. Send the bot a message! You should get an automated notice.
4. Check the folder `conversations/` in the Explorer tab on the left. You should see your message.

Now set the AI up and trigger it by:

1. In the chat window on the right, you should switch the model to GPT-4.1 or GPT-4o.
2. Enter the command `/triage-bot` with no further prompt
3. Check that it reads `REFERENCE.md` so it knows how to use our message tools.
4. Give the AI permission to run the various commands so it can read and respond to messages.

Each time the bot receives messages, you'll need to trigger it again with `/triage-bot`. Usually, this would be done automatically, but GitHub's free tier requires you trigger it manually.

The AI will produce unhelpful messages at first. You should take a look at the prompt in `.agents/skills/triage-bot/SKILL.md` and improve it.

---

## Reporter Bot

Once the triage-bot is working, you should then prepare a `reporter-bot` that:

    1. Reads a conversation log between a human and the intake bot
    2. Extracts and reports relevant details:
        a. `name`
        b. `sex`
        c. `age`
        d. `symptoms`
        e. `triage`, which is one of `Minor`, `Moderate`, `Severe`

This bot does not communicate over telegram. Instead, it saves reports to `reports/`

## Additional Tools

Additionally, you have access to the following tools:

- `reset`: reset all simulations with some initial test data.
- `report` : print the current state of every conversation.
- `message`: simulate a conversation in the shell. Great if you don't want to use Telegram.
- `telegram` : start a telegram bot. Keep this running in the background to automatically send/receive messages.

You can run these using Run and Debug (Ctrl + Shift + D) and selecting them in the menu on the right. You can read the current log of every conversation in the folder `conversations/`, seen in Explorer (Ctrl + Shift + E).
