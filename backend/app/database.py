"""
Configuração dos engines SQLAlchemy para os dois bancos de dados
"""
from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from .config import get_papa_connection_string, get_espelho_connection_string

logger = logging.getLogger(__name__)

# =============================================
# ENGINES DOS BANCOS DE DADOS
# =============================================

# Engine para banco PAPA (Produção SIASUS)
engine_papa = create_engine(
    get_papa_connection_string(),
    poolclass=pool.QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    connect_args={
        "connect_timeout": 5,  # Timeout de 5 segundos
        "options": "-c statement_timeout=30000"  # 30s para queries
    },
    echo=False  # Debug SQL (True para desenvolvimento)
)

# Engine para banco Espelho (Teto Orçamentário)
engine_espelho = create_engine(
    get_espelho_connection_string(),
    poolclass=pool.QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 5,
        "options": "-c statement_timeout=30000"
    },
    echo=False
)

# =============================================
# SESSION MAKERS
# =============================================

SessionPapa = sessionmaker(autocommit=False, autoflush=False, bind=engine_papa)
SessionEspelho = sessionmaker(autocommit=False, autoflush=False, bind=engine_espelho)

# =============================================
# DEPENDENCY INJECTION
# =============================================

def get_papa_db() -> Generator[Session, None, None]:
    """Dependency para obter sessão do banco PAPA"""
    db = SessionPapa()
    try:
        yield db
    finally:
        db.close()

def get_espelho_db() -> Generator[Session, None, None]:
    """Dependency para obter sessão do banco Espelho"""
    db = SessionEspelho()
    try:
        yield db
    finally:
        db.close()

# =============================================
# FUNÇÕES AUXILIARES
# =============================================

def test_connections():
    """Testa conexões com ambos os bancos com timeout"""
    try:
        # Testa PAPA
        with engine_papa.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Conexão com banco PAPA OK")
        
        # Testa Espelho
        with engine_espelho.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Conexão com banco Espelho OK")
        
        return True
    except Exception as e:
        logger.warning(f"⚠️ Bancos não conectados: {str(e)[:100]}")
        return False

def close_connections():
    """Fecha conexões com os bancos"""
    try:
        engine_papa.dispose()
        engine_espelho.dispose()
        logger.info("Conexões com bancos fechadas")
    except Exception as e:
        logger.warning(f"Erro ao fechar conexões: {e}")
