import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='siasus_db',
        user='postgres',
        password='180304'
    )
    cur = conn.cursor()
    
    # Total de registros
    cur.execute('SELECT COUNT(*) FROM atendimento')
    total = cur.fetchone()[0]
    print(f'Total de registros em atendimento: {total}')
    
    if total > 0:
        # Competências disponíveis
        cur.execute('SELECT DISTINCT competencia FROM atendimento ORDER BY competencia DESC LIMIT 10')
        print('\nCompetências disponíveis:')
        for row in cur.fetchall():
            print(f'  - {row[0]}')
        
        # Amostra de dados
        cur.execute('SELECT * FROM atendimento LIMIT 1')
        print('\nColunas da tabela:')
        for desc in cur.description:
            print(f'  - {desc[0]}')
    
    conn.close()
except Exception as e:
    print(f'Erro: {e}')
