# Deploy no Vercel - Portal de Ciclismo

## 🚀 Passos para Deploy

### 1. Preparar o Repositório
```bash
# Certificar que todos os arquivos estão commitados
git add .
git commit -m "Preparar para deploy no Vercel"
git push origin main
```

### 2. Deploy no Vercel

1. **Acesse**: https://vercel.com
2. **Login** com sua conta GitHub
3. **Import Project**: Selecione o repositório `Recovery`
4. **Framework Preset**: Vercel detectará automaticamente como "Other"
5. **Root Directory**: Deixe vazio (/)
6. **Build Settings**: Vercel usará automaticamente o `vercel.json`

### 3. Configurar Variáveis de Ambiente

No dashboard do Vercel, vá para **Settings > Environment Variables** e adicione:

#### ⚡ Obrigatórias
```bash
SECRET_KEY = sua-chave-secreta-forte-aqui
MONGODB_URI = mongodb+srv://usuario:senha@cluster.mongodb.net/?retryWrites=true&w=majority
STRAVA_CLIENT_ID = seu-client-id-strava
STRAVA_CLIENT_SECRET = seu-client-secret-strava
```

#### 🔧 Configurar URLs de Produção
```bash
STRAVA_REDIRECT_URI = https://seu-dominio.vercel.app/strava/callback
```

#### 🌤️ Opcionais (APIs de Tempo)
```bash
WEATHER_API_KEY = sua-chave-weather-api (1000 chamadas grátis/dia)
OPENWEATHER_API_KEY = sua-chave-openweather (opcional)
```

### 4. Atualizar Strava App Settings

1. Acesse: https://www.strava.com/settings/api
2. **Authorization Callback Domain**: `seu-dominio.vercel.app`
3. **Website**: `https://seu-dominio.vercel.app`

### 5. Funcionalidades Implementadas

#### 🚴‍♂️ Core Features
- ✅ Análise completa de atividades Strava
- ✅ Cálculo de índice de ciclismo baseado em tempo
- ✅ Mapas interativos com trajetos coloridos por velocidade
- ✅ Gráficos de velocidade e frequência cardíaca
- ✅ Estatísticas detalhadas (VO2max, zonas de FC, etc.)

#### 🌿 Recursos Avançados
- ✅ **Sistema de Pólen**: Integração para utilizadores alérgicos
- ✅ **Previsão Meteorológica**: Múltiplas APIs (WeatherAPI, OpenWeatherMap, Open-Meteo)
- ✅ **Heatmap de Atividades**: Visualização geográfica
- ✅ **Design Monochrome**: Interface moderna em tons neutros
- ✅ **Responsivo**: Otimizado para mobile e desktop

#### 📊 APIs Integradas
- **Strava API**: Atividades e estatísticas
- **WeatherAPI.com**: Previsão detalhada (1000 calls grátis/dia)
- **OpenWeatherMap**: Backup meteorológico
- **Open-Meteo**: Fallback gratuito ilimitado
- **MongoDB Atlas**: Base de dados na cloud

### 6. Após o Deploy

1. **Teste a aplicação**: `https://seu-dominio.vercel.app`
2. **Conecte com Strava**: Login e autorização
3. **Verifique funcionalidades**:
   - Importação de atividades
   - Cálculo de índices
   - Mapas e gráficos
   - Sistema de pólen

### 7. Monitorização

- **Logs**: Dashboard Vercel > Functions > View Logs
- **Performance**: Vercel Analytics (opcional)
- **Erros**: Verificar console do browser

### 8. Domínio Personalizado (Opcional)

1. **Vercel Dashboard** > Project > Settings > Domains
2. **Add Domain**: `seu-dominio.com`
3. **Configure DNS**: Apontar para Vercel

---

## 🔧 Estrutura do Projeto

```
Recovery/
├── app.py              # Aplicação Flask principal
├── index.html          # Frontend single-page
├── requirements.txt    # Dependências Python
├── vercel.json        # Configuração Vercel
├── .env.example       # Template variáveis ambiente
└── DEPLOY_VERCEL.md   # Este guia
```

## 🚨 Troubleshooting

### Erro de Build
- Verificar `requirements.txt` está correto
- Confirmar `vercel.json` configurado
- Logs em Vercel Dashboard > Functions

### Erro de Conexão MongoDB
- Verificar `MONGODB_URI` nas env vars
- IP whitelist no MongoDB Atlas (0.0.0.0/0 para Vercel)

### Erro Strava Authorization
- Confirmar callback URL atualizado na Strava API
- Verificar Client ID/Secret corretos

---

## 📈 Performance

- **Cold Start**: ~2-3s (primeira chamada)
- **Warm Requests**: ~200-500ms
- **Free Tier**: 100GB bandwidth, 10GB storage
- **Escalabilidade**: Automática via Vercel

**🎉 Aplicação pronta para produção!**