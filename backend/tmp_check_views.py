import sys
sys.path.insert(0, r'C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend')
from app.database import engine_papa
import sqlalchemy as sa

views = [
    'mv_producao_consolidada',
    'mv_kpis_agregados',
    'mv_tendencia_mensal'
]

for view in views:
    try:
        with engine_papa.connect() as conn:
            print(f'Contando registros em {view} para 2025...')
            result = conn.execute(sa.text(f"""
                SELECT competencia, COUNT(*) as total
                FROM {view}
                WHERE competencia LIKE '2025%'
                GROUP BY competencia
                ORDER BY competencia
            """))
            rows = result.fetchall()
            if rows:
                for r in rows:
                    print(f"{view} - Competencia: {r[0]}, Total: {r[1]}")
            else:
                print(f'{view}: Nenhum registro encontrado para 2025.')
    except Exception as e:
        print(f'Erro ao consultar {view}:', e)
