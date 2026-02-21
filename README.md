# Multiagent Triage Bot Simulation

Users will contact your chatbot with their symptoms. You have to develop two AIs: one that triages them and schedules appointments, and one that prepares intake documents for each day.

You need to prepare a `triage-bot` which interacts with patients:

    1. Ask patients for symptoms (not just schedule appointments)
    2. Triage the patients. If the symptoms are:
        a. Minor (cuts and scrapes, runny nose, etc.): schedule them for an appointment
        b. Moderate (fever, long coughing, etc.): schedule them for an appointment
        c. Severe (bleeding, etc.): tell them to go to the emergency room.

You also need to prepare a `reporter-bot` that:

    1. Reads a conversation log between a human and the intake bot
    2. Extracts and reports relevant details:
        a. `name`
        b. `sex`
        c. `age`
        d. `symptoms`
        e. `triage`, which is one of `Minor`, `Moderate`, `Severe`

Each agent has access to its own specific prompt and tools in the `.agents/skills/` folder. These are implemented as skills here, but in reality would be separate bots running on the cloud.

Additionally, you have access to the following tools:

- `reset`: reset all simulations with some initial test data.
- `report` : print the current state of every conversation.
- `message`: simulate a conversation in the shell.
- `telegram` : start a telegram bot. Keep this running in the background to automatically send/receive messages.

You can run these using Run and Debug (Ctrl + Shift + D) and selecting them in the menu on the right. You can read the current log of every conversation in the folder `conversations/`, seen in Explorer (Ctrl + Shift + E).
