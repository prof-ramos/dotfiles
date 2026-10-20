# Validação isolada dos links

Executada em 20/10/2026 sobre o commit `4596cac23fa17b099931f20e0d62b0c94dec2e24`.

Foi exportado o conteúdo do índice Git para um checkout temporário. A validação
usou o manifesto real de 18 arquivos, a CLI `scripts/links.py` e o GNU Stow
instalado. Tanto o checkout quanto os homes temporários tinham espaços no caminho.
Nenhum aplicativo foi instalado e nenhuma preferência do macOS foi aplicada.

| Cenário | Resultado |
| --- | --- |
| Plan listar os 18 destinos sem alterar os arquivos de destino | Passou |
| Aplicar os 18 links, excluindo os arquivos internos do repositório | Passou |
| Segunda aplicação manter os links; restaurar seu journal vazio preservar a instalação inicial | Passou |
| Restaurar a instalação inicial e repetir a restauração | Passou |
| Recusar arquivo existente e symlink externo antes de alterar qualquer destino gerenciado | Passou |
| Com `--replace`, salvar backup privado e restaurar conteúdo, modo e symlink anteriores | Passou |
| Proteger uma edição posterior e retomar a restauração após resolver o conflito | Passou |
| Comparar os destinos gerenciados no home real antes/depois, sem diferenças | Passou |

Também passaram os oito testes existentes de links:

```sh
python3 -m unittest discover -s tests -p test_links.py -v
```

O roteiro de integração foi executado como artefato local; este documento registra
seus resultados, não adiciona um teste automatizado ao CI. Os checkouts e homes
temporários foram removidos ao concluir. O relatório de execução permanece no
estado privado local, fora do Git.

## Limites

A restauração recupera os destinos gerenciados. Diretórios pais vazios e journals
de backup podem permanecer. A proteção contra alterações posteriores não implica
uma transação atômica de todos os arquivos durante a restauração.

Este ensaio não executou o bootstrap completo, a instalação de dependências do
shell, apps, associações de arquivos, ícones ou preferências reais do macOS. Não
validou fontes, login, permissões de Acessibilidade nem atalhos na interface.

A instalação e restauração em macOS limpo continuam pendentes. O próximo ensaio
será seguir apenas o README em uma máquina virtual, instalando somente o núcleo.
