# Experimento obrigatório: aprovado → reprovado → corrigido

| Cenário | Commit | Alteração | Resultado esperado |
|---|---|---|---|
| 1. Aprovado | `funcionalidade: kanban, testes e pipeline de qualidade` | Versão que atende a todos os gates | Todos os jobs verdes; "Decisão final" = APROVADO |
| 2. Reprovado | `experimento: altera o limite de WIP de 3 para 4` | `LIMITE_WIP` alterado de 3 para 4 em `app/domain.py` (simula alguém "afrouxando" a regra do time) | Gate 3 (testes) vermelho; "Decisão final" = REPROVADO |
| 3. Corrigido | `correcao: restaura o limite de WIP para 3` | Volta para 3 | Todos os jobs verdes novamente; histórico das execuções preservado em *Actions* |

## Por que essa alteração?
É um defeito plausível, de uma linha, que **compila, passa no lint e mantém a cobertura acima de 90%**
(99%) — os gates 1, 2, 4 e 5 não o detectam. Só os testes de **valor-limite** do WIP (o 3º card entra,
o 4º é bloqueado) e os que dependem dessa regra o detectam. O gate de testes bloqueia a alteração na etapa correta.

## Resultado local (ver `evidencias-locais/`)
| Cenário | Testes | Cobertura | Decisão |
|---|---|---|---|
| Aprovado | 48/48 | 100% | APROVADO |
| Reprovado | 43/48 — falharam `test_aceita_ate_o_limite`, `test_bloqueia_o_quarto_card`, `test_resumo`, `test_limite_wip_via_api`, `test_mover_e_resumo` | 99% | REPROVADO (Gate 3) |
| Corrigido | 48/48 | 100% | APROVADO |

Amostra extra (`extra-reprovado-lint.txt`): um arquivo com `import os` não usado e `eval()` é barrado
pelo Gate 2 com as regras `F401` e `S307`.

## Demonstração ao vivo com Pull Request
1. (Já configurado) *Settings → Branches*: `main` exige o check `Decisao final - Quality Gate`.
2. No GitHub, edite `app/domain.py`, troque `LIMITE_WIP = 3` por `LIMITE_WIP = 4` e faça commit numa nova branch `demo/falha`, abrindo um PR.
3. Pipeline vermelho → merge bloqueado.
4. Volte para 3 na mesma branch → pipeline verde → merge liberado.
