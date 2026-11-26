# Fichas dos Quality Gates

Todos os gates executam no GitHub Actions a cada `push` e `pull_request` para `main`.
Consequência padrão: job vermelho → job "Decisão final" falha → execução **reprovada**.
Com *branch protection* em `main` exigindo o check "Decisão final - Quality Gate", o merge do PR é **bloqueado**.

## Gate 1 — Dependências e build
| Campo | Registro |
|---|---|
| Critério | `pip install` sem erro; `compileall` sem erro de sintaxe; `python -m build` gera wheel e sdist; *smoke test* `/health` retorna 200. |
| Justificativa | Risco de código que não instala, não empacota ou não inicializa (dependência inexistente, erro de sintaxe, import quebrado). |
| Momento | Primeiro job, em todo push/PR. Os demais gates dependem dele (`needs: build`). |
| Evidência | Log do job; artefato `pacote-distribuicao` (.whl e .tar.gz). |
| Consequência | Bloqueia — demais gates nem executam. |
| Limitação | Não verifica comportamento; só que a aplicação é instalável e sobe. Não testa outras versões de Python (poderia usar *matrix*). |

## Gate 2 — Análise estática (Ruff)
| Campo | Registro |
|---|---|
| Critério | Zero ocorrências nas regras `E, W, F, B, S, I, C90` e código formatado (`ruff format --check`). Complexidade ciclomática máxima 10. |
| Justificativa | `F`/`B` capturam defeitos reais (variável indefinida, import não usado, default mutável); `S` (regras do Bandit) captura padrões inseguros como `eval`, `assert` em produção, `debug=True`; `C90` limita funções complexas e difíceis de testar. Tolerância zero é viável porque o código é pequeno e nasceu limpo. |
| Momento | Job `lint`, após o build. |
| Evidência | Anotações inline no PR (`--output-format=github`); artefato `relatorio-analise-estatica` (ruff.json). |
| Consequência | Bloqueia. |
| Limitação | Não detecta erro de lógica de negócio. Exceções só via `# noqa: CÓDIGO` com justificativa no próprio código, revisada no PR (ex.: `S101` liberado em `tests/`). |

## Gate 3 — Testes automatizados
| Campo | Registro |
|---|---|
| Critério | 100% dos 48 testes obrigatórios (unitários + integração/API) aprovados; nenhum erro de coleta. |
| Justificativa | Risco de regressão nas regras do quadro (limite de WIP 3, movimento de uma coluna por vez, validação de título e prioridade), que mantêm o fluxo de trabalho sob controle. |
| Momento | Job `test`, após o build, em paralelo ao lint. |
| Evidência | Log do pytest; `junit.xml`; resumo no *Job Summary* listando testes que falharam; artefato `relatorio-testes-cobertura`. |
| Consequência | Bloqueia. |
| Limitação | Só detecta o que os casos cobrem. Testes instáveis (*flaky*) devem ser corrigidos, não marcados como `skip`; `skip` só com issue associada. |

## Gate 4 — Cobertura de código
| Campo | Registro |
|---|---|
| Critério | Cobertura de linhas **e ramos** (`branch = true`) do pacote `app/` ≥ **90%**. |
| Justificativa | `app/` contém apenas regras de negócio e a API — tudo é crítico. A cobertura atual é 100%; 90% dá folga para código defensivo trivial sem permitir que uma regra nova entre sem teste. Um limite de 100% geraria testes artificiais; um limite baixo (ex.: 70%) permitiria que um módulo inteiro novo entrasse sem teste. |
| Momento | Job `test`, passo seguinte aos testes. |
| Evidência | `coverage.xml`, relatório HTML (`htmlcov/`) e tabela no *Job Summary*. |
| Consequência | Bloqueia. |
| Limitação | Cobertura mede execução, não qualidade das asserções (um teste sem `assert` também cobre). Mitigado por revisão de PR; evolução possível: teste de mutação (mutmut). |

## Gate 5 — Dependências vulneráveis (pip-audit)
| Campo | Registro |
|---|---|
| Critério | Nenhuma vulnerabilidade conhecida (base OSV/PyPI Advisory) nas dependências de produção (`requirements.txt`, versões fixadas). |
| Justificativa | Risco de uso de componente vulnerável (OWASP Top 10 — A06 *Vulnerable and Outdated Components*). Como a API recebe entrada externa, uma falha no Flask/Werkzeug afetaria o sistema diretamente. |
| Momento | Job `security`, após o build, em todo push/PR. |
| Evidência | Log do pip-audit; artefato `relatorio-dependencias` (pip-audit.json). |
| Consequência | Bloqueia e exige revisão: atualizar a versão ou, se não houver correção, registrar exceção com `--ignore-vuln ID` e justificativa no PR. |
| Limitação | Só encontra vulnerabilidades já publicadas; não analisa código próprio (papel do Gate 2) nem dependências de desenvolvimento. Uma vulnerabilidade nova pode reprovar o pipeline sem alteração no código — o que é desejável. |
