# ai-memory nos agentes de código

O `ai-memory` guarda memória entre sessões de agentes de código. Neste
ambiente o servidor é acessível por HTTPS dentro da tailnet. Consulte o inventário privado `infra` para obter o endereço MagicDNS
completo e o 1Password para obter o token autorizado. O bootstrap deste
repositório instala os clientes pelos respectivos módulos. Execute este
procedimento depois de entrar no Tailscale.

## Instalar o cliente macOS

Use a mesma versão do servidor. A instalação validada usou a 3.4.2 em Apple
Silicon. Os comandos abaixo verificam os SHA-256 publicados antes de instalar
o binário e os scripts oficiais. Rode o bloco em Bash.

```bash
(
  set -euo pipefail
  umask 077
  version=3.4.2
  release="https://github.com/akitaonrails/ai-memory/releases/download/v$version"
  scratch="$(mktemp -d)"
  data_dir="$HOME/.local/share/ai-memory"
  trap 'rm "$scratch/ai-memory-macos-aarch64.tar.gz" "$scratch/ai-memory-macos-aarch64.tar.gz.sha256" "$scratch/ai-memory-hooks.tar.gz" "$scratch/ai-memory-hooks.tar.gz.sha256" "$scratch/ai-memory" 2>/dev/null || :; rmdir "$scratch" 2>/dev/null || :' EXIT

  for asset in ai-memory-macos-aarch64.tar.gz ai-memory-hooks.tar.gz; do
    curl -fsSL "$release/$asset" -o "$scratch/$asset"
    curl -fsSL "$release/$asset.sha256" -o "$scratch/$asset.sha256"
    expected="$(awk 'NR == 1 { print $1 }' "$scratch/$asset.sha256")"
    actual="$(shasum -a 256 "$scratch/$asset" | awk '{print $1}')"
    [[ -n "$expected" && "$actual" == "$expected" ]]
  done

  mkdir -p "$HOME/.local/bin" "$data_dir"
  tar -xzf "$scratch/ai-memory-macos-aarch64.tar.gz" -C "$scratch" ./ai-memory
  install -m 755 "$scratch/ai-memory" "$HOME/.local/bin/ai-memory"
  tar -xzf "$scratch/ai-memory-hooks.tar.gz" -C "$data_dir"
  "$HOME/.local/bin/ai-memory" --version
)
```

## Configurar os agentes

O módulo `development` inclui Cursor, OpenCode 2, Oh My Pi e Antigravity CLI.
O núcleo inclui Codex. A integração do Sublime Text usa o Codex CLI quando
configurada para chamar esse executável, sem um registro MCP separado.

Rode o bloco em Bash. Informe a URL base em HTTPS, sem `/mcp`, e cole o token
quando solicitado. O instalador pode gravar a autenticação nos arquivos
locais dos clientes. O `umask 077` protege arquivos novos. Mantenha também as
configurações e os backups gerados pelo instalador fora do Git.

```bash
(
  set -euo pipefail
  umask 077
  export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
  data_dir="$HOME/.local/share/ai-memory"
  read -r -p 'URL base HTTPS do ai-memory: ' server
  server="${server%/}"
  [[ "$server" == https://* && "$server" != */mcp ]]
  read -r -s -p 'Token do ai-memory: ' AI_MEMORY_AUTH_TOKEN
  printf '\n'
  [[ -n "$AI_MEMORY_AUTH_TOKEN" ]]
  export AI_MEMORY_AUTH_TOKEN
  log_dir="$(mktemp -d "$data_dir/setup.XXXXXXXX")"

  for agent in codex cursor opencode2 omp antigravity-cli; do
    if ai-memory install-mcp --client "$agent" --apply \
        --server-url "$server/mcp" --data-dir "$data_dir" \
        >"$log_dir/$agent-mcp.log" 2>&1 &&
      ai-memory install-hooks --agent "$agent" --apply \
        --server-url "$server" --data-dir "$data_dir" \
        --hooks-dir "$data_dir/hooks" --capture-mode allowlist \
        >"$log_dir/$agent-hooks.log" 2>&1; then
      printf '%s configurado\n' "$agent"
    else
      printf '%s precisa de revisão. Logs privados em %s\n' "$agent" "$log_dir" >&2
      exit 1
    fi
  done
)
```

Em um Mac com menos agentes, use apenas os nomes dos clientes instalados no
loop. Abra novas sessões depois de aplicar e aprove os hooks que o cliente
pedir. Com `allowlist`, projetos sem o marcador `.ai-memory.toml` ficam sem
captura automática. Adicione esse marcador somente a projetos autorizados a
enviar eventos ao servidor.

## Verificar a integração

1. Confira a versão com `ai-memory --version`. Execute `codex mcp list` e
   `agy mcp list` e confirme que `ai-memory` aparece habilitado.
2. Abra uma nova sessão do Cursor e confira o servidor em **Settings → Tools
   & MCP**. Abra uma nova sessão do Oh My Pi e verifique se as ferramentas
   `memory_*` estão disponíveis.
3. No OpenCode, execute `opencode debug config` e `opencode mcp list` em uma
   nova sessão. O instalador grava `mcp.servers.ai-memory` no arquivo global
   `~/.config/opencode/opencode.json`. Na verificação deste Mac, o OpenCode
   2.3.2 leu o arquivo, mas ainda exibiu `No MCP servers configured`. Considere
   o cliente pendente até que a lista mostre a conexão.
4. Em cada cliente, faça uma consulta de memória de leitura. Para testar
   também a captura automática, use um projeto de teste autorizado com
   `.ai-memory.toml`, abra e encerre uma sessão com texto sintético, e
   confirme a sessão pela interface do servidor. Para usar o
   `ai-memory doctor --data-dir "$HOME/.local/share/ai-memory"`, execute-o na
   raiz do projeto com `AI_MEMORY_SERVER_URL` e `AI_MEMORY_AUTH_TOKEN`
   disponíveis no ambiente desse processo.
   Repita em um projeto sem marcador e confirme a ausência de captura.

Neste Mac, a negociação MCP autenticada e a chamada `tools/list` retornaram
27 ferramentas. Codex e Antigravity listaram o registro. A carga dos hooks
no Cursor e no Oh My Pi ainda precisa ser confirmada em uma nova sessão.

Consulte o [guia de instalação do ai-memory 3.4.2](https://github.com/akitaonrails/ai-memory/blob/v3.4.2/docs/install.md)
e o [guia de configuração MCP](https://github.com/akitaonrails/ai-memory/blob/v3.4.2/docs/mcp-install.md).
