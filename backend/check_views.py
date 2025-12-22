"""Verifica se todas as views materializadas foram criadas"""
from app.services.database_service import engine_papa
import pandas as pd
import sqlalchemy as sa

print("🔍 Verificando views materializadas...\n")

# 1. Listar views criadas
with engine_papa.connect() as conn:
    result = conn.execute(sa.text("""
        SELECT 
            schemaname,
            matviewname,
            ispopulated,
            hasindexes
        FROM pg_matviews 
        WHERE matviewname LIKE 'mv_%'
        ORDER BY matviewname
    """))
    df_views = pd.DataFrame(result.fetchall(), columns=result.keys())

print("📋 Views materializadas encontradas:")
if len(df_views) > 0:
    for _, row in df_views.iterrows():
        status = "✅" if row['ispopulated'] else "❌"
        indices = "📊 com índices" if row['hasindexes'] else "⚠️ sem índices"
        print(f"  {status} {row['matviewname']} - {indices}")
else:
    print("  ❌ Nenhuma view materializada encontrada!")

# 2. Contar registros em cada view
print("\n📊 Contagem de registros:")
if len(df_views) > 0:
    for view_name in df_views['matviewname']:
        try:
            with engine_papa.connect() as conn:
                result = conn.execute(sa.text(f"SELECT COUNT(*) as total FROM {view_name}"))
                total = result.fetchone()[0]
                print(f"  • {view_name}: {total:,} registros")
        except Exception as e:
            print(f"  ❌ {view_name}: ERRO - {str(e)[:50]}")

# 3. Listar índices criados
print("\n🔑 Índices criados nas views:")
with engine_papa.connect() as conn:
    result = conn.execute(sa.text("""
        SELECT 
            schemaname,
            tablename,
            indexname
        FROM pg_indexes
        WHERE tablename LIKE 'mv_%'
        ORDER BY tablename, indexname
    """))
    df_indices = pd.DataFrame(result.fetchall(), columns=result.keys())

if len(df_indices) > 0:
    current_view = None
    for _, row in df_indices.iterrows():
        if current_view != row['tablename']:
            current_view = row['tablename']
            print(f"  📋 {current_view}:")
        print(f"    - {row['indexname']}")
else:
    print("  ⚠️ Nenhum índice encontrado!")

# 4. Verificar tamanho
print("\n💾 Tamanho das views:")
with engine_papa.connect() as conn:
    result = conn.execute(sa.text("""
        SELECT 
            schemaname,
            matviewname,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
        FROM pg_matviews
        WHERE matviewname LIKE 'mv_%'
        ORDER BY matviewname
    """))
    df_size = pd.DataFrame(result.fetchall(), columns=result.keys())

if len(df_size) > 0:
    for _, row in df_size.iterrows():
        print(f"  • {row['matviewname']}: {row['size']}")

print("\n" + "="*60)
expected_views = ['mv_producao_consolidada', 'mv_kpis_agregados', 'mv_tendencia_mensal']
created_views = df_views['matviewname'].tolist() if len(df_views) > 0 else []
missing = set(expected_views) - set(created_views)

if len(missing) == 0 and len(created_views) == len(expected_views):
    print("✅ TODAS AS 3 VIEWS FORAM CRIADAS COM SUCESSO!")
    print("⚡ Dashboard está pronto para performance máxima!")
else:
    print(f"⚠️ Faltam {len(missing)} view(s): {', '.join(missing)}")
    print("Execute: py create_views.py")
