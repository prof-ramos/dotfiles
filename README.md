## Dotfiles — Backup Automático e Manual (macOS)

Este repositório contém automações para backup de dotfiles no macOS, com três formas de execução:

- Manual: `scripts/backup_manual.sh`
- Automático local (cron): `scripts/install_cron.sh`
- Automático remoto (GitHub Actions): `.github/workflows/backup.yml`

Cada execução gera um tarball no diretório do projeto com o padrão `dotfiles-${HOSTNAME}-${TIMESTAMP}.tar.gz` e faz commit/push automático (quando habilitado).

### Itens incluídos

- Arquivos comuns de shell e Git: `.zshrc`, `.zprofile`, `.gitconfig`, etc.
- Diretórios de configuração como `.config/` e `.ssh/` (somente `config`, chaves privadas são excluídas)
- Preferências do VS Code (settings, keybindings e snippets)
- Outras preferências úteis (ex.: iTerm2)

Listas completas em `backup/include.lst` e `backup/exclude.lst`.

### Segurança e privacidade

- Chaves privadas e materiais sensíveis são excluídos por padrão (`.ssh/id_*`, `.ssh/*_key`, `.gnupg/**` etc.)
- Nunca armazene segredos em texto claro neste repositório

### Scripts

- `scripts/dotfiles_backup.sh`: script principal. Fluxo:
  1. Copia itens do `$HOME` com `rsync` (listas de include/exclude)
  2. Exporta `Brewfile` e extensões do VS Code (se disponíveis)
  3. Gera inventário (`inventory.txt`) e manifesto (`manifest.sha256`)
  4. Gera o tarball em `./`
  5. (Opcional) Commit e push (`DO_GIT=1`)

- `scripts/backup_manual.sh`: executa o backup com `DO_GIT=1` no diretório do projeto.

- `scripts/install_cron.sh`: instala uma tarefa diária às 02:15 que executa o backup e registra logs em `logs/cron.log`.

### GitHub Actions

Workflow em `.github/workflows/backup.yml` roda diariamente às 05:00 UTC ou via disparo manual. No contexto de CI ele pula a coleta de `$HOME` e exportações de Brew/VS Code, mas ainda gera metadados e o tarball para registrar o estado e manter o repositório atualizado.

### Variáveis de ambiente

- `PROJECT_DIR`: diretório do projeto (padrão: `/Users/gabrielramos/dotfiles`)
- `DO_GIT`: quando `1`, adiciona o tarball ao Git, faz commit e push
- `DRY_RUN`: quando `1`, apenas simula
- `SKIP_HOME`: quando `1`, não coleta itens do `$HOME`
- `SKIP_BREW`: quando `1`, não exporta `Brewfile`
- `SKIP_VSCODE`: quando `1`, não exporta extensões do VS Code

### Uso rápido

Manualmente:

```bash
/bin/zsh /Users/gabrielramos/dotfiles/scripts/backup_manual.sh
```

Instalar cron:

```bash
/bin/zsh /Users/gabrielramos/dotfiles/scripts/install_cron.sh
```

Executar direto o script principal (exemplo com dry-run):

```bash
DRY_RUN=1 DO_GIT=0 /bin/zsh /Users/gabrielramos/dotfiles/scripts/dotfiles_backup.sh
```
