# 🚴‍♂️ Portal de Ciclismo com Análise Inteligente

> **Sistema completo de análise de performance ciclística com integração Strava, previsão meteorológica e sistema avançado para ciclistas alérgicos ao pólen.**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/motadb/Recovery)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Índice

- [🎯 Funcionalidades](#-funcionalidades)
- [🚀 Demo & Deploy Rápido](#-demo--deploy-rápido)
- [🛠️ Tecnologias](#️-tecnologias)
- [⚡ Instalação Local](#-instalação-local)
- [🌐 Deploy em Produção](#-deploy-em-produção)
- [📊 APIs Integradas](#-apis-integradas)
- [🔒 Segurança](#-segurança)
- [🤝 Contribuir](#-contribuir)
- [📄 Licença](#-licença)

---

## 🎯 Funcionalidades

### 🚴‍♂️ **Análise de Performance**
- ✅ **Integração completa com Strava API**
- ✅ **Cálculo automático de VO2max estimado**
- ✅ **Análise de zonas de frequência cardíaca**
- ✅ **Estatísticas detalhadas por atividade**
- ✅ **Gráficos interativos de velocidade e FC**

### 🗺️ **Visualização Geográfica**
- ✅ **Mapas interativos com trajetos coloridos por velocidade**
- ✅ **Heatmap de atividades por região**
- ✅ **Análise de elevação e desnível**
- ✅ **Marcadores de pontos de interesse**

### 🌤️ **Sistema Meteorológico Inteligente**
- ✅ **Previsão meteorológica em tempo real**
- ✅ **Cálculo de índice de ciclismo baseado no tempo**
- ✅ **Integração com múltiplas APIs (WeatherAPI, OpenWeatherMap, Open-Meteo)**
- ✅ **Sistema de fallback automático para APIs gratuitas**

### 🌿 **Sistema Avançado para Alérgicos**
- ✅ **Detecção automática de níveis de pólen**
- ✅ **Ajuste do índice de ciclismo para utilizadores alérgicos**
- ✅ **Redução inteligente do score (até -35 pontos baseado no nível de pólen)**
- ✅ **Dados sazonais simulados com precisão**

### 🎨 **Interface Moderna**
- ✅ **Design responsivo para desktop e mobile**
- ✅ **Tema monochrome elegante (tons neutros)**
- ✅ **Fonte Poppins para melhor legibilidade**
- ✅ **Animações suaves e hover effects**
- ✅ **Interface intuitiva de uma só página**

---

## 🚀 Demo & Deploy Rápido

### 1. Preparar o Repositório GitHub

```bash
# Clonar/fazer fork do repositório
git clone <seu-repo>
cd Recovery

# Verificar que todos os arquivos estão presentes
# - app.py (aplicação Flask)
# - index.html (frontend)
# - requirements.txt (dependências Python)
# - vercel.json (configuração Vercel)
```

### 2. Configurar Variáveis de Ambiente no Vercel

No dashboard do Vercel, configure estas variáveis de ambiente:

```env
SECRET_KEY=sua-chave-secreta-super-forte-aqui
MONGODB_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/?retryWrites=true&w=majority
STRAVA_CLIENT_ID=seu-client-id-strava
STRAVA_CLIENT_SECRET=seu-client-secret-strava
STRAVA_REDIRECT_URI=https://sua-app.vercel.app/strava/callback
```

### 3. Configurar App Strava

1. Vá para [Strava API Settings](https://www.strava.com/settings/api)
2. Atualize o **Authorization Callback Domain** para: `sua-app.vercel.app`
3. Anote o **Client ID** e **Client Secret**

### 4. Deploy

O Vercel irá automaticamente:
- Detectar que é uma aplicação Python Flask
- Instalar dependências do `requirements.txt`
- Usar a configuração do `vercel.json`
- Fazer deploy da aplicação

## 🏗️ Arquitetura

- **Backend**: Flask (Python) com integração Strava OAuth2
- **Frontend**: HTML/CSS/JavaScript puro com Chart.js e Leaflet.js
- **Database**: MongoDB Atlas para armazenamento de atividades
- **APIs**: Strava API v3 para dados de atividades

## 📊 Funcionalidades

- ✅ Login OAuth2 com Strava
- ✅ Importação automática de atividades
- ✅ Análise de performance (VO₂max, velocidade, FC)
- ✅ Mapas coloridos por velocidade
- ✅ Gráficos interativos
- ✅ Resumo estatístico completo
- ✅ Interface responsiva

## 🔧 Desenvolvimento Local

```bash
# Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# Executar aplicação
python app.py
```

## 📁 Estrutura do Projeto

```
Recovery/
├── app.py              # Aplicação Flask principal
├── index.html          # Frontend
├── requirements.txt    # Dependências Python
├── vercel.json        # Configuração Vercel
├── .env               # Variáveis ambiente (local)
├── .gitignore         # Arquivos ignorados
└── README.md          # Esta documentação
```

## 🌐 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta Flask | `sua-chave-super-secreta` |
| `MONGODB_URI` | String conexão MongoDB | `mongodb+srv://...` |
| `STRAVA_CLIENT_ID` | ID da aplicação Strava | `123456` |
| `STRAVA_CLIENT_SECRET` | Secret da aplicação Strava | `abc123...` |
| `STRAVA_REDIRECT_URI` | URL de callback | `https://app.vercel.app/strava/callback` |

## 🔐 Segurança

- ✅ Credenciais via variáveis de ambiente
- ✅ OAuth2 flow seguro
- ✅ Tokens armazenados em sessão
- ✅ `.env` não commitado
- ✅ Validação de dados de entrada

## 📈 Performance

- Filtragem de velocidades irreais (>80km/h ciclismo, >25km/h corrida)
- Suavização de dados (média móvel de 3 pontos)
- Cache de atividades no MongoDB
- Carregamento assíncrono de dados

---

**Desenvolvido com ❤️ para atletas e entusiastas do fitness**
