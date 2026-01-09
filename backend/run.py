"""
Script de inicialização do Uvicorn
Lê a variável PORT do ambiente e inicia o servidor
"""
import os
import sys

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
