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

## Conferência posterior de preferências

Na conferência inicial, o tamanho lido foi 52 e a posição à direita; o perfil
capturado então declarava 68. A divergência não foi sobrescrita nessa ocasião.
A comparação está em docs/research/macos-mathias-applicability.md.
O CI do commit de conclusão passou: https://github.com/prof-ramos/dotfiles/actions/runs/39364296143.

## Sincronização com o Mac em 26/10/2026

O perfil passa a refletir o Dock atual: tamanho 76 e dez aplicativos fixados na
mesma ordem, sem copiar metadados privados. As associações atuais são Obsidian
para Markdown, Cursor para JSON/YAML/TOML e Sublime para CSV/TXT/XML/LOG.
Essa atualização registra o estado observado, sem reaplicar preferências no Mac.
A receita opcional OpenLogi está documentada em docs/apps.md. Credenciais do
shell permanecem em arquivo privado, fora dos arquivos versionados.
