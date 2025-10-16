# 🌸 Configuração da Google Pollen API

## Como obter e configurar a Google Pollen API

### 1. Obter a Chave da API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um projeto existente
3. Vá para **APIs & Services** > **Library**
4. Procure por "**Air Quality API**" (inclui dados de pólen)
5. Clique em **Enable** para ativar a API
6. **IMPORTANTE**: Aguarde alguns minutos para a ativação
6. Vá para **APIs & Services** > **Credentials**
7. Clique em **Create Credentials** > **API Key**
8. Copie a sua chave da API

### 2. Configurar no Projeto

1. Abra o arquivo `.env`
2. Substitua `YOUR_GOOGLE_POLLEN_API_KEY` pela sua chave real:

```properties
GOOGLE_POLLEN_API_KEY=SuaChaveAquiRealDaGoogle
```

### 3. Funcionalidades Incluídas

A integração da Google Pollen API adiciona:

#### **📊 Informações de Pólen por Dia**
- **🌳 Árvores** - Nível de pólen de árvores (0-5)
- **🌿 Ervas** - Nível de pólen de ervas (0-5)  
- **🌾 Plantas** - Nível de pólen de plantas/gramíneas (0-5)

#### **🎯 Níveis Visuais**
- 🟢 **Muito Baixo** (0-1) - Verde
- 🟡 **Baixo** (1-2) - Amarelo
- 🟠 **Moderado** (2-3) - Laranja
- 🔴 **Alto** (3-4) - Vermelho
- 🟣 **Muito Alto** (4-5) - Roxo

#### **📱 Interface Integrada**
- Nova coluna "**Pólen**" na tabela de previsão do tempo
- Ícones coloridos com níveis por tipo de pólen
- Legenda explicativa automática

### 4. Limitações da API

- **5 dias** de previsão de pólen (vs 7 dias de tempo)
- **1000 chamadas gratuitas** por mês
- Cobertura geográfica pode variar por região

### 5. Comportamento Sem Chave

Se a chave não estiver configurada:
- A previsão do tempo funciona normalmente
- A coluna de pólen não aparece
- Não há erros ou falhas no sistema
- `tem_polen: false` no JSON de resposta

### 6. Resolução de Problemas Comuns

#### ❌ **Erro "SERVICE_DISABLED"**
Se vir este erro nos logs:
```
Air Quality API has not been used in project ... or it is disabled
```

**Solução:**
1. Acesse: https://console.cloud.google.com/apis/api/airquality.googleapis.com
2. Clique em **"Enable"** (Ativar)
3. Aguarde 2-5 minutos para propagação
4. Reinicie o servidor Flask

#### ✅ **Teste da Configuração**

Execute este comando para testar:

```bash
curl "http://localhost:5000/api/previsao_tempo?regiao=Viseu,PT"
```

Se configurado corretamente, verá `"tem_polen": true` na resposta.

---

## 💡 Benefícios para Ciclistas

A informação de pólen é especialmente útil para:
- **Ciclistas alérgicos** - Planejar rotas em dias de baixo pólen
- **Saúde respiratória** - Evitar exercício intenso em picos de pólen
- **Conforto geral** - Melhor experiência durante os passeios

---

**Nota**: Esta funcionalidade é opcional. O sistema funciona perfeitamente sem a Google Pollen API configurada!