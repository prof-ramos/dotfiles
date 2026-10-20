# Reconstrução dos dotfiles

Status: especificação aprovada; implementação e migração concluídas. Ver docs/migration-status.md.

## Objetivo e critérios de sucesso

Construir um setup pessoal menor, compreensível e reaplicável para o MacBook Air M3 de 13 polegadas. Usar a organização de mathiasbynens/dotfiles como referência, adaptada ao Zsh e às escolhas do usuário. Preservar o repositório atual e seu histórico como prof-ramos/dotfiles-legacy. O novo prof-ramos/dotfiles será público, com histórico independente e créditos e licença dos arquivos reaproveitados.

A primeira entrega inclui documentação, validação em diretório temporário, aplicação neste Mac e conferência dos links. Não equivale à validação de instalação em um macOS recém-formatado; esse teste permanecerá explicitamente pendente.

## Estado atual observado

O checkout atual está em ~/Developer/dotfiles, branch main, origin https://github.com/prof-ramos/dotfiles.git. O repositório remoto não está arquivado. Existem modificações locais em Brewfile, README.md, terminal/README.md e zsh/.zshrc. Revisar os diffs e preservar essas mudanças antes de qualquer migração; nunca descartá-las ou incluí-las inadvertidamente no commit desta especificação.

Stow gerencia zsh, p10k, ghostty, ssh e tmux. Links relativos do diretório pessoal apontam para o checkout atual, incluindo arquivos Zsh, Powerlevel10k, tmux, SSH e Ghostty. Renomear o diretório local quebra esses links; colocar outro checkout no mesmo caminho pode redirecioná-los silenciosamente. Renomear apenas o repositório GitHub não altera os links locais.

## Organização aprovada

```text
dotfiles/
  bootstrap.sh
  Brewfile
  .zshrc
  .zprofile
  .zshenv
  .aliases
  .functions
  .exports
  .gitconfig
  .stow-local-ignore
  ghostty/
  sublime/
  macos/
    preferences/
    icons/infra.icns
    folder-icons.json
  modules/
    personal/
    development/
    security/
    cloud/
    media/
  scripts/
  docs/
```

Os arquivos de shell na raiz constituem um pacote Stow explícito: limitar o conjunto por ignore rules para que scripts, documentação, Brewfiles, assets e módulos não sejam ligados ao diretório pessoal. Os diretórios ghostty e sublime serão pacotes com a hierarquia dos destinos. Implementação e validação devem demonstrar o conjunto exato de links antes de aplicá-los. O bootstrap resolve caminhos a partir da própria localização e não depende do nome do usuário ou do diretório do clone.

## Instalação e módulos

O núcleo contém Homebrew, Git, Stow, Zsh com Oh My Zsh, Powerlevel10k, sugestões e destaque de sintaxe, Ghostty, Sublime Text, Codex CLI e JetBrains Mono Nerd Font, com suas dependências necessárias. Manter os plugins usados no shell atual quando compatíveis; aliases, funções e variáveis ficam separados.

Registrar instalações Homebrew em Brewfile. Desenvolvimento adicional, segurança/pentest, cloud e mídia ficam em módulos opcionais. Apps pessoais e da App Store ficam em uma etapa selecionável. Usar o inventário atual como ponto de partida e apresentar a lista concreta antes de fechá-la; não instalar toda a coleção por inferência. Para Telegram, manter apenas a origem Homebrew cask, eliminando a duplicação com a App Store na nova declaração. Autenticação da App Store e demais serviços permanece manual e documentada.

O bootstrap permite executar o conjunto inteiro escolhido ou etapas isoladas: instalação de apps, shell/links, preferências do macOS e personalização visual. Reexecução não duplica configurações. Instalação de módulos opcionais exige seleção explícita; executar tudo não significa selecionar todos os módulos.

## Configurações e dados privados

Stow administra links simbólicos. Arquivos existentes com conteúdo diferente são preservados: mostrar o conflito/diff, oferecer backup e obter decisão antes de substituir. A validação temporária não aplica preferências reais do macOS nem instala apps.

Senhas, tokens, chaves privadas e configuração privada de hosts SSH não entram no Git. Versionar exemplos genéricos e documentar o arquivo local de SSH e sua inclusão. Preservar os acessos atuais durante a troca. Não copiar automaticamente configurações ou históricos de agentes que contenham dados privados. A configuração pública do Git não deve herdar a identidade do Mathias; obter a identidade local existente sem divulgá-la em logs.

## Personalização do macOS e do editor

Preservar as preferências atuais selecionadas, conferidas novamente no momento da captura. Incluir Dock sem aplicativos fixados e sem apps recentes; Finder e aplicativos abertos continuam sujeitos ao comportamento normal do macOS. Não executar o .macos do Mathias inteiro: novos ajustes exigem revisão individual. Preferências devem ter comparação prévia e backup para reversão.

Capturar deliberadamente os arquivos locais de Sublime aprovados nesta conversa: fonte JetBrains Mono Nerd Font com ligaturas, 15 pontos, ajustes para tela de 13 polegadas, Markdown, XML e aparência do chat Codex. Personalizações ficam em Packages/User. Não versionar caches, sessões, transcrições, licença, tokens ou dependências instaladas do Package Control. Registrar os pacotes necessários por nome. A configuração visual do chat não altera permissões, modelos ou autenticação do Codex.

Guardar o arquivo original ~/Downloads/infra.icns como macos/icons/infra.icns. folder-icons.json associa ~/Developer/infra ao asset relativo. Um script nativo usa NSWorkspace.setIcon; expande o diretório pessoal e resolve assets a partir do repositório. Criar a pasta vazia se ausente. Em erro de leitura ou aplicação, reportar a falha sem afirmar sucesso. Permitir reaplicar a etapa isoladamente.

## Migração e retorno

1. Revisar e preservar o estado local modificado do legado em backup e commits deliberados, após inspeção de dados privados.
2. Construir o novo checkout em ~/Developer/dotfiles-next; manter o checkout atual no lugar durante a preparação.
3. Validar configuração, scripts e links contra um diretório pessoal temporário. Listar alterações planejadas neste Mac.
4. Renomear o remoto atual para prof-ramos/dotfiles-legacy, atualizar seu origin local e criar o novo prof-ramos/dotfiles público com histórico próprio.
5. Migrar apenas os links gerenciados conhecidos, com backups e registro da origem e do destino. Não apagar ou mover diretórios pessoais inteiros. O novo checkout pode permanecer em dotfiles-next durante a validação; qualquer mudança posterior de caminho exige relink explícito.
6. Aplicar as etapas escolhidas neste Mac e conferir shell, Ghostty, Sublime, SSH, preferências e ícone.
7. Arquivar o repositório legado somente depois de validada a migração. Preservar o checkout e backups para retorno.

O retorno restaura os arquivos copiados, os links com seus destinos originais e as preferências a partir dos backups. Não desinstalar apps nem remover dados para desfazer a migração. Documentar quais ações externas ocorreram e como reverter nomes/arquivamento se necessário.

## Validação proporcional

Verificar sintaxe dos scripts e arquivos de configuração. Exercitar links e conflitos em diretório temporário, repetindo a aplicação para detectar duplicações ou mudanças indevidas. Garantir exclusão de segredos, caches e arquivos não destinados ao Stow. Conferir visualmente Sublime e ícone; conferir links e funcionamento dos componentes efetivamente migrados. Não afirmar validação de funcionalidades ou módulos não executados.

## Limites

Hermes/VPS e outros sistemas ficam fora da primeira versão. As fontes do Mathias servem como referência; a decisão de migrar não autoriza executar suas preferências em bloco. Não formatar o Mac, não apagar o legado e não ampliar permissões de agentes. O próximo passo após a revisão desta especificação é escrever o plano de implementação e escolher seu modo de execução.
