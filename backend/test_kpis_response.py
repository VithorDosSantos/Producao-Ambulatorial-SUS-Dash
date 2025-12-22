"""
Script para testar se o endpoint /kpis está retornando dados reais
"""
import sys
sys.path.append('C:\\Users\\vitho\\OneDrive\\Documentos\\Sesma\\Dashboard\\backend')

from app.services.database_service import DatabaseService
from app.services.calculos_kpi import calcular_kpis_globais

# Testa get_dados_papa_filtrados
db_service = DatabaseService()

print("=== Testando endpoint /kpis ===\n")

# Busca dados PAPA
df_papa = db_service.get_dados_papa_filtrados(competencias=['202509'])
print(f"Registros PAPA retornados: {len(df_papa)}")
print(f"Colunas: {df_papa.columns.tolist()}\n")

# Busca dados Espelho
df_espelho = db_service.get_dados_espelho()
print(f"Registros Espelho retornados: {len(df_espelho)}")
print(f"Colunas: {df_espelho.columns.tolist()}\n")

# Consolida
df_consolidado = db_service.consolidar_producao_teto(df_papa, df_espelho)
print(f"Registros consolidados: {len(df_consolidado)}")
print(f"\nPrimeiras linhas do consolidado:")
print(df_consolidado.head())

# Calcula KPIs
num_meses = len(df_papa['MES_NOME'].unique())
print(f"\nNúmero de meses: {num_meses}")

kpis = calcular_kpis_globais(df_consolidado, num_meses)
print(f"\nKPIs calculados:")
for key, value in kpis.items():
    print(f"  {key}: {value}")
