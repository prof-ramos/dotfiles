# Agent navigation

- Before editing or reviewing: read `docs/agents/workflow.md`.
- Checks and hook installation: `scripts/check.sh`, `scripts/install-hooks.sh`.
- Before changing installed settings: `scripts/doctor.py` and `scripts/managed-files.json`.
- Before applying or restoring: `docs/restore.md` and `docs/macos.md`.
- Optional apps: `docs/apps.md`. Proposed macOS changes: `docs/research/`.

## Memória dos agentes de código

Para conectar os clientes ao servidor na tailnet, siga [a instalação e os
testes do ai-memory](docs/ai-memory.md). Mantenha o token fora do Git.

## Agent skills

### Issue tracker

Track issues and specs in GitHub Issues for `prof-ramos/dotfiles`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the five standard triage roles. See `docs/agents/triage-labels.md`.

### Domain docs

Single context: root `GLOSSARY.md` and `docs/adr/`, created when needed. See `docs/agents/domain.md`.
