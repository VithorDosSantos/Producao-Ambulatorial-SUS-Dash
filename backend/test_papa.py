import sys
sys.path.append('C:\\Users\\vitho\\OneDrive\\Documentos\\Sesma\\Dashboard\\backend')

from app.services.database_service import DatabaseService

# Testa get_dados_papa_filtrados
db_service = DatabaseService()

print("=== Testando Query PAPA ===")
df = db_service.get_dados_papa_filtrados(competencias=['202509'])

print(f"Registros retornados: {len(df)}")
print(f"\nColunas: {df.columns.tolist()}")
print(f"\nPrimeiras linhas:")
print(df.head())
