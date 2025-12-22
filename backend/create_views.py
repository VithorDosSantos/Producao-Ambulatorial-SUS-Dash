"""
Script para criar e atualizar views materializadas no PostgreSQL
Views materializadas são caches de queries complexas que aceleram muito o acesso
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database_service import engine_papa
import sqlalchemy as sa

def create_materialized_views():
    """Cria views materializadas para acelerar o dashboard"""
    
    print("🏗️  Criando views materializadas...")
    print("⏳ Isso pode levar alguns minutos com 961K registros...\n")
    
    sql_file = os.path.join(os.path.dirname(__file__), 'create_views.sql')
    
    try:
        # Ler arquivo SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir por comando (separado por ponto e vírgula)
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        with engine_papa.connect() as conn:
            for i, cmd in enumerate(commands, 1):
                if cmd:
                    print(f"📝 Executando comando {i}/{len(commands)}...")
                    try:
                        result = conn.execute(sa.text(cmd))
                        conn.commit()
                        
                        # Mostrar resultados de SELECTs
                        if cmd.strip().upper().startswith('SELECT'):
                            rows = result.fetchall()
                            for row in rows:
                                print(f"   {dict(row)}")
                    except Exception as e:
                        if 'does not exist' not in str(e):
                            print(f"   ⚠️  Aviso: {str(e)[:100]}")
            
        print("\n✅ Views materializadas criadas!")
        print("📊 Execute 'py refresh_views.py' para atualizar os dados")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao criar views: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def refresh_views():
    """Atualiza os dados das views materializadas"""
    
    print("\n🔄 Atualizando views materializadas...")
    
    views = [
        'mv_producao_consolidada',
        'mv_kpis_agregados', 
        'mv_tendencia_mensal'
    ]
    
    try:
        with engine_papa.connect() as conn:
            for view in views:
                print(f"  ⏳ Atualizando {view}...")
                conn.execute(sa.text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"))
                conn.commit()
                print(f"  ✅ {view} atualizada")
        
        print("\n✅ Todas as views foram atualizadas!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao atualizar views: {str(e)}")
        # Se CONCURRENTLY falhar, tentar sem (mais lento mas funciona)
        print("⚠️  Tentando atualização sem CONCURRENTLY...")
        try:
            with engine_papa.connect() as conn:
                for view in views:
                    print(f"  ⏳ Atualizando {view}...")
                    conn.execute(sa.text(f"REFRESH MATERIALIZED VIEW {view}"))
                    conn.commit()
                    print(f"  ✅ {view} atualizada")
            print("\n✅ Todas as views foram atualizadas!")
            return True
        except Exception as e2:
            print(f"\n❌ Erro crítico: {str(e2)}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar views materializadas')
    parser.add_argument('--refresh', action='store_true', help='Atualizar views existentes')
    args = parser.parse_args()
    
    if args.refresh:
        success = refresh_views()
    else:
        success = create_materialized_views()
    
    sys.exit(0 if success else 1)
