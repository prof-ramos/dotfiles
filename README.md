# Dotfiles de prof-ramos

Setup pessoal para macOS Apple Silicon, inspirado na organização do Mathias Bynens,
com Zsh, Stow e etapas independentes. Credenciais e estado de aplicativos ficam locais.

```sh
./bootstrap.sh --stage all --dry-run
./bootstrap.sh --stage apps
./bootstrap.sh --stage shell
./bootstrap.sh --stage macos
./bootstrap.sh --stage visual
```

Instale Command Line Tools quando solicitado e execute novamente após concluir.
O bootstrap instala Homebrew pela fonte oficial quando ausente. Não use `source`.
Apps de outros módulos só entram com `--module personal|development|security|cloud|media`.
Sublime Text é EDITOR/VISUAL com espera (`subl -w`). Git usa identidade local em
~/.gitconfig.local. Autenticações são manuais; senhas e chaves privadas não entram no Git.
Validação: `python3 -m unittest discover -s tests -v`.
