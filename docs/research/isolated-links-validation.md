# Validação isolada dos links

Os links podem ser exercitados em um home temporário antes de aplicar o perfil
no Mac. Use um checkout temporário do repositório e um diretório de destino
separado, mantendo ambos disponíveis até terminar a restauração.

```sh
python3 scripts/links.py plan --target '/caminho/home temporário'
python3 scripts/links.py apply --target '/caminho/home temporário'
python3 scripts/links.py restore --journal '/caminho/impresso/journal.json'
```

O manifesto em `scripts/managed-files.json` define os destinos. Arquivos existentes
e symlinks externos causam conflito; `apply --replace` guarda backup privado antes
de substituí-los. A reaplicação preserva links corretos. Para desfazer a instalação
inicial, use o journal dessa instalação: um journal de reaplicação sem mudanças
não remove links criados anteriormente.

A restauração recusa sobrescrever edições posteriores. Resolva o conflito antes
de repetir o comando, preservando o journal e os backups. Veja docs/restore.md.

## Limites

A restauração recupera os destinos gerenciados. Diretórios pais vazios e journals
de backup podem permanecer. A proteção contra alterações posteriores não implica
uma transação atômica de todos os arquivos durante a restauração.

Exercitar links isoladamente não verifica o bootstrap completo, dependências do
shell, apps, associações de arquivos, ícones ou preferências reais do macOS, nem
fontes, login, permissões de Acessibilidade e atalhos na interface.

A instalação e restauração em macOS limpo continuam pendentes. Resultados de
execuções locais ficam em registros privados, fora dos arquivos versionados.
