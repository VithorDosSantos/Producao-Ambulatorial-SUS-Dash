import sys
sys.path.insert(0, r'C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend')

from app.services.database_service import db_service
import pandas as pd

print("=== Testando Query Espelho ===")
try:
    df_espelho = db_service.get_dados_espelho()
    print(f"Registros retornados: {len(df_espelho)}")
    
    if not df_espelho.empty:
        print(f"\nColunas: {list(df_espelho.columns)}")
        print(f"\nPrimeiras linhas:")
        print(df_espelho.head())
    else:
        print("DataFrame vazio!")
        
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
