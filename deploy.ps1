# Script de Deploy para Vercel (PowerShell)

Write-Host "🚀 Preparando deploy para Vercel..." -ForegroundColor Green

# Verificar se estamos na branch main
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "⚠️  Você não está na branch main. Mudando para main..." -ForegroundColor Yellow
    git checkout main
}

# Atualizar repository
Write-Host "📦 Commitando alterações..." -ForegroundColor Blue
git add .
$commitResult = git commit -m "Deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nada para commitar" -ForegroundColor Yellow
}

Write-Host "⬆️  Pushing para GitHub..." -ForegroundColor Blue
git push origin main

Write-Host "✅ Código enviado para GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Acesse https://vercel.com"
Write-Host "2. Import project do GitHub"
Write-Host "3. Configure as environment variables:"
Write-Host "   - SECRET_KEY"
Write-Host "   - MONGODB_URI" 
Write-Host "   - STRAVA_CLIENT_ID"
Write-Host "   - STRAVA_CLIENT_SECRET"
Write-Host "   - STRAVA_REDIRECT_URI (https://seu-dominio.vercel.app/strava/callback)"
Write-Host ""
Write-Host "📖 Guia completo: DEPLOY_VERCEL.md" -ForegroundColor Magenta

# Abrir Vercel no browser
$openBrowser = Read-Host "Deseja abrir o Vercel no browser? (y/N)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "https://vercel.com"
}