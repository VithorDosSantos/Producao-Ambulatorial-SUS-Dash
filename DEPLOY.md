# 🚀 Guia de Deploy - Dashboard SIA/SUS

## Opção 1: Deploy no Render (Recomendado)

### Passo 1: Preparação

1. **Crie uma conta no Render**
   - Acesse: https://render.com
   - Faça login com GitHub (recomendado)

2. **Faça push do código para o GitHub**
   ```bash
   git push origin desenvolvimento
   ```

### Passo 2: Criar Banco de Dados PostgreSQL

1. No painel do Render, clique em **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `dashboard-sus-db`
   - **Database:** `siasus_db`
   - **User:** `dashboard_user`
   - **Region:** Oregon (US West) - Free tier
   - **Plan:** Starter ($7/mês) ou Free
3. Clique em **"Create Database"**
4. **Importante:** Anote as credenciais (host, user, password, database)

### Passo 3: Importar Dados para o PostgreSQL

**Opção A: Via pgAdmin ou DBeaver**
1. Conecte-se ao banco usando as credenciais do Render
2. Execute os scripts SQL para criar as tabelas:
   - `01_create_database.sql`
   - Importe os CSVs (PAPA2501.csv, etc.)

**Opção B: Via linha de comando**
```bash
# Conectar ao banco
psql -h [RENDER_HOST] -U dashboard_user -d siasus_db

# Executar scripts
\i 01_create_database.sql

# Importar dados
\copy papa FROM 'PAPA2501.csv' WITH CSV HEADER;
```

### Passo 4: Deploy do Backend (FastAPI)

1. No Render, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub
3. Configure:
   - **Name:** `dashboard-sus-backend`
   - **Region:** Oregon (US West)
   - **Branch:** `desenvolvimento`
   - **Root Directory:** (deixe vazio)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free ou Starter

4. **Variáveis de Ambiente:**
   Clique em "Advanced" e adicione:
   ```
   DB_PAPA_HOST=<seu_host_render>
   DB_PAPA_DATABASE=siasus_db
   DB_PAPA_USER=dashboard_user
   DB_PAPA_PASSWORD=<sua_senha>
   DB_PAPA_PORT=5432
   DB_ESPELHO_HOST=<seu_host_render>
   DB_ESPELHO_DATABASE=Espelho_siasus
   DB_ESPELHO_USER=dashboard_user
   DB_ESPELHO_PASSWORD=<sua_senha>
   DB_ESPELHO_PORT=5432
   ```

5. Clique em **"Create Web Service"**

### Passo 5: Deploy do Frontend (React/Vite)

**Opção A: Deploy no Render (tudo junto)**

1. Use o arquivo `render.yaml` já configurado:
   - Faça push do render.yaml para o repositório
   - No Render, clique em **"New +"** → **"Blueprint"**
   - Selecione seu repositório
   - O Render criará automaticamente backend, frontend e database

**Opção B: Deploy no Vercel (Frontend separado - Mais rápido)**

1. Acesse: https://vercel.com
2. Importe o repositório do GitHub
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. **Variável de Ambiente:**
   ```
   VITE_API_URL=https://dashboard-sus-backend.onrender.com
   ```
5. Deploy!

### Passo 6: Configurar CORS no Backend

Atualize o arquivo `backend/app/main.py` com a URL do frontend em produção:

```python
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://seu-frontend.vercel.app",  # Adicione aqui
    "https://seu-frontend.onrender.com",  # Ou aqui
]
```

---

## Opção 2: Deploy no Railway

### Passo Rápido:

1. Acesse: https://railway.app
2. Clique em "Start a New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha o repositório
5. Railway detectará automaticamente FastAPI e React
6. Adicione PostgreSQL clicando em "+ New" → "Database" → "PostgreSQL"
7. Configure as variáveis de ambiente
8. Deploy automático!

---

## Opção 3: Deploy no Azure (Para Órgãos Governamentais)

### Recursos necessários:

1. **Azure App Service** (Backend FastAPI)
2. **Azure Static Web Apps** (Frontend React)
3. **Azure Database for PostgreSQL** (Banco de dados)

### Passo a passo:

```bash
# Login no Azure
az login

# Criar grupo de recursos
az group create --name dashboard-sus-rg --location brazilsouth

# Criar PostgreSQL
az postgres flexible-server create \
  --resource-group dashboard-sus-rg \
  --name dashboard-sus-db \
  --location brazilsouth \
  --admin-user adminuser \
  --admin-password SuaSenhaSegura123! \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14

# Deploy do Backend
az webapp up \
  --resource-group dashboard-sus-rg \
  --name dashboard-sus-backend \
  --runtime "PYTHON:3.11" \
  --location brazilsouth

# Deploy do Frontend (via Static Web Apps)
# Use a extensão do VS Code: Azure Static Web Apps
```

---

## Checklist Pré-Deploy ✅

- [ ] Código commitado e pushed para o GitHub
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados criado
- [ ] Tabelas e dados importados
- [ ] CORS configurado corretamente
- [ ] Scripts SQL executados
- [ ] `.env.example` atualizado
- [ ] Testado localmente

---

## URLs Finais (exemplo)

Após o deploy bem-sucedido, você terá:

- **Backend API:** `https://dashboard-sus-backend.onrender.com`
- **Frontend:** `https://dashboard-sus-frontend.onrender.com`
  - ou: `https://seu-projeto.vercel.app`
- **Database:** Interno no Render ou Railway

---

## Custos Estimados 💰

### Render (Recomendado para começar)
- **Banco PostgreSQL:** $7/mês (Starter) ou Free (limitado)
- **Backend:** Free ou $7/mês (Starter)
- **Frontend:** Free
- **Total:** Free ou ~$14/mês

### Railway
- **Créditos gratuitos:** $5/mês
- **Pay-per-use:** ~$10-15/mês após créditos

### Vercel (Frontend) + Render (Backend)
- **Frontend Vercel:** Free
- **Backend Render:** $7/mês
- **Database Render:** $7/mês
- **Total:** ~$14/mês

---

## Suporte

Se tiver problemas:
1. Verifique os logs no painel do Render/Railway
2. Confirme que as variáveis de ambiente estão corretas
3. Teste a conexão com o banco de dados
4. Verifique se o CORS está configurado

**Logs do Render:** Dashboard → Logs → Tail Logs
**Logs do Railway:** Project → Deployments → View Logs
