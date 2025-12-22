# Guia de Instalação e Execução

## ⚡ Início Rápido

### 1. Backend (Terminal 1)

```powershell
# Navegue até a pasta do backend
cd backend

# Crie e ative ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Execute o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend rodando em: **http://localhost:8000**  
📚 Documentação API: **http://localhost:8000/docs**

### 2. Frontend (Terminal 2)

```powershell
# Navegue até a pasta do frontend
cd frontend

# Instale dependências
npm install

# Execute o servidor de desenvolvimento
npm run dev
```

✅ Frontend rodando em: **http://localhost:3000**

## 📝 Passo a Passo Detalhado

### Pré-requisitos

Certifique-se de ter instalado:

- ✅ Python 3.11 ou superior: https://www.python.org/downloads/
- ✅ Node.js 18 ou superior: https://nodejs.org/

### Backend Python/FastAPI

1. **Abra o PowerShell/Terminal**

2. **Navegue até a pasta do projeto:**
   ```powershell
   cd "C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard"
   ```

3. **Entre na pasta backend:**
   ```powershell
   cd backend
   ```

4. **Crie um ambiente virtual Python:**
   ```powershell
   python -m venv venv
   ```

5. **Ative o ambiente virtual:**
   ```powershell
   venv\Scripts\activate
   ```
   
   Você verá `(venv)` no início da linha do terminal.

6. **Instale as dependências:**
   ```powershell
   pip install -r requirements.txt
   ```

7. **Inicie o servidor FastAPI:**
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Teste se está funcionando:**
   - Abra o navegador em: http://localhost:8000
   - Você verá informações da API
   - Acesse http://localhost:8000/docs para ver a documentação interativa

### Frontend React/TypeScript

1. **Abra um NOVO PowerShell/Terminal** (mantenha o backend rodando no outro)

2. **Navegue até a pasta do projeto:**
   ```powershell
   cd "C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard"
   ```

3. **Entre na pasta frontend:**
   ```powershell
   cd frontend
   ```

4. **Instale as dependências do Node.js:**
   ```powershell
   npm install
   ```
   
   Este comando pode levar alguns minutos na primeira vez.

5. **Inicie o servidor de desenvolvimento:**
   ```powershell
   npm run dev
   ```

6. **Abra o navegador:**
   - A aplicação estará disponível em: http://localhost:3000

## 🎯 Como Usar o Dashboard

### 1. Upload de Arquivos

1. Na página inicial, você verá a seção **"Upload de Dados"**
2. Selecione os **arquivos PAPA** (pode selecionar múltiplos)
3. Selecione o **arquivo Espelho** (apenas um)
4. Clique em **"Processar Arquivos"**
5. Aguarde o processamento

### 2. Filtros

Após o upload, você pode aplicar filtros:

- **📅 Competência:** Selecione os meses para análise (Ctrl + clique para múltiplos)
- **🏷️ Categoria:** Filtre por tipo de estabelecimento
- **🏥 Unidade:** Filtre por unidade específica

### 3. Visualizações

Navegue entre as abas:

- **📊 Visão Geral:** Gráficos de barras e pizza
- **📈 Tendência Mensal:** Evolução temporal
- **📋 Dados Detalhados:** Tabela completa com opção de download

## 🔧 Solução de Problemas

### Backend não inicia

**Erro:** `uvicorn: command not found`

**Solução:**
```powershell
# Certifique-se de que o ambiente virtual está ativado
venv\Scripts\activate

# Reinstale as dependências
pip install -r requirements.txt
```

### Frontend não inicia

**Erro:** `npm: command not found`

**Solução:**
- Instale o Node.js de: https://nodejs.org/

**Erro:** `Module not found`

**Solução:**
```powershell
# Delete a pasta node_modules e package-lock.json
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# Reinstale
npm install
```

### Erro de CORS

Se você ver erros de CORS no console do navegador:

1. Certifique-se de que o backend está rodando em **http://localhost:8000**
2. Certifique-se de que o frontend está rodando em **http://localhost:3000**
3. Reinicie ambos os servidores

### Erro ao processar arquivos

**Erro:** `Coluna não encontrada`

**Solução:**
- Verifique se os arquivos CSV estão no formato correto
- Certifique-se de que os arquivos são de produção (PAPA) e teto (Espelho)
- Verifique o encoding do arquivo (deve ser latin1)

## 📦 Arquivos Necessários

### Estrutura de Arquivos CSV

**PAPA (Produção):**
- Deve conter colunas: `PA_CODUNI`, `PA_MVM` ou `PA_CMP`, `PA_VALAPR`, `PA_QTDAPR`
- Encoding: latin1
- Separador: `;` ou `,` (detectado automaticamente)

**Espelho (Teto):**
- Deve conter colunas: CNES, valor total orçado, valor físico
- Encoding: latin1
- Separador: `;`

**filtro_CATEGORIA.csv (Opcional):**
- Mapeia CNES → Categoria
- Colunas: `Num_CNES`, `Categoria`

## 🚀 Comandos Úteis

### Backend

```powershell
# Parar o servidor: Ctrl + C

# Desativar ambiente virtual
deactivate

# Ver logs detalhados
uvicorn app.main:app --reload --log-level debug
```

### Frontend

```powershell
# Parar o servidor: Ctrl + C

# Build para produção
npm run build

# Preview do build
npm run preview

# Verificar erros de lint
npm run lint
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique se todas as dependências estão instaladas
2. Verifique se as portas 8000 e 3000 estão livres
3. Consulte os logs do terminal para mensagens de erro
4. Veja a documentação da API em http://localhost:8000/docs

---

**Bom uso! 🎉**
