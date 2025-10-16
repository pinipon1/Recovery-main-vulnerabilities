# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Sistema completo de análise de pólen para ciclistas alérgicos
- Design monochrome com tons neutros elegantes
- Documentação completa para deploy no Vercel
- Sistema de fallback inteligente para APIs meteorológicas

## [2.0.0] - 2025-09-25

### Added
- 🌿 **Sistema Avançado para Alérgicos**
  - Detecção automática de níveis de pólen
  - Ajuste inteligente do índice de ciclismo (-5 a -35 pontos)
  - Dados sazonais simulados baseados na região
  - Toggle visual para ativar/desativar modo alérgico

- 🎨 **Design System Monochrome**
  - Migração completa para tons neutros (cinza, preto, branco)
  - Remoção de todos os gradientes verdes e azuis
  - Implementação da fonte Poppins em todo o sistema
  - Hover effects suavizados e consistentes

- 🌤️ **Sistema Meteorológico Multi-API**
  - Integração com WeatherAPI.com (1000 calls gratuitas/dia)
  - Backup com OpenWeatherMap API
  - Fallback automático para Open-Meteo (gratuita ilimitada)
  - Cálculo inteligente do índice de ciclismo baseado no tempo

### Changed
- 🔄 **Refatoração Completa do Frontend**
  - Interface redesenhada com layout responsivo otimizado
  - Migração de tabelas para cards informativos
  - Melhoria na experiência mobile
  - Otimização de performance no loading

- 📊 **Melhorias nos Gráficos e Mapas**
  - Gráficos responsivos que se adaptam ao container
  - Mapas com trajetos coloridos por velocidade
  - Correções no layout dos containers Leaflet
  - Smooth scrolling e indicadores visuais melhorados

### Fixed
- 🐛 **Correções Críticas**
  - Problema do mapa desaparecendo no detalhe da atividade
  - Hover effects que causavam movimento nas tabelas
  - Layout quebrado em dispositivos móveis
  - Problemas de CSS conflitante entre componentes

- 🔧 **Melhorias de Compatibilidade**
  - Configuração otimizada para deploy no Vercel
  - Variáveis de ambiente organizadas e documentadas
  - Sistema de logs melhorado para debugging
  - Tratamento robusto de erros de API

### Security
- 🔒 **Melhorias de Segurança**
  - Remoção completa de credenciais hardcoded
  - Variáveis sensíveis movidas para environment
  - Validação aprimorada de inputs do utilizador
  - Sanitização de logs para evitar vazamento de dados

## [1.5.0] - 2025-09-20

### Added
- Integração completa com Strava API
- Sistema de autenticação OAuth2 com Strava
- Análise automática de atividades importadas
- Cálculo de VO2max estimado
- Gráficos interativos de velocidade e frequência cardíaca

### Changed
- Migração de dados locais para MongoDB Atlas
- Interface redesenhada com melhor UX
- Performance otimizada para grandes volumes de dados

## [1.0.0] - 2025-09-15

### Added
- 🚴‍♂️ **Core Features**
  - Portal básico de análise de desempenho físico
  - Visualização de mapas com Leaflet.js
  - Gráficos básicos com Chart.js
  - Sistema de importação manual de dados
  
- 🗄️ **Base de Dados**
  - Configuração inicial MongoDB
  - Modelos de dados para atividades
  - Sistema básico de persistência

- 📱 **Interface**
  - Design responsivo básico
  - Layout de single-page application
  - Navegação por tabs
  - Cards informativos

### Technical
- Flask 2.3+ como backend framework
- HTML5/CSS3/Vanilla JS no frontend
- MongoDB para persistência
- Estrutura inicial de projeto

---

## Tipos de Mudanças

- `Added` para novas funcionalidades
- `Changed` para mudanças em funcionalidades existentes  
- `Deprecated` para funcionalidades que serão removidas
- `Removed` para funcionalidades removidas
- `Fixed` para correções de bugs
- `Security` para correções de vulnerabilidades

## Links de Comparação

- [Unreleased]: https://github.com/motadb/Recovery/compare/v2.0.0...HEAD
- [2.0.0]: https://github.com/motadb/Recovery/compare/v1.5.0...v2.0.0
- [1.5.0]: https://github.com/motadb/Recovery/compare/v1.0.0...v1.5.0
- [1.0.0]: https://github.com/motadb/Recovery/releases/tag/v1.0.0