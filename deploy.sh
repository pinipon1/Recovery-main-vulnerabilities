#!/bin/bash
# Script de Deploy para Vercel

echo "🚀 Preparando deploy para Vercel..."

# Verificar se estamos na branch main
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  Você não está na branch main. Mudando para main..."
    git checkout main
fi

# Atualizar repository
echo "📦 Commitando alterações..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "Nada para commitar"

echo "⬆️  Pushing para GitHub..."
git push origin main

echo "✅ Código enviado para GitHub!"
echo ""
echo "🌐 Próximos passos:"
echo "1. Acesse https://vercel.com"
echo "2. Import project do GitHub"
echo "3. Configure as environment variables:"
echo "   - SECRET_KEY"
echo "   - MONGODB_URI" 
echo "   - STRAVA_CLIENT_ID"
echo "   - STRAVA_CLIENT_SECRET"
echo "   - STRAVA_REDIRECT_URI (https://seu-dominio.vercel.app/strava/callback)"
echo ""
echo "📖 Guia completo: DEPLOY_VERCEL.md"