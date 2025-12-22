import sys
sys.path.insert(0, r"C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend")

from app.services.database_service import engine_papa
import pandas as pd

# Ver colunas da tabela unidade_saude
print("=== Colunas da tabela unidade_saude ===")
df_cols = pd.read_sql("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'unidade_saude' 
    ORDER BY ordinal_position
""", engine_papa)
print(df_cols['column_name'].tolist())

# Ver exemplo de dados
print("\n=== Exemplo de dados ===")
df_sample = pd.read_sql("""
    SELECT * FROM unidade_saude LIMIT 3
""", engine_papa)
print(df_sample)
