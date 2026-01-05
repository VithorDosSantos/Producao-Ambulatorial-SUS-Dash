"""
Script de teste para verificar se as categorias funcionam no upload de arquivos
"""
import sys
sys.path.append('backend')

from backend.app.services.limpeza_dados import carregar_mapa_categorias, classificar_unidade

# Testa carregamento do mapa de categorias
print("=" * 80)
print("TESTE 1: Carregando mapa de categorias do CSV")
print("=" * 80)
mapa = carregar_mapa_categorias()

if mapa:
    print(f"✓ Mapa carregado com {len(mapa)} entradas")
    print("\nExemplos:")
    for i, (cnes, cat) in enumerate(list(mapa.items())[:10]):
        print(f"  CNES {cnes} -> {cat}")
        if i >= 9:
            break
else:
    print("✗ Erro ao carregar mapa de categorias")

print("\n" + "=" * 80)
print("TESTE 2: Classificando unidades com mapa")
print("=" * 80)

# Testa alguns CNESs do CSV
testes = [
    ('2337444', 'CAPS II'),
    ('2695197', 'CASA AD CENTRO ATENCAO PSIC USUARIO ALCOOL E DROGA'),
    ('9617868', 'UPA DAGUA I'),
    ('2337339', 'HOSPITAL PRONTO SOCORRO MUNICIPAL MARIO PINOTTI'),
    ('7377401', 'AMBULANCHA TAYNARA BASE COTIJUBA'),
    ('2334267', 'UNIDADE BASICA DE SAUDE DA PEDREIRA'),
]

for cnes, nome in testes:
    categoria = classificar_unidade(nome, cnes, mapa)
    esperado = mapa.get(cnes, 'DESCONHECIDO') if mapa else 'DESCONHECIDO'
    print(f"  CNES {cnes} - {nome}")
    print(f"    → Categoria obtida: {categoria}")
    print(f"    → Esperado no mapa: {esperado}")
    print()

print("=" * 80)
print("TESTE 3: Testando unidades sem mapeamento (fallback)")
print("=" * 80)

# Testa unidades fictícias sem CNES no mapa
testes_fallback = [
    ('9999999', 'UPA TESTE'),
    ('8888888', 'HOSPITAL FICTICIO'),
    ('7777777', 'UBS EXEMPLO'),
]

for cnes, nome in testes_fallback:
    categoria = classificar_unidade(nome, cnes, mapa)
    print(f"  CNES {cnes} - {nome}")
    print(f"    → Categoria obtida: {categoria}")
    print()
