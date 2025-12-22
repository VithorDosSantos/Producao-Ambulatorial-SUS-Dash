import sys
sys.path.insert(0, r"C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend")

from app.services.database_service import db_service

print("=== Testando get_unidades_disponiveis ===")
unidades = db_service.get_unidades_disponiveis()
print(f"Total de unidades: {len(unidades)}")
print("\nPrimeiras 10 unidades:")
for u in unidades[:10]:
    print(f"  {u['codigo']} - {u['nome']}")
