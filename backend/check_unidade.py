import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='siasus_db',
        user='postgres',
        password='180304'
    )
    cur = conn.cursor()
    
    # Colunas da tabela unidade_saude
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'unidade_saude'")
    print('Colunas da tabela unidade_saude:')
    for row in cur.fetchall():
        print(f'  - {row[0]}')
    
    conn.close()
except Exception as e:
    print(f'Erro: {e}')
