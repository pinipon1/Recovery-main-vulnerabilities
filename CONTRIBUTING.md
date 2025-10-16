# Guia de Contribuição

Obrigado pelo interesse em contribuir para o Portal de Ciclismo! 🚴‍♂️

## 🚀 Como Contribuir

### 🐛 Reportar Bugs

1. **Verificar Issues Existentes**: Procure se o bug já foi reportado
2. **Criar Nova Issue**: Use o template de bug report
3. **Incluir Informações**:
   - Descrição clara do problema
   - Passos para reproduzir
   - Screenshots/logs se aplicável
   - Versão do browser/OS
   - URL onde ocorreu (se aplicável)

### ✨ Sugerir Funcionalidades

1. **Abrir Feature Request**: Use o template específico
2. **Descrever Caso de Uso**: Explique o problema que resolve
3. **Incluir Mockups**: Se possível, adicione wireframes/designs
4. **Considerar Impacto**: Como beneficia outros utilizadores

### 🔧 Contribuir com Código

#### **1. Setup do Ambiente**

```bash
# Fork do repositório
git clone https://github.com/SEU-USUARIO/Recovery.git
cd Recovery

# Criar branch para feature
git checkout -b feature/nome-da-funcionalidade

# Setup ambiente local
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais
```

#### **2. Desenvolvimento**

- **Código Python**: Seguir PEP 8
- **JavaScript**: Usar ESLint/Prettier se possível  
- **CSS**: Manter consistência com design existente
- **Commits**: Usar Conventional Commits

```bash
# Exemplos de commits
git commit -m "feat: adicionar análise de potência"
git commit -m "fix: corrigir bug no cálculo de VO2max"
git commit -m "docs: atualizar guia de instalação"
```

#### **3. Testes**

```bash
# Testar localmente
python app.py

# Verificar funcionalidades principais:
# - Login Strava
# - Importação de atividades
# - Cálculos de índices
# - Mapas e gráficos
# - Sistema de pólen
```

#### **4. Pull Request**

1. **Push da Branch**:
   ```bash
   git push origin feature/nome-da-funcionalidade
   ```

2. **Criar PR** com:
   - Título descritivo
   - Descrição detalhada das mudanças
   - Screenshots antes/depois (se UI)
   - Checklist de testes realizados

3. **Aguardar Review**:
   - Responder a comentários
   - Fazer ajustes solicitados
   - Manter branch atualizada

## 📋 Standards de Código

### **Python (Backend)**

```python
# ✅ Bom
def calcular_vo2max(idade: int, fc_max: int, fc_repouso: int) -> float:
    """
    Calcula VO2max estimado baseado na frequência cardíaca.
    
    Args:
        idade: Idade do atleta em anos
        fc_max: Frequência cardíaca máxima
        fc_repouso: Frequência cardíaca de repouso
        
    Returns:
        VO2max estimado em ml/kg/min
    """
    return (fc_max - fc_repouso) * 15.3 / idade

# ❌ Evitar
def calc(a,b,c):
    return (a-b)*15.3/c
```

### **JavaScript (Frontend)**

```javascript
// ✅ Bom
async function carregarAtividades() {
    try {
        const response = await fetch('/api/atividades');
        const data = await response.json();
        
        if (data.error) {
            mostrarErro(data.error);
            return;
        }
        
        renderizarAtividades(data.atividades);
    } catch (error) {
        console.error('Erro ao carregar atividades:', error);
        mostrarErro('Erro de conexão');
    }
}

// ❌ Evitar
function loadActs(){
    fetch('/api/atividades').then(r=>r.json()).then(d=>render(d))
}
```

### **CSS**

```css
/* ✅ Bom - Classes específicas */
.cycling-stats {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: #f5f5f5;
    border-radius: 8px;
}

/* ❌ Evitar - Classes genéricas */
.box {
    display: flex;
}
```

## 🎯 Áreas de Contribuição

### **🚴‍♂️ Alto Impacto**
- Melhorias no cálculo de VO2max
- Novas métricas de performance
- Otimizações de performance
- Correções de bugs críticos

### **🗺️ Médio Impacto**
- Melhorias na UI/UX
- Novas visualizações de dados
- Integrações com APIs
- Documentação

### **🌿 Baixo Impacto (Bom para Iniciantes)**
- Correções de typos
- Melhorias no README
- Adicionar comentários ao código
- Refatoração de código legacy

## 🏆 Reconhecimento

### **Contribuidores Ativos**
- Listados no README principal
- Badge de contribuidor
- Créditos em releases

### **Primeiras Contribuições**

Para primeira contribuição, considere issues com label `good first issue`:

- Correções de documentação
- Melhorias de acessibilidade
- Pequenas funcionalidades
- Testes unitários

## 📞 Suporte

### **Dúvidas sobre Código**
- Abrir issue com label `question`
- Descrever o que está tentando fazer
- Incluir código atual se relevante

### **Discussões**
- Use GitHub Discussions para:
  - Ideias de funcionalidades
  - Arquitetura/design decisions
  - Questões gerais sobre o projeto

### **Chat em Tempo Real**
- Discord: [Link do servidor] (se houver)
- Telegram: [Link do grupo] (se houver)

## ✅ Checklist do PR

Antes de submeter PR, verificar:

- [ ] Código segue os standards do projeto
- [ ] Funcionalidade testada localmente
- [ ] Documentação atualizada se necessário
- [ ] Commits seguem Conventional Commits
- [ ] Não quebra funcionalidades existentes
- [ ] Variáveis sensíveis não expostas
- [ ] Performance não degradada

## 🙏 Obrigado!

Cada contribuição, por menor que seja, faz a diferença para a comunidade ciclística. Juntos estamos construindo uma ferramenta que ajuda milhares de atletas a melhorar sua performance!

---

*Para dúvidas específicas sobre este guia, abra uma issue com label `contributing`.*