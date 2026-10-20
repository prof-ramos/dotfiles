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
