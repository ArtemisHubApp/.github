# .github

Repo especial da organização ArtemisHubApp (Grupo 11). Ele guarda os formulários de issue, o template de PR e o script que mantém as labels iguais em todos os repos.

## Como os templates chegam aos repos

Os arquivos em `.github/ISSUE_TEMPLATE/` e `.github/pull_request_template.md` valem para todo repo da org que **não** tenha os próprios. Por isso, não crie cópias nos repos (mesma regra das skills).

Para conferir num repo, o comando abaixo tem de dar 404:

```
gh api repos/ArtemisHubApp/<repo>/contents/.github/ISSUE_TEMPLATE
```

## Labels

- `semana-1` a `semana-7`
- `prioridade: alta`, `prioridade: média`, `prioridade: baixa`
- `tipo: feature`, `tipo: bug`, `tipo: chore`, `tipo: docs`

Para sincronizar (precisa de `gh auth login` com permissão de *maintain*; o script nunca apaga labels):

```
python3 scripts/labels.py            # ensaio, não muda nada
python3 scripts/labels.py --apply    # aplica nos repos
python3 scripts/labels.py --apply --repo artemishub_rag   # só um repo
```

O número de semanas é a constante `SEMANAS` em `scripts/labels.py`. Os formulários de issue seguem essa mesma constante, e os testes avisam se ficarem diferentes.

## CODEOWNERS

O CODEOWNERS não é herdado da org. Em `exemplos/CODEOWNERS` há um modelo todo comentado: copie para `.github/CODEOWNERS` do repo e preencha os logins.

## Desenvolvimento

```
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Regras gerais

Processo, branches, PRs e kanban estão no [AGENTS.md do orquestrador](https://github.com/ArtemisHubApp/artemishub_orchestration/blob/main/AGENTS.md).
