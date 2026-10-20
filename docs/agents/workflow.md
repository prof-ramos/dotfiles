# Agent workflow

Start from this repository as the working root. `scripts/workspace.sh path`
prints its absolute location; `scripts/workspace.sh codex` starts a new Codex
session here, and `scripts/workspace.sh sublime` opens the editor project.
Existing conversation working roots do not change when a shell runs `cd`.

Run `python3 scripts/doctor.py` when diagnosing this Mac. It reports differences
without applying them; absent preference keys do not prove a feature is disabled.
Before installation, use `./bootstrap.sh --stage all --dry-run` to inspect actual
targets, typed preference changes, assets and default-app associations. Optional
modules require `--module`; see `docs/apps.md` for their contents.

Use `./scripts/check.sh` before committing. Install local hooks once with
`./scripts/install-hooks.sh`; commit hooks check the staged snapshot, and push
hooks also scan Git history. CI runs the same command. Failure logs are retained
privately under ~/.local/state/dotfiles/checks/. Missing prerequisites fail closed.

For Matt Pocock skills, use `python3 scripts/install-agent-skills.py grill-me`
(or another skill name). It installs referenced router dependencies in the same
operation. `python3 scripts/skill-doctor.py` diagnoses installed routes without
network access. The helper handles Matt Pocock skill names; it does not rewrite
third-party skills or change other installers.

Record approved scope, pending decisions and verification evidence in a private
execution ledger outside tracked files (for example .superpowers/). Reuse an
existing approval for the same action and scope; present a new decision when the
scope changes or a required review artifact first becomes available. Preserve
any explicit permission or review requirements from applicable instructions.

Prefer focused searches and relevant file sections. Use supported CLI/API
operations for machine-readable state and screenshots for visual verification;
read full UI trees only when choosing an accessible control requires them.

Review restoration using realistic data shapes and component reloads. Preserve
binary plist values, prior user changes and interruption recovery; read-back
success alone is not evidence of the UI's effective state. Mechanical failures
belong in tests/checks. The reviewer evaluates remaining judgement calls.

Public migration notes describe user-visible behavior, backups and limitations.
Keep tool transcripts, temporary task state and internal rulings in the private
ledger rather than expanding public operational documentation.
