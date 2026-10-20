# Dotfiles de prof-ramos

Setup pessoal para macOS Apple Silicon, inspirado na organização do Mathias Bynens,
com Zsh, Stow e etapas independentes. Credenciais e estado de aplicativos ficam locais.

```sh
./bootstrap.sh --stage all --dry-run
./bootstrap.sh --stage apps
./bootstrap.sh --stage shell
./bootstrap.sh --stage macos
./bootstrap.sh --stage visual
```

Instale Command Line Tools quando solicitado e execute novamente após concluir.
O bootstrap instala Homebrew pela fonte oficial quando ausente. Não use `source`.
Apps de outros módulos só entram com `--module personal|development|security|cloud|media`.
Sublime Text é EDITOR/VISUAL com espera (`subl -w`). Git usa identidade local em
~/.gitconfig.local. Autenticações são manuais; senhas e chaves privadas não entram no Git.
Validação: `python3 -m unittest discover -s tests -v`.

Listas opcionais: [apps](docs/apps.md). Personalização: [macOS](docs/macos.md).
Migração e retorno: [migração](docs/migration.md), [backups](docs/restore.md).
Fontes e licença: [créditos](docs/attribution.md).

Antes de substituir arquivos, rode `python3 scripts/links.py plan --target "$HOME"`.
Se houver conflito, o instalador para; após revisar, aplique com
`python3 scripts/links.py apply --target "$HOME" --replace` para guardar backups.
SSH, identidade Git e credenciais são locais. Copie seus dados privados antes de formatar.
A configuração do Package Control declara Codex; no Mac novo, instalar Package Control
pela paleta do Sublime. A instalação de apps não efetua login automaticamente.

Registro da aplicação neste Mac: [migração concluída](docs/migration-status.md).

Checks locais e do CI: `./scripts/check.sh` (adicione `--history` para o histórico).
Ative os hooks uma vez: `./scripts/install-hooks.sh`. O commit verifica o índice,
e o push verifica também o histórico. Pré-requisitos adicionais: Stow e Gitleaks;
o Brewfile do núcleo instala ambos. Logs ficam em ~/.local/state/dotfiles/checks/.

Diagnóstico sem alterações: `python3 scripts/doctor.py` (`--json` para automação).
Diferenças retornam código 1 para serem revisadas, não são corrigidas automaticamente.
`python3 scripts/macos-preferences.py verify --reload` recarrega o Dock e verifica
persistência; `apply` também recarrega o Dock quando modifica suas preferências.

Workspace: `./scripts/workspace.sh sublime` ou `./scripts/workspace.sh codex`.
Instalação de skills com dependências: veja [fluxo de agentes](docs/agents/workflow.md).

Validação de arquivos em home temporário: [resultados e limites](docs/research/isolated-links-validation.md).
