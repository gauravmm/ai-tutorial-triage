"""Reset all conversations and populate with initial test data."""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from _common import CONVERSATIONS_DIR

# ---------------------------------------------------------------------------
# Clear existing conversations
# ---------------------------------------------------------------------------

deleted = list(CONVERSATIONS_DIR.glob("*.yaml"))
for f in deleted:
    f.unlink()
print(f"Deleted {len(deleted)} existing conversation(s).")

# ---------------------------------------------------------------------------
# Seed data — covers every possible state
# ---------------------------------------------------------------------------

SEED: list[dict] = [
    # --- Active: last=HUMAN (6) — awaiting bot reply ---
    {
        "id": "alice",
        "history": [
            "$$HUMAN$$ Hi, I've had a splitting headache for the past two days.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "bob",
        "history": [
            "$$HUMAN$$ I cut my finger pretty badly while cooking.",
            "$$BOT$$ How deep does the cut look? Is the bleeding controlled?",
            "$$HUMAN$$ It's still bleeding a bit. Maybe half an inch long.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "carol",
        "history": [
            "$$HUMAN$$ My kid has had a runny nose and mild cough since Monday.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "david",
        "history": [
            "$$HUMAN$$ I twisted my ankle playing football. It's swollen but I can walk.",
            "$$BOT$$ Can you put weight on it? Any severe pain or bruising?",
            "$$HUMAN$$ Some bruising yes, but I can hobble around.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "eve",
        "history": [
            "$$HUMAN$$ I've had a fever of 38.9°C for three days now.",
            "$$BOT$$ Are you experiencing any other symptoms — sore throat, rash, difficulty breathing?",
            "$$HUMAN$$ Sore throat and fatigue, but no rash or breathing issues.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "frank",
        "history": [
            "$$HUMAN$$ My lower back has been aching for a week. I work at a desk all day.",
        ],
        "last": "HUMAN",
    },
    # --- Active: last=BOT (4) — awaiting human reply ---
    {
        "id": "grace",
        "history": [
            "$$HUMAN$$ I hurt my knee at the gym yesterday.",
            "$$BOT$$ I'm sorry to hear that. Can you describe the pain — is it sharp, dull, or aching? Does it hurt to bend the knee?",
        ],
        "last": "BOT",
    },
    {
        "id": "henry",
        "history": [
            "$$HUMAN$$ I've been coughing for three weeks.",
            "$$BOT$$ That's quite a while. Is the cough dry or productive? Any blood or discoloured mucus?",
        ],
        "last": "BOT",
    },
    {
        "id": "iris",
        "history": [
            "$$HUMAN$$ I have a stomach ache and feel nauseous.",
            "$$BOT$$ How long have you had these symptoms? Did you eat anything unusual recently?",
        ],
        "last": "BOT",
    },
    {
        "id": "jack",
        "history": [
            "$$HUMAN$$ There's a rash spreading on my arm.",
            "$$BOT$$ When did you first notice it? Is it itchy, painful, or warm to the touch?",
        ],
        "last": "BOT",
    },
    # --- Scheduled: morning (3) ---
    {
        "id": "karen",
        "history": [
            "$$HUMAN$$ I have a runny nose and mild cold symptoms.",
            "$$BOT$$ These sound like minor cold symptoms. I'll book you in for a routine check-up.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-03", "time": "am"},
    },
    {
        "id": "liam",
        "history": [
            "$$HUMAN$$ My ear has been hurting for two days. Could be an infection.",
            "$$BOT$$ Ear pain that persists warrants a check. I've scheduled a morning appointment for you.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-04", "time": "am"},
    },
    {
        "id": "maya",
        "history": [
            "$$HUMAN$$ I lightly sprained my wrist — it's a bit sore but I can move it.",
            "$$BOT$$ Sounds like a mild sprain. Let's have a doctor take a look in the morning.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-05", "time": "am"},
    },
    # --- Scheduled: afternoon (3) ---
    {
        "id": "noah",
        "history": [
            "$$HUMAN$$ Sore throat for four days. Hurts to swallow.",
            "$$BOT$$ It could be strep. I've scheduled an afternoon appointment — they can do a quick swab.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-03", "time": "pm"},
    },
    {
        "id": "olivia",
        "history": [
            "$$HUMAN$$ I burned my hand on the oven — it's red and a bit blistered.",
            "$$BOT$$ That sounds like a second-degree burn. Please come in this afternoon so we can assess it properly.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-04", "time": "pm"},
    },
    {
        "id": "peter",
        "history": [
            "$$HUMAN$$ I've been getting headaches every afternoon this week.",
            "$$BOT$$ Recurring headaches should be looked at. I've booked you an afternoon slot.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-06", "time": "pm"},
    },
    # --- Escalated (2) ---
    {
        "id": "quinn",
        "history": [
            "$$HUMAN$$ I'm having severe chest pain and my left arm feels numb.",
            "$$BOT$$ These are signs of a possible cardiac emergency. Please call 999 immediately or go to A&E now. Do not drive yourself.",
        ],
        "last": "BOT",
        "escalated": True,
    },
    {
        "id": "rachel",
        "history": [
            "$$HUMAN$$ I fell and have a deep cut on my leg. It won't stop bleeding.",
            "$$BOT$$ This needs immediate attention. Go to A&E or call 999 right away. Apply firm pressure to the wound while you wait.",
        ],
        "last": "BOT",
        "escalated": True,
    },
    # --- No further action (2) ---
    {
        "id": "sam",
        "history": [
            "$$HUMAN$$ Hi, I was wondering if you could tell me your opening hours?",
            "$$BOT$$ We're open Monday to Friday, 8am–6pm. Is there anything medical I can help with?",
            "$$HUMAN$$ No, that's all I needed. Thanks!",
            "$$BOT$$ Happy to help. Take care!",
        ],
        "last": "BOT",
        "no_further_action": True,
    },
    {
        "id": "tom",
        "history": [
            "$$HUMAN$$ I just wanted to double-check my appointment time.",
            "$$BOT$$ Your appointment is confirmed for 2026-03-04 at 2pm. No changes needed?",
            "$$HUMAN$$ Nope, perfect. See you then.",
            "$$BOT$$ See you then. Goodbye!",
        ],
        "last": "BOT",
        "no_further_action": True,
    },
]

# ---------------------------------------------------------------------------
# Write files
# ---------------------------------------------------------------------------

CONVERSATIONS_DIR.mkdir(exist_ok=True)
for conv in SEED:
    path = CONVERSATIONS_DIR / f"{conv['id']}.yaml"
    with open(path, "w") as f:
        yaml.dump(conv, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print(f"Created {len(SEED)} seed conversation(s).")
