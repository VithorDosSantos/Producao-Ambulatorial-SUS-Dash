"""
Configurações do sistema - Conexões com bancos de dados
"""
import os
from typing import Dict

# =============================================
# CONFIGURAÇÕES DO BANCO PAPA (Produção SIASUS)
# =============================================
DB_PAPA_CONFIG: Dict[str, str] = {
    'host': os.getenv('DB_PAPA_HOST', 'localhost'),
    'database': os.getenv('DB_PAPA_DATABASE', 'siasus_db'),
    'user': os.getenv('DB_PAPA_USER', 'postgres'),
    'password': os.getenv('DB_PAPA_PASSWORD', '180304'),
    'port': os.getenv('DB_PAPA_PORT', '5432')
}

# =============================================
# CONFIGURAÇÕES DO BANCO ESPELHO (Teto Orçamentário)
# =============================================
DB_ESPELHO_CONFIG: Dict[str, str] = {
    'host': os.getenv('DB_ESPELHO_HOST', 'localhost'),
    'database': os.getenv('DB_ESPELHO_DATABASE', 'Espelho_siasus'),
    'user': os.getenv('DB_ESPELHO_USER', 'postgres'),
    'password': os.getenv('DB_ESPELHO_PASSWORD', '180304'),
    'port': os.getenv('DB_ESPELHO_PORT', '5432')
}

# =============================================
# STRINGS DE CONEXÃO
# =============================================
def get_papa_connection_string() -> str:
    """Retorna string de conexão para o banco PAPA"""
    return (
        f"postgresql://{DB_PAPA_CONFIG['user']}:{DB_PAPA_CONFIG['password']}"
        f"@{DB_PAPA_CONFIG['host']}:{DB_PAPA_CONFIG['port']}/{DB_PAPA_CONFIG['database']}"
    )

def get_espelho_connection_string() -> str:
    """Retorna string de conexão para o banco Espelho"""
    return (
        f"postgresql://{DB_ESPELHO_CONFIG['user']}:{DB_ESPELHO_CONFIG['password']}"
        f"@{DB_ESPELHO_CONFIG['host']}:{DB_ESPELHO_CONFIG['port']}/{DB_ESPELHO_CONFIG['database']}"
    )

# =============================================
# CONFIGURAÇÕES GERAIS
# =============================================
CACHE_TTL_SECONDS = 300  # Cache de 5 minutos
MAX_WORKERS = 4  # Threads para queries paralelas
