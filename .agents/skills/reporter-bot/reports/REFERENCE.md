# Reference

These tools are only for use by the `reporter-bot` skill.

Always invoke from the root of the repository as the working directory.

## Reading the next unreported conversation

```sh
uv run .agents/skills/reporter-bot/reports/report.py next
```

Finds the first terminated conversation (escalated, scheduled, or no-further-action) that does not yet have a corresponding file in `reports/`. Prints the full conversation as YAML:

```yaml
id: <conversation id>
history:
  - $$HUMAN$$ <message>
  - $$BOT$$ <message>
last: BOT
escalated: true          # present if escalated
no_further_action: true  # present if no further action
scheduled:               # present if scheduled
  date: YYYY-MM-DD
  time: am|pm
```

If no unreported conversations remain, prints:

```
# NO PENDING REPORTS
```

## Writing a report

```sh
uv run .agents/skills/reporter-bot/reports/report.py report "<id>" "<yaml text>"
```

Writes the report to `reports/<id>.yaml`. The YAML must include all of the following required keys:

| Key | Description |
|-----|-------------|
| `name` | Patient's name |
| `sex` | Patient's sex |
| `age` | Patient's age |
| `symptoms` | Description of presenting symptoms |
| `triage` | One of: `Minor`, `Moderate`, `Severe` |

Additional keys are allowed. The tool exits with an error if any required key is missing or if `triage` is not one of the three allowed values.

Example:

```sh
uv run .agents/skills/reporter-bot/reports/report.py report "alice" "
name: Alice
sex: Female
age: 34
symptoms: Splitting headache for two days
triage: Minor
"
```

After a successful `report`, that conversation will no longer appear in `next` output.
