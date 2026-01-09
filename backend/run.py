"""
Script de inicialização do Uvicorn
Lê a variável PORT do ambiente e inicia o servidor
"""
import os
import sys

if __name__ == "__main__":
    # Lê PORT do ambiente
    port_env = os.getenv("PORT", "8000")
    print(f"PORT environment variable: {port_env}")
    
    try:
        port = int(port_env)
        print(f"Starting server on port: {port}")
    except ValueError:
        print(f"ERROR: PORT value '{port_env}' is not valid, using 8000")
        port = 8000
    
    import uvicorn
    
    print(f"Uvicorn starting on 0.0.0.0:{port}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
