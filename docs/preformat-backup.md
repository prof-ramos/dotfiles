# Recuperar SSH e Zsh após formatar o Mac

O backup privado de 13/11/2026 fica no **1Password**, cofre **Personal**:

| Item | Finalidade |
| --- | --- |
| `Backup pre-formatacao - SSH e Zsh - 20261113-050412` | Documento com a imagem `ssh-zsh-preformat.dmg`, criptografada com AES-256. |
| `Backup pre-formatacao - SSH e Zsh - 20261113-050412 - Senha` | Senha necessária para abrir a imagem. |
| `Backup pre-formatacao - SSH e Zsh - 20261113-050412 - Instrucoes` | Cópia desta documentação, preparada após o snapshot. |

O Git não contém a imagem, a senha, as chaves privadas ou os arquivos privados.
Antes de apagar o Mac, confirme que consegue entrar no 1Password e abrir esses
itens em outro aparelho. A autenticação já aberta neste Mac não comprova essa
independência. Mantenha os meios de recuperação da conta acessíveis fora dele.

## Conteúdo do snapshot

- `home/.ssh/`: configuração atual, chaves existentes, arquivos públicos e de
  confiança dos servidores e cópias locais anteriores. Sockets temporários do
  agente são excluídos porque representam processos, não arquivos restauráveis.
- `home/`: cópias reais de `.zshrc`, `.zprofile`, `.zshenv`, `.aliases`,
  `.functions`, `.exports`, `.p10k.zsh`, `.zsh_secrets`, `.gitconfig.local`,
  `.zsh_ai_risky` e `.tmux.conf`, quando presentes. Os links do shell são
  desreferenciados para preservar seu conteúdo.
- `dotfiles-checkout/`: checkout completo no momento da captura, incluindo `.git`
  e alterações locais ainda não publicadas. Inclui as mudanças então existentes
  em `.zshrc` e `.zprofile`.
- `manifest.json`: hashes SHA-256, permissões dos arquivos e destinos dos links
  simbólicos para conferir a recuperação.

Este é um snapshot pontual, não um backup completo do Mac nem uma sincronização
contínua. Não inclui aplicativos, sessões autenticadas, todo o diretório pessoal
ou os binários privados referenciados por PATH, como `~/.editor-video`.
Alterações feitas depois da captura exigem novo backup. Esta documentação foi
escrita após o snapshot; preserve também a versão atual do repositório.

## Recuperação segura

1. No Mac reinstalado, instale o 1Password e entre na conta existente. Abra o
   documento no cofre **Personal** e baixe `ssh-zsh-preformat.dmg`. Consulte a
   senha no item separado, diretamente no aplicativo; não a cole em comandos,
   conversas ou arquivos versionados.
2. Abra a imagem pelo Finder. Quando solicitado, digite a senha. Copie o
   conteúdo primeiro para uma pasta privada de recuperação, sem substituir os
   arquivos da sua pasta pessoal.
3. Compare os arquivos recuperados com `manifest.json`. Ele permite verificar
   conteúdo e permissões antes de aplicar. O snapshot não corrige referências
   SSH que já apontavam para arquivos inexistentes na origem.
4. Revise `home/.ssh/config` e restaure o diretório `.ssh` preservando permissões:
   diretório `0700`, chaves privadas e configuração `0600`. Não publique esse
   diretório nem o copie para o checkout. Arquivos `known_hosts` guardam a
   confiança capturada; alterações posteriores das chaves dos servidores exigem
   validação independente, sem aceitar chaves automaticamente.
5. Restaure `.zsh_secrets` e `.gitconfig.local` como arquivos privados locais.
   Restaure o checkout em `~/Developer/dotfiles` somente depois de revisar o que
   já existir nesse destino. Use o [fluxo de restauração](restore.md) e o
   [workflow](agents/workflow.md) para inspecionar os links antes de aplicar.
   As cópias regulares em `home/` também permitem recuperar o conteúdo do shell
   sem depender de links antigos. Evite copiar os dois conjuntos por cima um do
   outro sem revisar os conflitos.
6. Reinstale as dependências pelo [README](../README.md) e autentique 1Password,
   GitHub e Tailscale conforme [acesso à infraestrutura](infra.md). Habilite as
   integrações necessárias do 1Password. O backup de arquivos não transfere
   sessões, autorizações do app ou permissões de acesso remoto.
7. Valide o shell, o diagnóstico `python3 scripts/doctor.py` e os acessos SSH
   necessários antes de apagar a pasta de recuperação ou remover o backup.

## Evidências e limites

A verificação executada confirmou o download do documento do 1Password,
abertura com a senha relida do cofre, cópia para uma pasta isolada e comparação
integral de **477 entradas**: hashes SHA-256, permissões e links do manifesto.
Os arquivos privados e do shell foram também comparados com os originais.
`zsh -n` e `git fsck --full` passaram na cópia restaurada. O recibo privado fica em
`~/.local/state/dotfiles/preformat-20261113-050412/receipt.json`.

Há uma cópia adicional criptografada na pasta do iCloud Drive
`Backups/Mac-SSH-Zsh-20261113-050412/`, com `COMO-RECUPERAR.txt` ao lado.
A existência dessa cópia no Mac não comprova a sincronização remota do iCloud.
A cópia no 1Password é o destino usado para o teste de download e restauração.
Nenhum destes testes comprova login em outro aparelho ou autorização em todos
os servidores; confira esses requisitos separadamente antes da formatação.
