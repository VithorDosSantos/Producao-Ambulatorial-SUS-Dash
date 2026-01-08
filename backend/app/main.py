"""
API Backend - Dashboard SIA/SUS
FastAPI application main entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .routers import filtros, kpis, visao_geral, tendencia, tabela
from .routers import upload
from .database import test_connections, close_connections

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================
# LIFESPAN: Inicialização e Finalização
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia ciclo de vida da aplicação
    - Startup: Testa conexões com bancos
    - Shutdown: Fecha conexões
    """
    # Startup
    logger.info("🚀 Iniciando Dashboard SIA/SUS API...")
    logger.info("📊 Conectando aos bancos de dados...")
    
    if test_connections():
        logger.info("✅ Sistema pronto! Dados vêm diretamente do banco PostgreSQL")
    else:
        logger.error("❌ Falha ao conectar aos bancos. Verifique as configurações.")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")
    close_connections()
    logger.info("✅ Conexões fechadas")

# =============================================
# CRIAÇÃO DA APLICAÇÃO
# =============================================
app = FastAPI(
    title="Dashboard SIA/SUS API",
    description="API RESTful para gestão estratégica de dados SIA/SUS com PostgreSQL",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuração CORS (permite acesso do frontend)
import os

# URLs permitidas - adicione aqui a URL do seu frontend em produção
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:5173",
]

# Em produção, adicionar URLs do Render/Vercel
if os.getenv("ENVIRONMENT") == "production":
    production_urls = os.getenv("CORS_ORIGINS", "").split(",")
    allowed_origins.extend([url.strip() for url in production_urls if url.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# REGISTRA ROUTERS (sem upload)
# =============================================

# REGISTRA ROUTERS
app.include_router(filtros.router)
app.include_router(kpis.router)
app.include_router(visao_geral.router)
app.include_router(tendencia.router)
app.include_router(tabela.router)
app.include_router(upload.router)


@app.get("/")
async def root():
    """
    Endpoint raiz - informações da API
    """
    return {
        "nome": "Dashboard SIA/SUS API",
        "versao": "2.0.0",
        "status": "online",
        "tipo_dados": "PostgreSQL (Banco PAPA + Banco Espelho)",
        "documentacao": "/docs",
        "endpoints": {
            "filtros": "/filtros/*",
            "kpis": "/kpis",
            "visao_geral": "/visao-geral/*",
            "tendencia": "/tendencia-mensal",
            "tabela": "/tabela-detalhada"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint - verifica conexão com bancos
    """
    db_status = test_connections()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": "2.0.0"
    }


# Tratamento global de erros
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas
    """
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erro interno do servidor",
            "detalhes": str(exc)
        }
    )
