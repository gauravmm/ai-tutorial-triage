"""Reset all conversations and populate with initial test data."""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from _common import CONVERSATIONS_DIR

REPORTS_DIR = Path("reports")

# ---------------------------------------------------------------------------
# Clear existing conversations and reports
# ---------------------------------------------------------------------------

deleted = list(CONVERSATIONS_DIR.glob("*.yaml"))
for f in deleted:
    f.unlink()
print(f"Deleted {len(deleted)} existing conversation(s).")

deleted_reports = list(REPORTS_DIR.glob("*.yaml")) if REPORTS_DIR.exists() else []
for f in deleted_reports:
    f.unlink()
print(f"Deleted {len(deleted_reports)} existing report(s).")

# ---------------------------------------------------------------------------
# Seed data — covers every possible state
# ---------------------------------------------------------------------------

SEED: list[dict] = [
    # --- Active: last=HUMAN (8) — awaiting bot reply ---
    {
        "id": "alice",
        "history": [
            "$$HUMAN$$ Hi, I'm Alice Marsh, I'm 35 years old. I've had a splitting headache for the past two days.",
            "$$BOT$$ I'm sorry to hear that. How severe is the pain on a scale of 1–10, and have you had headaches like this before?",
            "$$HUMAN$$ I'd say around a 7. I do get migraines sometimes, but this feels different — more pressure, and it hasn't let up at all.",
            "$$BOT$$ Are you experiencing any sensitivity to light, neck stiffness, or changes in vision?",
            "$$HUMAN$$ Yes, the light is really bothering me. No neck stiffness though.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "bob",
        "history": [
            "$$HUMAN$$ Hi, I'm Bob Keane, 28. I cut my finger pretty badly while cooking.",
            "$$BOT$$ How deep does the cut look? Is the bleeding controlled?",
            "$$HUMAN$$ It's still bleeding a bit. Maybe half an inch long.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "carol",
        "history": [
            "$$HUMAN$$ Hi, I'm Carol Fenn, I'm 33. My kid has had a runny nose and mild cough since Monday.",
            "$$BOT$$ How old is your child, and have they had a fever or any difficulty breathing?",
            "$$HUMAN$$ She's 5. Her temperature was 37.5°C this morning — nothing too high. No breathing trouble.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "david",
        "history": [
            "$$HUMAN$$ Hi, I'm David Osei, 24 years old. I twisted my ankle playing football. It's swollen but I can walk.",
            "$$BOT$$ Can you put weight on it? Any severe pain or bruising?",
            "$$HUMAN$$ Some bruising yes, but I can hobble around.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "eve",
        "history": [
            "$$HUMAN$$ Hi, I'm Eve Hartley, I'm 29. I've had a fever of 38.9°C for three days now.",
            "$$BOT$$ Are you experiencing any other symptoms — sore throat, rash, difficulty breathing?",
            "$$HUMAN$$ Sore throat and fatigue, but no rash or breathing issues.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "frank",
        "history": [
            "$$HUMAN$$ Hi, I'm Frank Dolan, I'm 45. My lower back has been aching for a week. I work at a desk all day.",
            "$$BOT$$ Has the pain come on gradually or was there a specific moment it started? Does it radiate down your legs at all?",
            "$$HUMAN$$ Gradually, over the past week. No leg pain — just a constant dull ache in my lower back, maybe a 4 out of 10.",
        ],
        "last": "HUMAN",
    },
    # --- Active: last=BOT (2) — awaiting human reply; registration incomplete ---
    {
        "id": "grace",
        "history": [
            "$$HUMAN$$ I hurt my knee at the gym yesterday.",
            "$$BOT$$ I'm sorry to hear that. Can you describe the pain — is it sharp, dull, or aching? Does it hurt to bend the knee?",
            "$$HUMAN$$ It's a dull ache. I can bend it a little but it's quite painful and there's some swelling.",
            "$$BOT$$ Did you hear a pop when it happened? Any feeling of instability when you stand? Could I also get your name and age?",
            "$$HUMAN$$ No pop. It does feel a bit unstable. I'm Grace Tanner, I'm 30.",
        ],
        "last": "HUMAN",
    },
    {
        "id": "henry",
        "history": [
            "$$HUMAN$$ I've been coughing for three weeks.",
            "$$BOT$$ That's quite a while. Is the cough dry or productive? Any blood or discoloured mucus?",
            "$$HUMAN$$ It's productive — yellowish mucus. No blood.",
            "$$BOT$$ Have you had a fever or shortness of breath? And could I get your name and age?",
            "$$HUMAN$$ I'm Henry Walsh, I'm 52. No fever, but I do get a bit breathless when it's bad.",
        ],
        "last": "HUMAN",
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
            "$$HUMAN$$ Hi, I'm Karen Voss, 41 years old. I have a runny nose and mild cold symptoms.",
            "$$BOT$$ These sound like minor cold symptoms. I'll book you in for a routine check-up.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-03", "time": "am"},
    },
    {
        "id": "liam",
        "history": [
            "$$HUMAN$$ Hi, I'm Liam Corrigan, I'm 19. My ear has been hurting for two days. Could be an infection.",
            "$$BOT$$ Ear pain that persists warrants a check. I've scheduled a morning appointment for you.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-04", "time": "am"},
    },
    {
        "id": "maya",
        "history": [
            "$$HUMAN$$ Hi, I'm Maya Patel, I'm 26 years old. I lightly sprained my wrist — it's a bit sore but I can move it.",
            "$$BOT$$ Sounds like a mild sprain. Let's have a doctor take a look in the morning.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-05", "time": "am"},
    },
    # --- Scheduled: afternoon (3) ---
    {
        "id": "noah",
        "history": [
            "$$HUMAN$$ Hi, I'm Noah Fletcher, 34. Sore throat for four days. Hurts to swallow.",
            "$$BOT$$ It could be strep. I've scheduled an afternoon appointment — they can do a quick swab.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-03", "time": "pm"},
    },
    {
        "id": "olivia",
        "history": [
            "$$HUMAN$$ Hi, I'm Olivia Strand, I'm 27. I burned my hand on the oven — it's red and a bit blistered.",
            "$$BOT$$ That sounds like a second-degree burn. Please come in this afternoon so we can assess it properly.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-04", "time": "pm"},
    },
    {
        "id": "peter",
        "history": [
            "$$HUMAN$$ Hi, I'm Peter Huang, I'm 48. I've been getting headaches every afternoon this week.",
            "$$BOT$$ Recurring headaches should be looked at. I've booked you an afternoon slot.",
        ],
        "last": "BOT",
        "scheduled": {"date": "2026-03-06", "time": "pm"},
    },
    # --- Escalated (2) ---
    {
        "id": "quinn",
        "history": [
            "$$HUMAN$$ Hi, I'm Quinn Adler, I'm 60 years old. I'm having severe chest pain and my left arm feels numb.",
            "$$BOT$$ These are signs of a possible cardiac emergency. Please call 999 immediately or go to A&E now. Do not drive yourself.",
        ],
        "last": "BOT",
        "escalated": True,
    },
    {
        "id": "rachel",
        "history": [
            "$$HUMAN$$ Hi, I'm Rachel Burns, I'm 44 years old. I fell and have a deep cut on my leg. It won't stop bleeding.",
            "$$BOT$$ This needs immediate attention. Go to A&E or call 999 right away. Apply firm pressure to the wound while you wait.",
        ],
        "last": "BOT",
        "escalated": True,
    },
    # --- No further action (2) ---
    {
        "id": "samantha",
        "history": [
            "$$HUMAN$$ Hi, I'm Samantha Cole. I was wondering if you could tell me your opening hours?",
            "$$BOT$$ We're open Monday to Friday, 8am-6pm. Is there anything medical I can help with?",
            "$$HUMAN$$ No, that's all I needed. Thanks!",
            "$$BOT$$ Happy to help. Take care!",
        ],
        "last": "BOT",
        "no_further_action": True,
    },
    {
        "id": "tom",
        "history": [
            "$$HUMAN$$ Hi, I'm Tom Griffiths. I just wanted to double-check my appointment time.",
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
        yaml.dump(
            conv, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

print(f"Created {len(SEED)} seed conversation(s).")
