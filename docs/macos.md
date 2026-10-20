# Preferências, ícones e apps padrão

`python3 scripts/macos-preferences.py diff` compara somente as chaves declaradas.
`apply` salva valores anteriores (inclusive ausência) antes de aplicar;
`restore --journal PATH` desfaz, recusando mudanças posteriores conflitantes.
O Dock fica sem apps fixados e sem recentes. Finder/apps abertos continuam visíveis.
Algumas preferências passam a valer após reabrir o app ou iniciar nova sessão.

`swift scripts/apply-folder-icons.swift --map macos/folder-icons.json --home "$HOME"`
cria pastas declaradas e aplica os ícones. Adicione .icns em macos/icons/ e entradas
folder/icon relativas ao home e ao diretório do mapa. `--dry-run` não altera nada.
O diário privado impresso permite `--restore PATH`; a pasta criada permanece vazia
se só o ícone for desfeito. O restore recusa ícones modificados posteriormente.

`python3 scripts/default-apps.py diff` mostra quantas associações mudarão.
`apply` usa duti para associar as extensões de macos/default-apps.json ao Sublime Text;
`restore --journal PATH` restaura os handlers anteriores. Sem um handler anterior
recuperável, a etapa para antes de modificar qualquer associação: escolha primeiro
um aplicativo pelo Finder e execute novamente. O backup registra o app de abertura
anterior por extensão; não captura distinções avançadas de roles do Launch Services.

Lista inicial: md, markdown, csv, txt, json, xml, yaml, yml, toml e log.
O usuário pode editar a lista versionada. EDITOR/VISUAL também usam `subl -w`.
A verificação em Mac recém-formatado ainda está pendente.
