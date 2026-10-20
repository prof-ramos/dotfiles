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

`diff` identifica cada chave e seus valores atuais/propostos, resumindo estruturas
binárias. `verify` retorna erro se houver diferenças; `verify --reload` reinicia
o Dock antes de conferir. `apply` verifica as escritas e recarrega o Dock quando
modifica esse domínio, guardando o journal antes de qualquer alteração.
`python3 scripts/doctor.py` reúne preferências, links, apps e ferramentas em uma
consulta de leitura. O preview do bootstrap também mostra esses destinos.

## Atalhos de janelas e terminal

O Magnet é o responsável pelo posicionamento de janelas. Neste Mac, a extensão
Window Management do Raycast foi desativada pela interface, pois tinha atalhos
sobrepostos ao Magnet. Essa escolha do Raycast é local: não é aplicada pelo
bootstrap nem exige exportar o banco privado do aplicativo. Após uma formatação,
desative essa extensão em Raycast Settings > Window Management.

| Ação | Atalho |
| --- | --- |
| Alternar janelas da aplicação (macOS) | `⌘ + crase` |
| Terminal rápido (Ghostty) | `⌃ + crase` |
| Metades (Magnet) | `⌃⌥ + setas` |
| Maximizar (Magnet) | `⌃⌥ + Return` |
| Centralizar (Magnet) | `⌃⌥ + C` |
| Monitor anterior/próximo (Magnet) | `⌃⌥⌘ + ←/→` |

A configuração do Ghostty é versionada e ligada pelo Stow; os atalhos do Magnet
acima descrevem a configuração local observada, sem importação automática.
Recarregue a configuração pelo menu do Ghostty ou reabra o aplicativo para ativar
uma alteração de atalho global. A validação do arquivo não comprova registro do
atalho nem permissões de Acessibilidade. Não foi possível testar o terminal rápido
nesta sessão: a automação de interface bloqueou o acesso ao Ghostty.
