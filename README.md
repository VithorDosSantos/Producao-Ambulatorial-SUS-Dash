# Dashboard SIA/SUS - Sistema de Gestão Estratégica

Sistema completo de análise e visualização de dados SIA/SUS com arquitetura desacoplada Backend (Python/FastAPI) + Frontend (React/TypeScript).

## 📋 Estrutura do Projeto

```
Dashboard/
├── backend/              # API Backend (Python/FastAPI)
│   ├── app/
│   │   ├── main.py      # Entrada da aplicação
│   │   ├── routers/     # Endpoints da API
│   │   ├── services/    # Lógica de negócio
│   │   ├── models/      # Schemas/tipos de dados
│   │   └── utils/       # Funções auxiliares
│   └── requirements.txt
├── frontend/             # Interface React/TypeScript
│   ├── src/
│   │   ├── components/  # Componentes reutilizáveis
│   │   ├── pages/       # Páginas da aplicação
│   │   ├── services/    # Comunicação com API
│   │   └── types/       # Tipos TypeScript
│   └── package.json
├── filtro_CATEGORIA.csv # Mapeamento CNES → Categoria
└── README.md
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- npm ou yarn

### Backend (FastAPI)

1. **Navegue até a pasta do backend:**
   ```bash
   cd backend
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute o servidor:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Acesse a documentação da API:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend (React/TypeScript)

1. **Navegue até a pasta do frontend:**
   ```bash
   cd frontend
   ```

2. **Instale as dependências:**
   ```bash
   npm install
   ```

3. **Execute o servidor de desenvolvimento:**
   ```bash
   npm run dev
   ```

4. **Acesse a aplicação:**
   - URL: http://localhost:3000

## 📊 Funcionalidades

### Upload de Dados
- **Arquivos PAPA (Produção):** Upload múltiplo de CSVs
- **Arquivo Espelho (Teto):** Upload único de CSV
- Validação e processamento automático

### Processamento
- Detecção automática de separador CSV
- Remoção de BOM e caracteres inválidos
- Normalização de textos
- Limpeza de valores monetários brasileiros
- Preenchimento de CNES (7 dígitos)
- INNER JOIN Produção × Espelho

### Regras de Negócio SUS
- ✅ Prioridade PA_MVM sobre PA_CMP
- ✅ Fallback automático se PA_MVM ausente
- ✅ Filtro Natureza Jurídica 1031 (Municipal)
- ✅ Classificação por categoria via CSV ou palavras-chave

### Sistema de Filtros
- 📅 **Competência:** Seleção de meses
- 🏷️ **Categoria:** Filtro por tipo de estabelecimento
- 🏥 **Unidade:** Filtro por unidade de saúde
- Filtros em cascata com atualização automática

### Indicadores (KPIs)
- **ORÇADO:** Quantidade e Valor Teto
- **APRESENTADO:** Quantidade e Valor Apresentado
- **APROVADO:** Quantidade, Valor Aprovado e % Execução
- Barra de progresso com cores dinâmicas

### Visualizações
- 📊 **Barras Agrupadas:** Orçado × Aprovado por unidade (Top 10)
- 🍩 **Donut:** Distribuição por categoria
- 📈 **Linha Temporal:** Aprovado, Apresentado e Teto mensal

### Tabela e Exportação
- Tabela detalhada interativa
- Ordenação por coluna
- Cores dinâmicas de saldo
- **Download CSV:** Separador `;`, Decimal `,`, Encoding `latin1`

## 🔌 Endpoints da API

### Upload
- `POST /upload/papa` - Upload arquivos PAPA
- `POST /upload/espelho` - Upload arquivo Espelho
- `GET /upload/status` - Status dos dados
- `DELETE /upload/reset` - Limpar dados

### Filtros
- `GET /filtros/competencias` - Lista meses
- `GET /filtros/categorias` - Lista categorias
- `GET /filtros/unidades` - Lista unidades
- `GET /filtros/todos` - Todos os filtros

### Dados
- `GET /kpis` - KPIs globais
- `GET /visao-geral/unidades` - Produção por unidade
- `GET /visao-geral/categorias` - Distribuição por categoria
- `GET /tendencia-mensal` - Série temporal
- `GET /tabela-detalhada` - Tabela completa
- `GET /tabela-detalhada/download/csv` - Download CSV

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno
- **Pandas** - Processamento de dados
- **NumPy** - Cálculos numéricos
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool
- **Tailwind CSS** - Estilização
- **ECharts** - Gráficos interativos
- **Axios** - Cliente HTTP

## 📝 Desenvolvimento

### Adicionar Novos Endpoints (Backend)

1. Crie um novo router em `backend/app/routers/`
2. Implemente a lógica em `backend/app/services/`
3. Registre o router em `backend/app/main.py`

### Adicionar Novos Componentes (Frontend)

1. Crie o componente em `frontend/src/components/`
2. Adicione tipos em `frontend/src/types/`
3. Integre na página `frontend/src/pages/Dashboard.tsx`

## 🔒 Segurança

- ✅ CORS configurado para desenvolvimento
- ✅ Validação de dados com Pydantic
- ✅ Tratamento de erros global
- ⚠️ **Produção:** Adicionar autenticação, rate limiting e HTTPS

## 📦 Build para Produção

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
# Arquivos em frontend/dist/
```

## 🤝 Contribuindo

1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário e confidencial.

## 👥 Autores

- **Desenvolvido para:** SESMA (Secretaria Municipal de Saúde)
- **Propósito:** Gestão Estratégica SIA/SUS

---

**Versão:** 1.0.0  
**Data:** Dezembro 2025
