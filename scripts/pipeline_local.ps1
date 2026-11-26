# Reproduz localmente os mesmos gates do GitHub Actions (Windows PowerShell).
$ErrorActionPreference = "Stop"
function Invoke-Gate($nome, [scriptblock]$cmd) {
    Write-Host "== $nome ==" -ForegroundColor Cyan
    & $cmd
    if ($LASTEXITCODE -ne 0) { Write-Host "QUALITY GATE: REPROVADO em '$nome'" -ForegroundColor Red; exit 1 }
}
New-Item -ItemType Directory -Force reports | Out-Null
Invoke-Gate "Gate 1: dependencias e build" { python -m pip install -q -r requirements-dev.txt; python -m compileall -q app; python -m build -q }
Invoke-Gate "Gate 2: analise estatica"     { python -m ruff check .; if ($LASTEXITCODE -eq 0) { python -m ruff format --check . } }
Invoke-Gate "Gate 3: testes"               { python -m pytest -q --junitxml=reports/junit.xml --cov=app --cov-report=xml:reports/coverage.xml --cov-report=html:reports/htmlcov --cov-fail-under=0 }
Invoke-Gate "Gate 4: cobertura >= 90%"     { python -m coverage report --fail-under=90 }
Invoke-Gate "Gate 5: dependencias"         { python -m pip_audit -r requirements.txt }
Write-Host "QUALITY GATE: APROVADO" -ForegroundColor Green
