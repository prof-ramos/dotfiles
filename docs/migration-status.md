# Migração concluída em 20/10/2026

Novo repositório: https://github.com/prof-ramos/dotfiles (público).
Legado: https://github.com/prof-ramos/dotfiles-legacy (privado e arquivado).
Checkout ativo: ~/Developer/dotfiles-next. Checkout legado preservado: ~/Developer/dotfiles.

Aplicação: apenas núcleo. Nenhum aplicativo existente foi desinstalado. Os cinco
módulos opcionais permanecem disponíveis e não foram instalados nesta migração.

Verificações: 34 testes locais, validação de arquivos públicos e varredura do
histórico novo sem credenciais detectadas; 18 links conferidos; configuração SSH
preservada byte a byte; zero links antigos nas localizações gerenciadas; shell de
login/interativo usa subl -w; Ghostty +validate-config passou; preferências sem diff.
Dez extensões abrem no Sublime. Ícone infra e entrada do chat Codex conferidos
na interface. Codex foi reinstalado pelo Package Control; SideBarEnhancements
preexistente foi preservado. Não enviamos mensagens ao Codex nem testamos conexões SSH.

Backups privados em ~/Library/Application Support/dotfiles/backups/:
- legacy-20261020-000240/: arquivos locais modificados e inventário inicial.
- migration-ce3b701a52d84d9d847c3299a12ef778/journal.json: SSH, configurações locais e identidade Git.
- ef8d0ab991ec4a0dbfd08765a557806a/journal.json: links/configurações anteriores.
- preferences-2941636a5fbf430c92299dd217a1b5c0/preferences.json: preferências anteriores.
- icons-AC5BA742-CA13-461D-8ECD-DCBDB32C1A11/icons.json: ícone anterior.
- apps-fc8cb480354d4240aabd3ff2e0195a20/apps.json: aplicativos padrão anteriores.

Para voltar, usar os journals conforme docs/restore.md e docs/macos.md, mantendo
ambos os checkouts no lugar. Não apagar backups nem o checkout antigo antes de
terminar a avaliação pessoal. Restores recusam modificações posteriores conflitantes.

Limites: restauração em macOS recém-formatado, autenticações e instalações de
módulos opcionais não foram verificadas. Plugin Codex 1.160.0 declara teste com
CLI 0.160.1; CLI atual 0.163.0 não foi validado enviando prompts. Roles avançadas
de Launch Services não são preservadas individualmente pelo backup de app padrão.

## Decisões registradas durante a execução

- Ruling: use independent approved dotfiles-next checkout on rebuild branch as isolation; no linked worktree of legacy — independent history is required — cost if wrong: workspace relocation.
- Ruling: task-done helper requires nonempty stdout; use explicit verification output for silent git checks — helper grep exits on empty successful output — cost if wrong: reporting only.
- Task 2: Ruling: Zsh reserves modules; renamed array selected_modules — runtime failure caught by bootstrap tests — cost if wrong: bootstrap stops before effects.
- Task 2: Ruling: add gh and duti to core — GitHub migration and user-requested default editor need these CLIs — cost if wrong: two extra packages.
- Task 3: Ruling: canonicalize temporary test root (/var is a macOS system symlink) — production rejects symlink ancestors deliberately — cost if wrong: tests reject otherwise valid system aliases.
- Task 4: Ruling: Ghostty uses JetBrainsMono NFM — standardize core font preserving its theme — cost if wrong: reversible visual preference.
- Task 4: Ruling: synthetic private-key marker assembled in test fixture to avoid scanner false positive in test source — same runtime fixture — cost if wrong: fixture-only detection gap.
- Task 5: Ruling: default text extensions are md, markdown, csv, txt, json, xml, yaml, yml, toml, log — explicit finite interpretation of user's etc — cost if wrong: reversible associations.
- Task 5: Ruling: duti backs up principal opening app per extension, not advanced separate Launch Services roles — standard personal setup, documented limit — cost if wrong: custom role-specific mappings require manual restoration.
- Task 6: Ruling: run final independent review after integrated code/tests but before external cut, then verify real migration — plan placed publication inside final task — cost if wrong: extra verification ordering only.
- Task 6: Ruling: preserve legacy-only tmux, risky-alias and SSH symlinks as local files rather than new public packages — no optional setup implicitly enabled — cost if wrong: local files no longer version-managed until selected for future migration.
- Final: Ruling: CI prerequisite graded Important rather than Minor; shell tests now provide temporary subl executable fallback — CI runner lacks Sublime — cost if wrong: test fixture does not exercise GUI installation.
- Final: Ruling: icon resource-map handles vary per folder; fingerprint stable data payload and custom flag, not resource-map runtime metadata — reproduced differing resource map with identical payload — cost if wrong: metadata-only edits do not block restore.
- Final: Ruling: pending operational checks follow code review; fresh formatted macOS, App Store authentication and optional installs stay untested; no live SSH connection or Codex prompt is sent — explicit scope — cost if wrong: integrations may need manual authentication or compatible CLI.
- Final: Ruling: principal Launch Services opening app is restoration unit, not separate roles — documented personal setup limitation — cost if wrong: advanced role mappings need manual recovery.
- Final: Ruling: public working-tree and full new Git history scanning required before push; legacy history remains private — original repo observed PRIVATE — cost if wrong: scanner cannot guarantee absence of every secret pattern.
- Final: Ruling: concurrent hostile filesystem races and upstream integrity beyond pinned SHAs are outside personal bootstrap threat scope — no privilege escalation or concurrent writer assumed — cost if wrong: TOCTOU or compromised upstream may evade checks.
- Task 6: Ruling: retain SideBarEnhancements in Package Control manifest — prior private backup proved it was installed before migration — cost if wrong: one additional editor extension restored.

Nenhum achado menor foi adiado; o problema de CI foi reclassificado e corrigido.
