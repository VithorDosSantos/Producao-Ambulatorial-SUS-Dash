import sys
sys.path.insert(0, r'C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend')

from app.services.database_service import db_service

try:
    print("Testando query PAPA...")
    df_papa = db_service.get_dados_papa_filtrados(['202509', '202508', '202507'])
    print(f"Registros retornados: {len(df_papa)}")
    if not df_papa.empty:
        print(f"\nColunas: {list(df_papa.columns)}")
        print(f"\nPrimeiras linhas:")
        print(df_papa.head())
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
