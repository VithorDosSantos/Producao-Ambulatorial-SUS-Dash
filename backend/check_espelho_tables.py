import sys
sys.path.insert(0, r"C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend")

from app.services.database_service import engine_espelho
import pandas as pd

print("=== Tabelas no banco Espelho ===")
df_tables = pd.read_sql("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""", engine_espelho)
print(df_tables['table_name'].tolist())

print("\n=== Colunas da primeira tabela ===")
table_name = df_tables['table_name'].iloc[0]
df_cols = pd.read_sql(f"""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
""", engine_espelho)
print(f"Tabela: {table_name}")
print(df_cols['column_name'].tolist())

print(f"\n=== Exemplo de dados da tabela {table_name} ===")
df_sample = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 3", engine_espelho)
print(df_sample)
