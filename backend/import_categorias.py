"""
Script para importar categorias do filtro_CATEGORIA.csv para o banco de dados
"""
import pandas as pd
from sqlalchemy import text
from app.database import engine_papa
import os

def importar_categorias():
    """Importa categorias do CSV para o banco de dados"""
    
    # Caminho para o CSV
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'filtro_CATEGORIA.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return False
    
    # Ler CSV
    print(f"📁 Lendo arquivo: {csv_path}")
    df = pd.read_csv(csv_path, sep=';', encoding='latin1', dtype=str)
    
    # Limpar BOM e espaços dos nomes das colunas
    import re
    colunas_limpas = []
    for col in df.columns:
        # Remove BOM e caracteres especiais no início
        match = re.search(r'[A-Za-z0-9_]', col)
        if match:
            col_limpa = col[match.start():]
        else:
            col_limpa = col
        colunas_limpas.append(col_limpa.strip())
    df.columns = colunas_limpas
    
    print(f"✅ Arquivo lido com sucesso: {len(df)} registros")
    print(f"📋 Colunas: {list(df.columns)}")
    
    # Limpar dados
    df['Num_CNES'] = df['Num_CNES'].astype(str).str.strip().str.zfill(7)
    df['Nome_estabelecimento'] = df['Nome_estabelecimento'].str.strip()
    df['Categoria'] = df['Categoria'].str.strip().str.upper()
    
    # Criar tabela no banco
    with engine_papa.connect() as conn:
        # Drop e create table
        print("🔧 Criando tabela categoria_unidade...")
        conn.execute(text("""
            DROP TABLE IF EXISTS categoria_unidade CASCADE;
            
            CREATE TABLE categoria_unidade (
                codigo_unidade VARCHAR(7) PRIMARY KEY,
                nome_estabelecimento TEXT,
                categoria VARCHAR(100) NOT NULL
            );
            
            COMMENT ON TABLE categoria_unidade IS 'Mapeamento de unidades de saúde por categoria (UPA, HOSPITAL, SAMU, etc.)';
        """))
        conn.commit()
        
        # Inserir dados
        print(f"💾 Inserindo {len(df)} registros...")
        for _, row in df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO categoria_unidade (codigo_unidade, nome_estabelecimento, categoria)
                    VALUES (:cnes, :nome, :categoria)
                    ON CONFLICT (codigo_unidade) DO UPDATE
                    SET nome_estabelecimento = EXCLUDED.nome_estabelecimento,
                        categoria = EXCLUDED.categoria
                """),
                {
                    'cnes': row['Num_CNES'],
                    'nome': row['Nome_estabelecimento'],
                    'categoria': row['Categoria']
                }
            )
        conn.commit()
        
        # Verificar
        result = conn.execute(text("SELECT COUNT(*) as total FROM categoria_unidade"))
        total = result.fetchone()[0]
        print(f"✅ Importação concluída! Total de registros: {total}")
        
        # Mostrar distribuição por categoria
        result = conn.execute(text("""
            SELECT categoria, COUNT(*) as total
            FROM categoria_unidade
            GROUP BY categoria
            ORDER BY categoria
        """))
        print("\n📊 Distribuição por categoria:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} unidades")
        
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("IMPORTAÇÃO DE CATEGORIAS DO FILTRO_CATEGORIA.CSV")
    print("=" * 60)
    importar_categorias()
