# 🚂 Deploy no Railway - Guia Completo

## Passo 1: Criar conta e conectar GitHub

1. Acesse: **https://railway.app**
2. Clique em **"Start a New Project"**
3. Faça login com sua conta **GitHub**
4. Autorize o Railway a acessar seus repositórios

---

## Passo 2: Deploy do Backend (Python/FastAPI)

### 2.1 Criar serviço do Backend

1. No Railway, clique em **"+ New"**
2. Selecione **"GitHub Repo"**
3. Escolha o repositório: **"Producao-Ambulatorial-SUS-Dash"**
4. Clique em **"Deploy Now"**

### 2.2 Configurar o Backend

1. Railway detectará Python automaticamente
2. Clique no serviço criado
3. Vá em **"Settings"** (ícone de engrenagem)
4. Em **"Root Directory"**, digite: `backend`
5. Em **"Build Command"**, deixe: `pip install -r requirements.txt`
6. Em **"Start Command"**, coloque: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.3 Adicionar Variáveis de Ambiente

1. Clique na aba **"Variables"**
2. Adicione as seguintes variáveis (clique em "+ New Variable" para cada uma):

```
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
```

**Aguarde!** Não adicione as variáveis do banco ainda. Faremos isso depois de criar o PostgreSQL.

---

## Passo 3: Adicionar PostgreSQL

### 3.1 Criar banco de dados

1. No mesmo projeto, clique em **"+ New"**
2. Selecione **"Database"**
3. Escolha **"Add PostgreSQL"**
4. Railway criará o banco automaticamente

### 3.2 Copiar credenciais do banco

1. Clique no **PostgreSQL** criado
2. Vá na aba **"Variables"**
3. Você verá variáveis como:
   - `PGHOST`
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGPORT`

**IMPORTANTE:** Copie esses valores! Você vai precisar deles.

### 3.3 Adicionar variáveis do banco no Backend

1. Volte para o serviço do **Backend**
2. Vá em **"Variables"**
3. Adicione as seguintes variáveis usando os valores que você copiou:

```
DB_PAPA_HOST=<valor do PGHOST>
DB_PAPA_DATABASE=<valor do PGDATABASE>
DB_PAPA_USER=<valor do PGUSER>
DB_PAPA_PASSWORD=<valor do PGPASSWORD>
DB_PAPA_PORT=<valor do PGPORT>

DB_ESPELHO_HOST=<mesmo valor do PGHOST>
DB_ESPELHO_DATABASE=<mesmo valor do PGDATABASE>
DB_ESPELHO_USER=<mesmo valor do PGUSER>
DB_ESPELHO_PASSWORD=<mesmo valor do PGPASSWORD>
DB_ESPELHO_PORT=<mesmo valor do PGPORT>
```

4. O Railway fará **redeploy automático** do backend

---

## Passo 4: Deploy do Frontend (React/Vite)

### 4.1 Criar serviço do Frontend

1. No mesmo projeto, clique em **"+ New"**
2. Selecione **"GitHub Repo"**
3. Escolha o **mesmo repositório** novamente
4. Clique em **"Deploy Now"**

### 4.2 Configurar o Frontend

1. Clique no serviço do frontend
2. Vá em **"Settings"**
3. Em **"Root Directory"**, digite: `frontend`
4. Em **"Build Command"**, coloque: `npm install && npm run build`
5. Em **"Start Command"**, coloque: `npx serve dist -s -p $PORT`

### 4.3 Adicionar Variáveis de Ambiente

1. Primeiro, copie a **URL do backend**:
   - Vá no serviço do backend
   - Na aba **"Settings"**, copie a URL que aparece (ex: `https://seu-backend.up.railway.app`)

2. Volte no serviço do **frontend**
3. Vá em **"Variables"**
4. Adicione:

```
VITE_API_URL=<URL do backend que você copiou>
```

---

## Passo 5: Configurar CORS no Backend

### 5.1 Adicionar URL do frontend no CORS

1. Copie a **URL do frontend** (ex: `https://seu-frontend.up.railway.app`)
2. Vá no serviço do **backend**
3. Vá em **"Variables"**
4. Adicione:

```
CORS_ORIGINS=<URL do frontend>
```

5. O Railway fará redeploy automático

---

## Passo 6: Testar!

1. Acesse a **URL do frontend** (está em Settings do frontend)
2. Teste o upload de CSV
3. Verifique se tudo funciona!

---

## 🎯 URLs Finais

Depois do deploy, você terá:

- **Frontend:** `https://seu-frontend.up.railway.app`
- **Backend API:** `https://seu-backend.up.railway.app`
- **Backend Docs:** `https://seu-backend.up.railway.app/docs`
- **PostgreSQL:** Interno no Railway

---

## 💰 Custo

- **Crédito grátis:** $5/mês
- **Uso estimado:** ~$3-5/mês
- **Primeiro mês:** GRÁTIS
- Depois: Pay-as-you-go

---

## 🔧 Troubleshooting

### Se o backend não subir:

1. Vá em **"Deployments"**
2. Clique no último deployment
3. Veja os **logs**
4. Procure por erros

### Se o frontend não carregar:

1. Verifique se `VITE_API_URL` está correta
2. Teste acessando `https://seu-backend.up.railway.app` diretamente
3. Limpe o cache do navegador (Ctrl+Shift+Delete)

### Se der erro de CORS:

1. Verifique se `CORS_ORIGINS` no backend tem a URL correta do frontend
2. Certifique-se de que NÃO tem barra `/` no final da URL

---

## ✅ Checklist Final

- [ ] Backend deployado e "Live"
- [ ] PostgreSQL criado
- [ ] Variáveis do banco configuradas no backend
- [ ] Frontend deployado e "Live"
- [ ] VITE_API_URL configurada no frontend
- [ ] CORS_ORIGINS configurada no backend
- [ ] Testado upload de CSV com sucesso

---

**Pronto! Seu dashboard está no ar!** 🎉
