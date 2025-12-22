import sys
sys.path.insert(0, r'C:\Users\vitho\OneDrive\Documentos\Sesma\Dashboard\backend')
from app.database import engine_papa
import pandas as pd
import sqlalchemy as sa

try:
    with engine_papa.connect() as conn:
        print('Contando registros na tabela atendimento para 2025...')
        result = conn.execute(sa.text("""
            SELECT competencia, COUNT(*) as total
            FROM atendimento
            WHERE competencia LIKE '2025%'
            GROUP BY competencia
            ORDER BY competencia
        """))
        rows = result.fetchall()
        if rows:
            for r in rows:
                print(f"Competencia: {r[0]}, Total: {r[1]}")
        else:
            print('Nenhum registro encontrado para 2025 na tabela atendimento.')
except Exception as e:
    print('Erro ao consultar tabela atendimento:', e)
    import traceback
    traceback.print_exc()
