import sys
sys.path.insert(0, r"C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend")

from app.routers.filtros import get_todos_filtros
import asyncio
import json

async def test():
    print("=== Testando resposta do endpoint /filtros/todos ===\n")
    
    # Simular a requisição
    response = await get_todos_filtros()
    
    # Converter para dict
    data = response.dict() if hasattr(response, 'dict') else response
    
    print("Tipo da resposta:", type(data))
    print("\n=== Competências ===")
    print(f"Total: {len(data['competencias'])}")
    if len(data['competencias']) > 0:
        print("Primeira:", data['competencias'][0])
    else:
        print("VAZIO!")
    
    print("\n=== Categorias ===")
    print(f"Total: {len(data['categorias'])}")
    print("Lista:", data['categorias'])
    
    print("\n=== Unidades ===")
    print(f"Total: {len(data['unidades'])}")
    if len(data['unidades']) > 0:
        print("Primeira:", data['unidades'][0])
        print("Estrutura da primeira unidade:")
        for key in data['unidades'][0].keys():
            print(f"  - {key}: {data['unidades'][0][key]}")
    else:
        print("VAZIO!")
    
    print("\n=== JSON Completo (primeiras 1000 chars) ===")
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    print(json_str[:1000])

if __name__ == "__main__":
    asyncio.run(test())
