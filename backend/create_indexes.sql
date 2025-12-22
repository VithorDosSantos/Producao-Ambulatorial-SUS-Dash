-- Script para criar índices e acelerar queries do Dashboard
-- Execute este script no banco PAPA (siasus_db)

-- Índices para acelerar queries na tabela atendimento
CREATE INDEX IF NOT EXISTS idx_atendimento_competencia ON atendimento(competencia);
CREATE INDEX IF NOT EXISTS idx_atendimento_codigo_unidade ON atendimento(codigo_unidade);
CREATE INDEX IF NOT EXISTS idx_atendimento_codigo_procedimento ON atendimento(codigo_procedimento);
CREATE INDEX IF NOT EXISTS idx_atendimento_comp_unid ON atendimento(competencia, codigo_unidade);

-- Índices para acelerar JOINs
CREATE INDEX IF NOT EXISTS idx_unidade_saude_codigo ON unidade_saude(codigo_unidade);
CREATE INDEX IF NOT EXISTS idx_unidade_saude_natureza ON unidade_saude(natureza_juridica);
CREATE INDEX IF NOT EXISTS idx_procedimento_codigo ON procedimento(codigo_procedimento);
CREATE INDEX IF NOT EXISTS idx_municipio_codigo ON municipio(codigo_municipio);

-- Índice composto para queries mais específicas
CREATE INDEX IF NOT EXISTS idx_atendimento_complete 
ON atendimento(competencia, codigo_unidade, codigo_procedimento);

-- Analyze para atualizar estatísticas do PostgreSQL
ANALYZE atendimento;
ANALYZE unidade_saude;
ANALYZE procedimento;
ANALYZE municipio;

SELECT 'Índices criados com sucesso!' as status;
