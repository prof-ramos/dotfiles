# Migração do legado

Novo checkout em ~/Developer/dotfiles-next; legado permanece em ~/Developer/dotfiles.
Não renomear pastas antes de reconfigurar todos os links. Só o repositório GitHub
passa a dotfiles-legacy; o novo dotfiles tem histórico independente.

1. Backup privado e commits preservam alterações atuais.
2. Validar scripts, arquivos públicos e links em home temporário.
3. Revisão independente antes do corte remoto e local.
4. Renomear remoto antigo, ajustar origin local, criar/publicar novo remoto.
5. Instalar somente núcleo, migrar links revisados com backup e aplicar macOS/visual.
6. Desvincular configurações privadas de SSH e configurações antigas ainda em uso,
   preservando-as como arquivos locais e mantendo backup dos links anteriores.
7. Conferir destinos e apps; arquivar legado apenas após sucesso.

Não desinstalar apps ou dependências de módulos que não foram selecionados.
As listas de módulos em docs/apps.md ficam disponíveis, sem instalação automática.
No Mac novo, autenticar GitHub, Codex e App Store manualmente, quando necessário;
restaurar chaves privadas e ~/.zsh_secrets do armazenamento privado.

Git usa ~/.gitconfig.local para identidade. SSH usa ~/.ssh/config local.
A reversão dos links usa o journal privado: veja docs/restore.md. Preferências,
ícones e apps padrão possuem journals próprios: veja docs/macos.md.
Reverter nomes remotos via GitHub apenas após avaliar possíveis novos clones;
nenhum force-push ou exclusão é necessário para a migração.

A validação em Mac recém-formatado permanece pendente.
