# Apps opcionais

Nenhum módulo é instalado por padrão. Todos preservam os apps já existentes neste Mac.

## personal

- `cask "1password"`
- `cask "1password-cli"`
- `cask "brave-browser"`
- `cask "discord"`
- `cask "google-chrome"`
- `cask "localsend"`
- `cask "microsoft-excel"`
- `cask "microsoft-word"`
- `cask "obsidian"`
- `cask "openlogi"`
- `cask "raycast"`
- `cask "telegram"`
- `cask "todoist-app"`
- `cask "utm"`
- `cask "voiceink"`
- `cask "whatsapp"`
- `mas "Brother iPrint&Scan", id: 1193539993`
- `mas "Canva", id: 897446215`
- `mas "Dropover", id: 1355679052`
- `mas "Hidden Bar", id: 1452453066`
- `mas "Home Assistant", id: 1099568401`
- `mas "Magnet", id: 441258766`
- `mas "Paste", id: 967805235`
- `mas "TestFlight", id: 899247664`

## development

- `brew "node"`
- `brew "agent-browser"`
- `brew "ast-grep"`
- `brew "chrome-devtools-mcp"`
- `brew "docker"`
- `brew "fnm"`
- `brew "git-filter-repo"`
- `brew "gitleaks"`
- `brew "gnupg"`
- `brew "go"`
- `brew "hugo"`
- `brew "localsend-cli"`
- `brew "mas"`
- `brew "mole"`
- `brew "neovim"`
- `brew "pipx"`
- `brew "pnpm"`
- `brew "sqlite"`
- `brew "repomix"`
- `brew "ripgrep"`
- `brew "kenn-io/tap/roborev", trusted: true`
- `brew "f/mcptools/mcp", trusted: true`
- `brew "rustup"`
- `brew "shellcheck"`
- `brew "superfile"`
- `brew "tmux"`
- `brew "tree"`
- `brew "uv"`
- `brew "yarn"`
- `brew "anomalyco/tap/opencode-v2", trusted: true`
- `brew "can1357/tap/omp", trusted: true`
- `brew "steipete/tap/remindctl", trusted: true`
- `cask "antigravity-cli"`
- `cask "coderabbit"`
- `cask "cursor"`
- `cask "font-fira-code-nerd-font"`
- `cask "font-maple-mono-nf"`
- `cask "font-googlesanscode-nerd-font"`
- `npm "ctx7"`
- `npm "vercel"`
- `vscode "anysphere.remote-containers"`
- `vscode "anysphere.remote-ssh"`
- `vscode "ms-ceintl.vscode-language-pack-pt-br"`
- `vscode "tomoki1207.pdf"`
- `uv "browser-harness"`

## security

- `brew "amass"`
- `brew "binwalk"`
- `brew "dalfox"`
- `brew "feroxbuster"`
- `brew "ffuf"`
- `brew "gobuster"`
- `brew "hashcat"`
- `brew "hydra"`
- `brew "john"`
- `brew "masscan"`
- `brew "medusa"`
- `brew "ncrack"`
- `brew "nikto"`
- `brew "nmap"`
- `brew "nuclei"`
- `brew "radare2"`
- `brew "rustscan"`
- `brew "sqlmap"`
- `brew "sshpass"`
- `brew "subfinder"`
- `brew "u-boot-tools"`

## cloud

- `brew "googleworkspace-cli"`
- `brew "neonctl"`
- `brew "oci-cli"`
- `brew "opentofu"`
- `brew "rclone"`
- `brew "hashicorp/tap/terraform", trusted: true`
- `brew "supabase/tap/supabase", trusted: true`
- `brew "tursodatabase/tap/turso", trusted: true`
- `cask "cloudflare-warp"`
- `cask "gcloud-cli"`
- `cask "tailscale-app"`

## media

- `brew "a2ps"`
- `brew "webp"`
- `brew "exiftool"`
- `brew "ffmpeg"`
- `brew "librsvg"`
- `brew "p7zip"`
- `brew "telegram-downloader"`
- `brew "tesseract"`
- `brew "yt-dlp"`
- `npm "pake-cli"`

Telegram: somente cask. A etapa personal inclui mas e exige sessão App Store; falhas interrompem a etapa e permitem retomada.

## Sublime Text

No Mac novo, executar `Install Package Control` pela paleta do Sublime.
O manifesto User declara Package Control e Codex; pacotes são obtidos pelo
Package Control, sem vendor no Git. Autenticar Codex CLI manualmente.
Codex plugin 1.160.0 informa testes com CLI 0.160.1; Homebrew pode atualizar o CLI.
Conferir compatibilidade antes de declarar a integração funcional. A restauração
visual não envia mensagens nem altera permissões, modelo ou autenticação.
