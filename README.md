# Kanban — Pipeline DevOps/QAOps

[![Pipeline de Qualidade](https://github.com/ilvln/devops-qaops-kanban/actions/workflows/ci.yml/badge.svg)](https://github.com/ilvln/devops-qaops-kanban/actions/workflows/ci.yml)

Projeto prático de DevOps/QAOps: um pipeline de qualidade no GitHub Actions com 5 *quality gates*
(build, análise estática, testes, cobertura e auditoria de dependências), aplicado a um **Kanban básico**
feito em Python/Flask (API + página web).

## O Kanban
| Regra | Valor |
|---|---|
| Colunas | `A_FAZER` → `FAZENDO` → `FEITO` |
| Novo card | nasce em `A_FAZER`, prioridade padrão `MEDIA` |
| Título | obrigatório, 1 a 100 caracteres |
| Prioridade | `BAIXA`, `MEDIA` ou `ALTA` (ALTA aparece primeiro) |
| Movimento | uma coluna por vez, para frente ou para trás |
| Limite de WIP | no máximo **3** cards em `FAZENDO` |

## Estrutura
```
app/domain.py            regras do quadro (classe Quadro)
app/api.py               API Flask + página web
app/static/index.html    página do quadro (HTML + JavaScript)
tests/unit/              testes unitários (positivos, negativos, valores-limite)
tests/integration/       testes de integração/API (requisições HTTP via test client)
.github/workflows/ci.yml pipeline com os quality gates
scripts/pipeline_local.* execução local dos mesmos gates
docs/                    fichas dos quality gates, experimento e evidências
```

## Instalação e execução local
Requisitos: Python 3.11+ e Git.
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    | Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.api                    # abra http://127.0.0.1:5000
```

| Método | Rota | O que faz | Erros |
|---|---|---|---|
| GET | `/` | página do quadro | — |
| GET | `/health` | status da aplicação | — |
| GET | `/api/cards?coluna=` | lista cards (filtro opcional) | 422 |
| POST | `/api/cards` | cria card `{"titulo","prioridade"}` | 400, 422 |
| POST | `/api/cards/<id>/mover` | move card `{"coluna"}` | 404, 409, 422 |
| DELETE | `/api/cards/<id>` | remove card | 404 |
| GET | `/api/resumo` | contagem por coluna e vagas de WIP | — |

Os dados ficam em memória (reiniciar a aplicação limpa o quadro).

## Testes e gates localmente
```bash
pytest --cov=app                       # testes + cobertura
ruff check . && ruff format --check .  # análise estática
pip-audit -r requirements.txt          # vulnerabilidades em dependências
./scripts/pipeline_local.sh            # todos os gates (Linux/macOS/Git Bash)
powershell -File scripts/pipeline_local.ps1   # todos os gates (Windows)
```

## Pipeline (GitHub Actions)
Acionado em `push` (qualquer branch), `pull_request` para `main` e manualmente (`workflow_dispatch`).

```
push/PR ──► Gate 1: Build ──┬──► Gate 2: Análise estática (Ruff) ──┐
                            ├──► Gates 3+4: Testes + Cobertura ≥90% ├──► Decisão final
                            └──► Gate 5: pip-audit (dependências) ──┘    (APROVADO/REPROVADO)
```
Artefatos publicados em cada execução: `pacote-distribuicao`, `relatorio-analise-estatica`,
`relatorio-testes-cobertura` (JUnit XML, coverage XML/HTML) e `relatorio-dependencias`.
A branch `main` é protegida e exige o check **Decisao final - Quality Gate**.
Detalhes de cada gate: [docs/quality-gates.md](docs/quality-gates.md).
Experimento aprovado/reprovado/corrigido: [docs/experimento.md](docs/experimento.md).

## Segurança
Nenhum segredo, senha, token ou dado pessoal é versionado. O pipeline não precisa de segredos;
se um dia precisar (ex.: deploy), eles devem ser cadastrados em *Settings → Secrets and variables → Actions*
e lidos via `${{ secrets.NOME }}`. O workflow usa `permissions: contents: read` (privilégio mínimo).
