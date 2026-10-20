# Dotfiles Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Reconstruir os dotfiles públicos de prof-ramos e migrar este Mac preservando o legado e o caminho de retorno.

**Architecture:** Novo repositório independente em ~/Developer/dotfiles-next. Bootstrap Zsh coordena etapas explícitas; Stow gerencia arquivos de shell na raiz e pacotes de apps. Preferências e ícones são aplicados por scripts próprios, separados da criação de links.

**Tech Stack:** Zsh, GNU Stow, Homebrew Bundle, Python 3 para manifesto/validação, Swift/AppKit para ícones, Git e GitHub CLI.

**Spec:** docs/superpowers/specs/2026-10-19-dotfiles-rebuild-design.md no checkout legado; copiar para o mesmo caminho do novo repositório na tarefa 2.

## Global Constraints

- O novo prof-ramos/dotfiles será público, com histórico independente e créditos e licença dos arquivos reaproveitados.
- Credenciais, chaves privadas, configuração privada de SSH, sessões e transcrições não entram no Git.
- Não formatar o Mac, não apagar o legado e não ampliar permissões de agentes.
- Hermes/VPS e outros sistemas ficam fora da primeira versão.
- O novo checkout fica em ~/Developer/dotfiles-next durante a migração; o checkout antigo permanece onde está.
- Módulos opcionais exigem seleção explícita; executar todas as etapas não seleciona todos os módulos.
- A primeira entrega não equivale à validação de instalação em um macOS recém-formatado.
- Revalidar estado e ferramentas antes de agir; não interpretar valores observados na especificação como estado imutável.

## Review Focus

1. Home temporário e clone com espaços: nenhum link ou escrita deve escapar do destino solicitado.
2. Arquivo local divergente ou link de outro gerenciador: preservar sem substituição silenciosa.
3. Falha no meio da migração: diário e backups devem permitir restaurar cada destino já alterado.
4. Clone público com arquivo sensível inesperado: validação deve bloquear publicação, sem imprimir o segredo.
5. App Store sem login, pasta ausente ou asset inválido: reportar resultado real e permitir retomar a etapa.

## Interfaces e arquivos

Todos os caminhos seguintes são relativos ao novo checkout, exceto a tarefa 1. O pacote Stow da raiz será o nome do checkout, com --dir definido como seu diretório pai. Usar --no-folding para evitar links de diretórios inteiros; a allowlist raiz inclui somente .zshrc, .zprofile, .zshenv, .aliases, .functions, .exports, .gitconfig e .p10k.zsh. Pacotes ghostty/ e sublime/ possuem hierarquia relativa ao home. O manifesto scripts/managed-files.json declara package, source e target de cada arquivo; paths são relativos e não aceitam traversal. Não depender apenas de regex de ignore para definir o conjunto permitido.

- bootstrap.sh: interface `--stage apps|shell|macos|visual|all`, `--module personal|development|security|cloud|media` repetível, `--dry-run`; sem argumentos mostra ajuda e escolhas. Nunca sourcear bootstrap no shell do usuário.
- scripts/links.py: `plan_links(repo: Path, target: Path) -> list[dict]`, CLI `plan|apply|restore --target PATH`; aplicação usa Stow após preflight e decisão de conflito.
- scripts/state.py: `save_backup(path: Path, state_dir: Path) -> dict`, `restore_entry(entry: dict) -> None`; diário JSON registra tipo, origem, destino, backup e estado por operação, sem conteúdo de credenciais.
- scripts/apps.sh: consome Brewfile e modules/<name>/Brewfile; recebe apenas módulos validados pelo bootstrap.
- scripts/macos-preferences.py: CLI `diff|apply|restore`; aplica exclusivamente manifesto macos/preferences/defaults.json e registra valores anteriores, inclusive chaves ausentes.
- scripts/apply-folder-icons.swift: CLI `--map PATH --home PATH --dry-run`; mapa JSON com pares folder/icon, folder relativo ao home, icon relativo ao diretório do mapa; falha com exit não zero se qualquer item falhar.
- scripts/validate.py: CLI `--repo PATH`; valida manifesto, allowlist pública, assets e arquivos declarados.
- Estado de aplicação: ~/Library/Application Support/dotfiles/backups/<run-id>/, fora do Git; usar modo privado para backups.

## Task 1: Preservar o legado

**Files:** checkout atual, backup externo e docs/migration-inventory.md local até revisão de dados privados.
**Interfaces:** produz baseline Git e inventário de destinos gerenciados; não modifica links.

- [x] Conferir git status, remotes, branch, arquivos staged e instruções locais; ler os quatro diffs mencionados na especificação e detectar mudanças adicionais.
- [x] Criar backup privado do estado modificado e lista dos links com readlink/lstat; registrar checksum dos arquivos de configuração relevantes sem expor seus conteúdos.
- [x] Revisar diff para informações privadas e preservar alterações deliberadamente no legado. Não usar git add .; registrar commits e arquivos que permanecerem exclusivamente locais.
- [x] Verificar backup e git status contra inventário: nenhum arquivo alterado desapareceu. Não renomear remoto nem arquivar nesta tarefa.

## Task 2: Núcleo instalável e configuração de shell

**Files:** bootstrap.sh, Brewfile, .zshrc, .zprofile, .zshenv, .aliases, .functions, .exports, .gitconfig, .p10k.zsh, .gitignore, .stow-local-ignore, scripts/apps.sh, scripts/install-shell-deps.sh, scripts/zsh-deps.lock, scripts/managed-files.json, README.md, LICENSE-MIT.txt, docs/attribution.md, tests/test_bootstrap.py.
**Interfaces:** produz bootstrap e manifesto consumidos pela tarefa 3; execução sem --stage não instala nada.

- [x] Criar diretório novo somente se ausente ou vazio, inicializar histórico independente e copiar especificação/plano aprovados. Inspecionar upstream Mathias em leitura, fixar SHA usado e manter licença e créditos dos arquivos realmente reutilizados.
- [x] Escrever testes comportamentais com executáveis fake: `test_help_has_no_effect`, `test_all_does_not_select_optional_modules`, `test_invalid_module_fails_before_install`, `test_apps_failure_stops_later_stages`. Asserções: chamadas e códigos de saída, zero efeito fora do temporário.
- [x] Rodar `python3 -m unittest discover -s tests -p 'test_bootstrap.py' -v`; confirmar falha por bootstrap ainda ausente.
- [x] Implementar interfaces declaradas. Núcleo Brewfile: git, stow, python, zsh-autosuggestions, zsh-syntax-highlighting; casks ghostty, sublime-text, codex e font-jetbrains-mono-nerd-font. Verificar os identificadores no Homebrew antes de fixar. Zsh é o shell do sistema; não mudar login shell automaticamente.
- [x] Migrar plugins e pins atuais compatíveis; remover caminhos fixos de usuário. .zshenv mínimo, configuração interativa em .zshrc, PATH/login em .zprofile; arquivos separados são sourceados uma vez. Registrar qualquer dependência adicional exigida pelos plugins, incluindo autojump se preservado.
- [x] Rodar testes, `zsh -n` em cada script e config Zsh; documentar CLT/Homebrew e retomada após instalação manual de CLT. Commit somente arquivos desta tarefa.

## Task 3: Links, conflitos e retorno

**Files:** scripts/links.py, scripts/state.py, scripts/managed-files.json, .stow-local-ignore, tests/test_links.py, docs/restore.md.
**Interfaces:** implementa plan_links, save_backup, restore_entry e CLIs declaradas; plano precede qualquer mutação.

- [x] Escrever testes: `test_clone_and_home_with_spaces`, `test_root_package_links_only_allowlist`, `test_divergent_file_is_preserved_without_decision`, `test_foreign_symlink_not_followed`, `test_second_apply_is_unchanged`, `test_restore_after_partial_failure`, `test_traversal_rejected`. Comparar lstat/readlink, bytes e destinos esperados; simular falha após primeira operação.
- [x] Rodar `python3 -m unittest discover -s tests -p 'test_links.py' -v`; confirmar falhas pelas interfaces ausentes.
- [x] Implementar preflight global antes de alterar destinos. Usar subprocess argv para Stow, sem shell interpolation; --no-folding e exclusões explícitas. Conflitos interrompem execução não interativa e, na interativa, apresentam diff e decisão de backup/substituição. Diretórios ancestrais com symlink abortam a escrita.
- [x] Registrar operação antes/depois e backup privado com run-id único; restore restaura somente itens comprovadamente pertencentes à execução, sem apagar alterações posteriores silenciosamente.
- [x] Rodar testes com Stow real em home temporário; conferir que scripts, docs, assets e módulos não foram ligados. Documentar restauração e fazer commit.

## Task 4: Apps opcionais e editor

**Files:** modules/{personal,development,security,cloud,media}/Brewfile, ghostty/Library/Application Support/com.mitchellh.ghostty/config.ghostty, sublime/Library/Application Support/Sublime Text/Packages/User/, scripts/managed-files.json, tests/test_public_files.py, docs/apps.md.
**Interfaces:** módulos escolhidos alimentam apps.sh; pacotes de apps usam links.py.

- [x] Classificar inventário completo do Brewfile legado nas cinco listas e apresentar tabela concreta ao usuário para revisão antes de fechar seleção. Telegram somente cask; App Store é opcional e requer conta local autenticada. Não executar os módulos por classificá-los.
- [x] Escrever testes do validador: `test_private_key_and_token_files_rejected`, `test_sublime_sessions_and_license_rejected`, `test_app_packages_have_exact_destinations`; usar fixtures sintéticas sem segredos reais. Confirmar que falham antes de implementar validações.
- [x] Capturar Ghostty e apenas preferências/atalhos/plugins visuais aprovados de Packages/User. Preservar JSONC do Sublime, incluindo comentários e vírgulas finais, com parser apropriado ou API do Sublime; não usar json.loads sobre arquivo JSONC.
- [x] Registrar Package Control e Codex pelo mecanismo oficial de instalação, sem copiar vendor. Não alterar permissões/modelo/autenticação. Incluir família JetBrainsMono NFM 15 e ligaturas, Markdown, XML e aparência do chat. Verificar compatibilidade da versão CLI com o plugin antes de declarar integração funcional.
- [x] Implementar scripts/validate.py com allowlist dos arquivos publicáveis e rejeição de arquivos inesperados; revisar manualmente diffs para valores sensíveis. Testar inventário, JSONC no Sublime e links temporários. Commit dos arquivos revisados.

## Task 5: Preferências e ícones

**Files:** macos/preferences/defaults.json, macos/icons/infra.icns, macos/folder-icons.json, scripts/macos-preferences.py, scripts/apply-folder-icons.swift, tests/test_macos_preferences.py, tests/test_folder_icons.py, docs/macos.md.
**Interfaces:** implementa diff/apply/restore e mapa de ícones; nenhuma ação real em dry-run.

- [x] Escrever testes com backend defaults fake: `test_missing_key_restored_by_delete`, `test_apply_uses_selected_keys_only`, `test_dry_run_has_no_mutations`; confirmar falha antes da implementação.
- [x] Reutilizar lógica revisada do script legado quando útil; capturar apenas chaves selecionadas atuais e declarar persistent-apps vazio e show-recents false. Backup registra tipo/ausência e restore respeita ambos. Não importar .macos upstream em bloco.
- [x] Copiar infra.icns original, validar decodificação NSImage e registrar mapa `[{"folder":"Developer/infra","icon":"icons/infra.icns"}]`.
- [x] Implementar Swift/AppKit e testes de integração macOS em pasta temporária: `test_missing_folder_created`, `test_invalid_icon_reports_failure`, `test_dry_run_creates_nothing`, `test_paths_cannot_escape_home`. Verificar retorno setIcon e metadados do ícone após sucesso; impedir traversal e symlinks ancestrais.
- [x] Para reaplicação do ícone real, guardar estado anterior recuperável (ícone customizado e indicador de ausência) fora do Git antes de modificar; restore remove ícone customizado apenas quando antes ausente. Falha na captura aborta alteração.
- [x] Executar testes e typecheck Swift; documentar execução por etapa, backup/restore e ausência de teste em Mac formatado. Commit.

## Task 6: Validação integrada, publicação e migração

**Files:** tests/test_setup.py, docs/migration.md, docs/restore.md, README.md, .github/workflows/validate.yml.
**Interfaces:** usa todas as CLIs e diário; produz relatório local de execução e pendências reais.

- [x] Criar `test_full_plan_is_read_only` e `test_twice_applied_temp_home_has_stable_links`: plan/dry-run não instala apps nem altera defaults; reaplicação em temporário conserva destinos e conteúdo. Falhas externas simuladas não produzem mensagem falsa de conclusão.
- [x] Rodar suite completa, zsh -n, validação pública e inspeção Stow; configurar CI sem aplicação real de defaults ou acesso a credenciais. Revisar todo o diff e publicar somente arquivos examinados.
- [x] Apresentar lista final de módulos/apps, mudanças reais, backups e comandos GitHub antes do corte. Resolver qualquer mudança de escopo com o usuário. A migração e publicação já foram autorizadas; não repetir pedidos de permissão sem nova razão concreta.
- [x] Conferir namespace remoto imediatamente antes de renomear. Renomear atual via `gh repo rename dotfiles-legacy --repo prof-ramos/dotfiles --yes`; ajustar origin legado. Criar novo remoto público sem force-push, conferir origin e publicar main do checkout novo. Se nome ocupado ou publicação falhar, parar corte local e registrar estado retomável.
- [x] Aplicar módulos efetivamente escolhidos, com backups, depois trocar apenas links inventariados. Configuração privada de SSH fica local, com arquivo de exemplo no Git e acesso atual preservado. Não mover a pasta antiga.
- [x] Conferir shell/login/interatividade, destinos Ghostty/Sublime, SSH sem conexão de teste não autorizada, preferências e ícone. Conferir visual do Codex sem enviar prompts. Resolver falhas antes de arquivar legado.
- [x] Arquivar remoto legado com `gh repo archive prof-ramos/dotfiles-legacy --yes` somente após verificações passarem. Manter checkout e backups locais. Atualizar documentação/relatório e fazer commit final no novo.
- [x] Relatar commits/remotos finais, etapas aplicadas, módulos não executados, backups, rollback e teste de formatação pendente. Não declarar sucesso de autenticações ou instalações não verificadas.

## Auto-revisão do plano

Cobertura: preservação/troca de repositórios nas tarefas 1/6; bootstrap e shell em 2; Stow e rollback em 3; módulos, fontes e apps em 4; macOS e ícones em 5. Os cinco riscos de Review Focus têm verificações nas tarefas 2–6. Interfaces e caminhos são consistentes. Configurações simples terão validação de sintaxe e inspeção, sem testes que apenas repitam seus valores.

## Handoff

Aguardar revisão deste plano e escolha entre execução nativa (executing-plans) e execução por subagentes (subagent-driven-development). Recomendada execução nativa: as tarefas compartilham estado deste Mac e o corte remoto/local é sequencial. Em qualquer método, concluir com revisão independente do conjunto antes do corte.
