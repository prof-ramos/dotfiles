# Backups e retorno

`python3 scripts/links.py plan --target "$HOME"` mostra mudanças e diffs.
`apply` recusa conflitos; depois de revisar, `apply --replace` preserva os
arquivos anteriores em backup privado antes de substituí-los.
O diário é impresso ao aplicar. Para desfazer:

```sh
python3 scripts/links.py restore --journal '/caminho/impresso/journal.json'
```

Arquivos alterados depois da aplicação não são sobrescritos pelo restore.
Links são restaurados com o destino anterior, sem copiar chaves ou arquivos
privados para o repositório. Backups permanecem em
~/Library/Application Support/dotfiles/backups/. Não apagar esse diretório
antes de terminar a validação da migração.

Os journals anteriores a 31/10/2026 podem registrar ~/Developer/dotfiles como
origem do checkout legado. Desde a renomeação, esse caminho identifica o checkout
ativo; o legado está em ~/Developer/dotfiles-legacy. Revise os destinos históricos
antes de restaurar: aplicar esses caminhos literalmente pode apontar para o checkout
errado. O caminho ~/Developer/dotfiles-next permanece como link de compatibilidade.

## Backup privado antes de formatar

O snapshot criptografado de SSH e Zsh está no 1Password, separado do Git.
Consulte [conteúdo, itens do cofre e recuperação após formatação](preformat-backup.md).
Os backups locais descritos acima não substituem essa cópia fora do Mac.
