"""
Script para recriar as views materializadas com a categoria de tipo de unidade
"""
import os
from sqlalchemy import text
from app.database import engine_papa

def recreate_views():
    """Recria as views materializadas"""
    
    # Caminho para o arquivo SQL
    sql_path = os.path.join(os.path.dirname(__file__), 'create_views.sql')
    
    if not os.path.exists(sql_path):
        print(f"❌ Arquivo não encontrado: {sql_path}")
        return False
    
    # Ler SQL
    print(f"📁 Lendo arquivo: {sql_path}")
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Executar SQL
    with engine_papa.connect() as conn:
        print("🔧 Recriando views materializadas...")
        print("⏳ Isso pode levar alguns minutos...")
        
        # Executar o script completo
        conn.execute(text(sql_script))
        conn.commit()
        
        print("✅ Views materializadas recriadas com sucesso!")
        
        # Verificar tamanho das views
        result = conn.execute(text("""
            SELECT 
                schemaname,
                matviewname as view_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
            FROM pg_matviews
            WHERE matviewname LIKE 'mv_%'
            ORDER BY matviewname
        """))
        
        print("\n📊 Views materializadas:")
        for row in result:
            print(f"  - {row[1]}: {row[2]}")
        
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("RECRIAÇÃO DAS VIEWS MATERIALIZADAS")
    print("=" * 60)
    recreate_views()
