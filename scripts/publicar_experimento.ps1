# Envia os commits do experimento um a um para o GitHub, gerando uma execucao do pipeline por commit.
param(
    [Parameter(Mandatory = $true)][string]$Remote,
    [int]$EsperaSegundos = 20
)
$ErrorActionPreference = "Stop"
if (-not (git remote | Select-String -Quiet "^origin$")) { git remote add origin $Remote }
$commits = git rev-list --reverse HEAD
foreach ($c in $commits) {
    $msg = git log -1 --format=%s $c
    Write-Host "Enviando $($c.Substring(0,7)) - $msg" -ForegroundColor Cyan
    git push --force-with-lease origin "${c}:refs/heads/main"
    if ($LASTEXITCODE -ne 0) { throw "falha no push" }
    Start-Sleep -Seconds $EsperaSegundos
}
git branch -M main
git push -u origin main
Write-Host "Pronto. Veja as execucoes em: $($Remote -replace '\.git$','')/actions" -ForegroundColor Green
