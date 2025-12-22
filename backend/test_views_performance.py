"""Teste rápido da performance das views materializadas"""
from app.services.database_service import engine_papa
import pandas as pd
import time

print("⚡ Testando performance das views materializadas...\n")

# Teste 1: Contar registros
start = time.time()
df = pd.read_sql('SELECT COUNT(*) as total FROM mv_producao_consolidada', engine_papa)
tempo1 = time.time() - start
print(f"1. COUNT na view materializada:")
print(f"   Total: {df['total'][0]:,} registros")
print(f"   Tempo: {tempo1:.3f}s\n")

# Teste 2: Query com filtro (simula dashboard)
start = time.time()
df = pd.read_sql("""
    SELECT cnes_key, categoria, 
           SUM(valor_aprovado) as total_valor,
           COUNT(*) as total_registros
    FROM mv_producao_consolidada
    WHERE competencia IN ('202501', '202502', '202503')
    GROUP BY cnes_key, categoria
""", engine_papa)
tempo2 = time.time() - start
print(f"2. Query agregada (simula KPIs):")
print(f"   Linhas retornadas: {len(df)}")
print(f"   Tempo: {tempo2:.3f}s\n")

# Teste 3: Query completa (tabela detalhada)
start = time.time()
df = pd.read_sql("""
    SELECT *
    FROM mv_producao_consolidada
    WHERE competencia IN ('202501')
    LIMIT 1000
""", engine_papa)
tempo3 = time.time() - start
print(f"3. Query detalhada (1000 registros):")
print(f"   Linhas: {len(df)}")
print(f"   Tempo: {tempo3:.3f}s\n")

print(f"✅ Views materializadas funcionando perfeitamente!")
print(f"⚡ Tempo total dos testes: {tempo1+tempo2+tempo3:.3f}s")
