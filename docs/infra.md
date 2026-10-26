# Preparar o acesso à infraestrutura

O `dotfiles` prepara o Mac. Inventários, destinos, usuários, fingerprints e procedimentos de VPS pertencem ao repositório privado `infra`; credenciais pertencem ao 1Password. O `infra` tem commits e publicação independentes, sem submódulo ou cópia dentro deste repositório.

## Aplicativos e autenticação

Os módulos opcionais `personal` e `cloud` incluem, respectivamente, 1Password/CLI e Tailscale. Confira [apps](apps.md) e o dry-run antes de instalar: esses módulos incluem outros aplicativos. Se precisar somente desses três aplicativos, selecione-os individualmente; não é necessário instalar todo o módulo.

A instalação não autentica os aplicativos. No Mac novo:

1. Entre na conta existente do 1Password e desbloqueie o app.
2. Em Settings → Developer, habilite **Integrate with 1Password CLI** e **Use the SSH agent**. Autorize Touch ID se desejar; preserve as solicitações de aprovação.
3. Entre no Tailscale com a conta autorizada. Não recrie a tailnet nem altere sua política para resolver falhas locais.
4. Confira `op --version` e `op whoami`. Se falhar, identifique a operação que precisa de autenticação antes de repetir login.

CLI, SSH Agent e plugins são integrações distintas: uma funcionar não comprova as demais.

## SSH permanece local

Este dotfiles não gerencia `~/.ssh/config`, chaves privadas, `known_hosts` ou configurações de autorização do app. Não restaure a configuração SSH do repositório legado por cima da atual: destinos e usuários antigos podem divergir do inventário vigente.

Para hosts que usam chaves do 1Password, o trecho oficial para macOS é:

```sshconfig
Host *
    IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
```

O [exemplo local](ssh-config.example) mostra a seleção por chave pública. Integre o trecho à configuração local após conferir os blocos existentes. Exceções específicas precisam preceder `Host *`, pois o OpenSSH usa o primeiro valor obtido. Não remova `IdentityAgent none` de hosts que usam Tailscale SSH. Usar o agente dispensa exportar as chaves privadas; uma chave pública pode ser usada para selecionar a identidade quando necessário.

Verifique apenas as identidades públicas oferecidas:

```sh
SSH_AUTH_SOCK="$HOME/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock" ssh-add -l
```

Isso comprova a resposta do agente, não autorização em um servidor. Conexão pela rede Tailscale e autenticação Tailscale SSH também são coisas distintas. Use o método e o usuário do inventário privado. Preserve `StrictHostKeyChecking=yes`; obtenha fingerprints por canal independente ou use a validação autenticada do Tailscale SSH. Não copie `known_hosts` nem aceite chaves automaticamente como substituto dessa validação.

## Repositório infra e GitHub

O [infra](https://github.com/prof-ramos/infra) é privado e exige acesso autorizado à conta GitHub. Clone-o separadamente e leia seu `AGENTS.md`:

```sh
git clone https://github.com/prof-ramos/infra.git ~/Developer/infra
```

O roteiro detalhado fica em `m3-gabrielramos/1password/README.md` dentro do `infra`. Ele descreve validações seguras e a seleção da credencial existente do GitHub. O arquivo local `.op/` não é versionado: no Mac novo, valide a credencial e configure o plugin no diretório apropriado. Não emita token novo nem amplie escopos apenas para reproduzir a configuração.

Após clonar o `infra`, execute seu gate offline:

```sh
cd ~/Developer/infra
git clone https://github.com/prof-ramos/observatorio.git observatorio
python3 scripts/check-all.py
```

O Observatório é clonado separadamente porque seus guias são referenciados pelo inventário; o gate confere esses links locais. O gate não autentica serviços. Complete o roteiro privado com testes reais de GitHub e dos hosts necessários; não publique a lista de máquinas ou dados dos cofres neste repositório.

## Fontes oficiais

- [Integração do CLI](https://www.1password.dev/cli/app-integration)
- [SSH Agent](https://www.1password.dev/ssh/get-started)
- [Plugin GitHub](https://www.1password.dev/cli/shell-plugins/github)
