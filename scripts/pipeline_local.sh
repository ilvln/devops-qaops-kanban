#!/usr/bin/env bash
# Reproduz localmente os mesmos gates do GitHub Actions (Linux/macOS/Git Bash).
set -euo pipefail
mkdir -p reports
echo "== Gate 1: dependencias e build ==";  pip install -q -r requirements-dev.txt; python -m compileall -q app; python -m build -q
echo "== Gate 2: analise estatica ==";      ruff check . && ruff format --check .
echo "== Gate 3: testes ==";                 pytest -q --junitxml=reports/junit.xml --cov=app --cov-report=xml:reports/coverage.xml --cov-report=html:reports/htmlcov --cov-fail-under=0
echo "== Gate 4: cobertura >= 90% ==";       python -m coverage report --fail-under=90
echo "== Gate 5: dependencias ==";           pip-audit -r requirements.txt
echo "QUALITY GATE: APROVADO"
