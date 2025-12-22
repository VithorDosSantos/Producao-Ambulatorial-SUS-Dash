"""
Script para criar índices no banco de dados e melhorar performance
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database_service import engine_papa
import sqlalchemy as sa

def create_indexes():
    """Cria índices nas tabelas principais para melhorar performance"""
    
    indexes = [
        # Índices individuais
        "CREATE INDEX IF NOT EXISTS idx_atendimento_competencia ON atendimento(competencia)",
        "CREATE INDEX IF NOT EXISTS idx_atendimento_codigo_unidade ON atendimento(codigo_unidade)",
        "CREATE INDEX IF NOT EXISTS idx_atendimento_codigo_procedimento ON atendimento(codigo_procedimento)",
        "CREATE INDEX IF NOT EXISTS idx_atendimento_comp_unid ON atendimento(competencia, codigo_unidade)",
        
        # Índices para JOINs
        "CREATE INDEX IF NOT EXISTS idx_unidade_saude_codigo ON unidade_saude(codigo_unidade)",
        "CREATE INDEX IF NOT EXISTS idx_unidade_saude_natureza ON unidade_saude(natureza_juridica)",
        "CREATE INDEX IF NOT EXISTS idx_procedimento_codigo ON procedimento(codigo_procedimento)",
        "CREATE INDEX IF NOT EXISTS idx_municipio_codigo ON municipio(codigo_municipio)",
        
        # Índice composto
        "CREATE INDEX IF NOT EXISTS idx_atendimento_complete ON atendimento(competencia, codigo_unidade, codigo_procedimento)"
    ]
    
    print("🔧 Criando índices no banco de dados...")
    
    try:
        with engine_papa.connect() as conn:
            for idx_query in indexes:
                print(f"  • Executando: {idx_query[:80]}...")
                conn.execute(sa.text(idx_query))
                conn.commit()
            
            # Analyze para atualizar estatísticas
            print("\n📊 Atualizando estatísticas do PostgreSQL...")
            conn.execute(sa.text("ANALYZE atendimento"))
            conn.execute(sa.text("ANALYZE unidade_saude"))
            conn.execute(sa.text("ANALYZE procedimento"))
            conn.execute(sa.text("ANALYZE municipio"))
            conn.commit()
            
        print("\n✅ Índices criados com sucesso!")
        print("📈 As queries agora devem ser significativamente mais rápidas!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao criar índices: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_indexes()
    sys.exit(0 if success else 1)
