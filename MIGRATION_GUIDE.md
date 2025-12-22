# Guia de Migração - Streamlit → FastAPI + React

## 📊 Visão Geral da Migração

Este guia documenta a migração completa do dashboard monolítico Streamlit para uma arquitetura desacoplada Backend (Python/FastAPI) + Frontend (React/TypeScript).

## ✅ O Que Foi Preservado 100%

### Regras de Negócio SUS
- ✅ Prioridade PA_MVM sobre PA_CMP (fallback automático)
- ✅ Filtro Natureza Jurídica 1031 (Municipal)
- ✅ Classificação por categoria via filtro_CATEGORIA.csv
- ✅ Fallback por palavras-chave quando mapeamento ausente

### Processamento de Dados
- ✅ Detecção automática de separador CSV
- ✅ Remoção de BOM e caracteres inválidos
- ✅ Normalização de textos (NFKD)
- ✅ Limpeza de valores monetários brasileiros
- ✅ Preenchimento de CNES com 7 dígitos
- ✅ Otimização de dtypes (float32, int32)
- ✅ INNER JOIN Produção × Espelho

### Cálculos e Métricas
- ✅ Teto base mensal × número de meses = Teto acumulado
- ✅ Valor Aprovado, Valor Apresentado, Quantidades
- ✅ Saldo = Teto Acumulado - Produção
- ✅ % Execução = (Produção / Teto) × 100
- ✅ Cores dinâmicas por faixa de execução

### Visualizações
- ✅ KPIs: Orçado, Apresentado, Aprovado
- ✅ Gráfico de barras: Top 10 unidades (Teto × Aprovado)
- ✅ Gráfico donut: Distribuição por categoria
- ✅ Gráfico de linha: Tendência mensal
- ✅ Tabela detalhada interativa

### Exportação
- ✅ Download CSV: separador `;`, decimal `,`, encoding `latin1`

## 🔄 Mapeamento de Componentes

### Streamlit → FastAPI (Backend)

| Streamlit Original | FastAPI Equivalente | Localização |
|-------------------|---------------------|-------------|
| `DataLoader.load_data_raw()` | `ler_csv_papa()` + `ler_csv_espelho()` | `services/leitura_csv.py` |
| `processar_consolidado()` | `consolidar_producao_teto()` | `services/agregacoes.py` |
| `processar_tendencia_mensal()` | `calcular_tendencia_mensal()` | `services/calculos_kpi.py` |
| `calcular_metricas_globais()` | `calcular_kpis_globais()` | `services/calculos_kpi.py` |
| `classificar_unidade()` | `classificar_unidade()` | `services/limpeza_dados.py` |
| `normalizar_texto()` | `normalizar_texto()` | `utils/helpers.py` |
| `formatar_brl()` | `formatar_brl()` | `utils/helpers.py` |

### Streamlit → React (Frontend)

| Streamlit Component | React Component | Localização |
|--------------------|-----------------|-------------|
| `st.metric()` (KPIs) | `<KPICard />` | `components/KPICard.tsx` |
| `st.multiselect()` (Filtros) | `<Filters />` | `components/Filters.tsx` |
| `go.Bar()` (Plotly) | `<BarChart />` | `components/BarChart.tsx` |
| `go.Pie()` (Plotly) | `<DonutChart />` | `components/DonutChart.tsx` |
| `px.line()` (Plotly) | `<LineChart />` | `components/LineChart.tsx` |
| `st.dataframe()` | `<DataTable />` | `components/DataTable.tsx` |
| `st.file_uploader()` | `<FileUpload />` | `components/FileUpload.tsx` |

## 📁 Estrutura de Arquivos

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py                      # Aplicação FastAPI principal
│   ├── routers/
│   │   ├── upload.py               # POST /upload/papa, /upload/espelho
│   │   ├── filtros.py              # GET /filtros/*
│   │   ├── kpis.py                 # GET /kpis
│   │   ├── visao_geral.py          # GET /visao-geral/*
│   │   ├── tendencia.py            # GET /tendencia-mensal
│   │   └── tabela.py               # GET /tabela-detalhada
│   ├── services/
│   │   ├── leitura_csv.py          # Leitura de arquivos CSV
│   │   ├── limpeza_dados.py        # Normalização e classificação
│   │   ├── regras_sus.py           # Regras de negócio SUS
│   │   ├── calculos_kpi.py         # Cálculo de KPIs
│   │   └── agregacoes.py           # Consolidação de dados
│   ├── models/
│   │   └── schemas.py              # Schemas Pydantic
│   └── utils/
│       ├── helpers.py              # Funções auxiliares
│       └── state.py                # Gerenciador de estado
└── requirements.txt
```

### Frontend (React/TypeScript)

```
frontend/
├── src/
│   ├── components/
│   │   ├── KPICard.tsx             # Cards de indicadores
│   │   ├── Filters.tsx             # Filtros em cascata
│   │   ├── BarChart.tsx            # Gráfico de barras (ECharts)
│   │   ├── DonutChart.tsx          # Gráfico donut (ECharts)
│   │   ├── LineChart.tsx           # Gráfico de linha (ECharts)
│   │   ├── DataTable.tsx           # Tabela detalhada
│   │   └── FileUpload.tsx          # Upload de arquivos
│   ├── pages/
│   │   └── Dashboard.tsx           # Página principal
│   ├── services/
│   │   └── api.ts                  # Cliente API (Axios)
│   ├── types/
│   │   └── index.ts                # Tipos TypeScript
│   ├── utils/
│   │   └── formatters.ts           # Funções de formatação
│   ├── main.tsx                    # Entrada da aplicação
│   └── index.css                   # Estilos globais
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## 🔌 Endpoints da API

### Upload
```http
POST /upload/papa
Content-Type: multipart/form-data
Body: files (múltiplos arquivos CSV)
```

```http
POST /upload/espelho
Content-Type: multipart/form-data
Body: file (único arquivo CSV)
```

### Filtros
```http
GET /filtros/competencias
Response: { competencias: [{ codigo, nome, ordem }] }
```

```http
GET /filtros/categorias
Response: { categorias: ["🚨 UPA", "🏥 HOSPITAL", ...] }
```

```http
GET /filtros/unidades?categorias=🚨%20UPA
Response: { unidades: [{ nome, cnes }] }
```

### KPIs
```http
GET /kpis?competencias=2501&competencias=2502
Response: {
  teto_total_valor: 1000000,
  producao_aprovada_valor: 800000,
  percentual_execucao: 80.0,
  ...
}
```

### Visualizações
```http
GET /visao-geral/unidades?competencias=2501&top=10
Response: [{ unidade, cnes, valor_teto, valor_aprovado, ... }]
```

```http
GET /visao-geral/categorias?competencias=2501
Response: [{ categoria, valor_producao, percentual_execucao }]
```

```http
GET /tendencia-mensal?competencias=2501&competencias=2502
Response: [{ mes, valor_aprovado, valor_apresentado, valor_teto }]
```

### Tabela
```http
GET /tabela-detalhada?competencias=2501
Response: [{ unidade, cnes, categoria, valores... }]
```

```http
GET /tabela-detalhada/download/csv?competencias=2501
Response: CSV file (latin1, sep=;, decimal=,)
```

## 🎨 Design System

### Cores
- **Primary:** `#3498db` (Azul)
- **Secondary:** `#2c3e50` (Escuro)
- **Success:** `#2ecc71` (Verde) - Execução >= 80%
- **Warning:** `#f39c12` (Laranja) - Execução 50-79%
- **Danger:** `#e74c3c` (Vermelho) - Execução < 50%
- **Info:** `#00bcd4` (Ciano)

### Tipografia
- **Fonte:** Inter (Google Fonts)
- **Títulos:** 700 (Bold)
- **Corpo:** 400 (Regular)
- **Números:** 600 (Semi-Bold)

## 🔄 Fluxo de Dados

### 1. Upload
```
Frontend → POST /upload/papa → Backend
                ↓
        ler_csv_papa() → processar_papa()
                ↓
        app_state.set_dados_papa()

Frontend → POST /upload/espelho → Backend
                ↓
        ler_csv_espelho() → processar_espelho()
                ↓
        app_state.set_dados_teto()
                ↓
        consolidar_producao_teto()
```

### 2. Filtros
```
Frontend → GET /filtros/todos → Backend
                ↓
        app_state.get_competencias()
        app_state.get_categorias()
        app_state.get_unidades()
                ↓
        Frontend (atualiza selects)
```

### 3. Atualização de Dados
```
User seleciona filtros → Frontend
        ↓
GET /kpis?competencias=...&categorias=...
        ↓
Backend: filtrar_papa_por_competencias()
        consolidar_producao_teto()
        filtrar_consolidado()
        calcular_kpis_globais()
        ↓
Frontend: atualiza KPICard
```

## ⚡ Performance

### Backend
- ✅ Tipos otimizados: float32, int32
- ✅ INNER JOIN ao invés de LEFT JOIN
- ✅ Cálculos em Pandas (vetorização)
- ✅ Cache em memória (app_state)

### Frontend
- ✅ React.memo para componentes pesados
- ✅ useEffect com dependências corretas
- ✅ Lazy loading de gráficos
- ✅ Debounce em filtros (implementar se necessário)

## 🚀 Melhorias Futuras

### Backend
- [ ] Substituir app_state por Redis
- [ ] Adicionar autenticação JWT
- [ ] Rate limiting
- [ ] Logging estruturado
- [ ] Testes unitários (pytest)
- [ ] Docker/Kubernetes

### Frontend
- [ ] Context API para estado global
- [ ] React Query para cache
- [ ] Skeleton loaders
- [ ] Paginação na tabela
- [ ] Filtros avançados
- [ ] Gráficos drill-down
- [ ] PWA support

### Geral
- [ ] CI/CD pipeline
- [ ] Monitoramento (Sentry, New Relic)
- [ ] Backup automático
- [ ] Documentação OpenAPI enriquecida

## 📝 Checklist de Migração

### Preparação
- [x] Análise do código Streamlit
- [x] Documentação das regras de negócio
- [x] Definição da arquitetura

### Backend
- [x] Estrutura de pastas
- [x] Configuração FastAPI
- [x] Routers e endpoints
- [x] Services (lógica de negócio)
- [x] Models (schemas)
- [x] Utils (helpers)
- [x] Gerenciador de estado

### Frontend
- [x] Setup Vite + React + TypeScript
- [x] Configuração Tailwind CSS
- [x] Estrutura de componentes
- [x] Serviço de API
- [x] Tipos TypeScript
- [x] Componentes UI
- [x] Integração com backend

### Documentação
- [x] README principal
- [x] Guia de instalação
- [x] Guia de migração
- [x] Documentação de endpoints

### Testes
- [ ] Testar upload de arquivos
- [ ] Testar filtros em cascata
- [ ] Testar cálculos de KPIs
- [ ] Testar gráficos
- [ ] Testar download CSV
- [ ] Testar diferentes navegadores
- [ ] Testar responsividade

## 🎓 Conceitos Aprendidos

### Separação de Responsabilidades
- **Backend:** Regras de negócio, processamento, cálculos
- **Frontend:** Apresentação, interação, UX

### Arquitetura RESTful
- Recursos bem definidos
- Verbos HTTP corretos
- Status codes apropriados
- Documentação automática

### Type Safety
- Pydantic (Backend)
- TypeScript (Frontend)
- Contratos bem definidos

---

**Desenvolvido com 💙 para SESMA**  
**Migração concluída em: Dezembro 2025**
