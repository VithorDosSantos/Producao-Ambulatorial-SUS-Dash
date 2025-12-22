import sys
sys.path.insert(0, r"C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend")

from app.services.database_service import engine_papa
import pandas as pd

# Ver colunas da tabela atendimento (PAPA)
print("=== Colunas da tabela atendimento ===")
df_cols = pd.read_sql("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'atendimento' 
    ORDER BY ordinal_position
""", engine_papa)
print(df_cols['column_name'].tolist())

# Ver dados distintos de unidades
print("\n=== Unidades disponíveis (com nomes) ===")
df_unidades = pd.read_sql("""
    SELECT DISTINCT 
        codigo_unidade,
        nome_unidade
    FROM atendimento
    WHERE codigo_unidade IS NOT NULL
    ORDER BY nome_unidade
    LIMIT 10
""", engine_papa)
print(df_unidades)
print(f"\nTotal de unidades únicas: {df_unidades.shape[0]}")
