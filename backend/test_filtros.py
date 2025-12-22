import sys
sys.path.insert(0, r"C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend")

from app.services.database_service import db_service
import json

print("=== Testando endpoint /filtros/todos ===\n")

print("1. Competências:")
competencias = db_service.get_competencias_disponiveis()
print(f"   Total: {len(competencias)}")
if competencias:
    print(f"   Primeiras 3: {competencias[:3]}")
else:
    print("   VAZIO!")

print("\n2. Categorias:")
categorias = db_service.get_categorias_disponiveis()
print(f"   Total: {len(categorias)}")
if categorias:
    print(f"   Todas: {categorias}")
else:
    print("   VAZIO!")

print("\n3. Unidades:")
unidades = db_service.get_unidades_disponiveis()
print(f"   Total: {len(unidades)}")
if unidades:
    print(f"   Primeiras 3:")
    for u in unidades[:3]:
        print(f"      {u}")
else:
    print("   VAZIO!")

print("\n=== Resposta JSON do endpoint ===")
response = {
    "competencias": competencias,
    "categorias": categorias,
    "unidades": unidades
}
print(json.dumps(response, indent=2, ensure_ascii=False)[:500] + "...")
