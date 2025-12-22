-- ===================================================================
-- VIEWS MATERIALIZADAS PARA ACELERAR O DASHBOARD
-- Execute este script no banco PAPA (siasus_db)
-- ===================================================================

-- 1. VIEW MATERIALIZADA: Dados consolidados de produção (já com JOINs)
DROP MATERIALIZED VIEW IF EXISTS mv_producao_consolidada CASCADE;

CREATE MATERIALIZED VIEW mv_producao_consolidada AS
SELECT 
    a.id_atendimento,
    a.codigo_unidade as cnes_key,
    a.competencia,
    u.cnpj,
    a.codigo_unidade as unidade,
    u.natureza_juridica,
    a.codigo_procedimento,
    p.descricao_procedimento,
    CASE 
        WHEN p.complexidade = '01' THEN 'ATENÇÃO BÁSICA'
        WHEN p.complexidade = '02' THEN 'MÉDIA COMPLEXIDADE'
        WHEN p.complexidade = '03' THEN 'ALTA COMPLEXIDADE'
        ELSE 'OUTROS'
    END as categoria,
    a.quantidade_aprovada,
    a.valor_aprovado,
    a.quantidade_produzida,
    a.valor_procedimento,
    -- Campos calculados para acelerar agregações
    DATE_PART('year', TO_DATE(a.competencia, 'YYYYMM')) as ano,
    DATE_PART('month', TO_DATE(a.competencia, 'YYYYMM')) as mes,
    TO_CHAR(TO_DATE(a.competencia, 'YYYYMM'), 'Month/YYYY') as mes_nome
FROM atendimento a
INNER JOIN unidade_saude u ON a.codigo_unidade = u.codigo_unidade
INNER JOIN procedimento p ON a.codigo_procedimento = p.codigo_procedimento
WHERE u.natureza_juridica = '1031';

-- Índices na view materializada para queries rápidas
CREATE INDEX idx_mv_producao_competencia ON mv_producao_consolidada(competencia);
CREATE INDEX idx_mv_producao_cnes ON mv_producao_consolidada(cnes_key);
CREATE INDEX idx_mv_producao_categoria ON mv_producao_consolidada(categoria);
CREATE INDEX idx_mv_producao_comp_cnes ON mv_producao_consolidada(competencia, cnes_key);

-- 2. VIEW MATERIALIZADA: KPIs agregados por competência e unidade
DROP MATERIALIZED VIEW IF EXISTS mv_kpis_agregados CASCADE;

CREATE MATERIALIZED VIEW mv_kpis_agregados AS
SELECT 
    competencia,
    cnes_key,
    unidade,
    categoria,
    COUNT(*) as total_atendimentos,
    SUM(quantidade_aprovada) as qtd_total_aprovada,
    SUM(valor_aprovado) as valor_total_aprovado,
    SUM(quantidade_produzida) as qtd_total_produzida,
    SUM(valor_procedimento) as valor_total_procedimento,
    AVG(valor_aprovado) as valor_medio_procedimento
FROM mv_producao_consolidada
GROUP BY competencia, cnes_key, unidade, categoria;

-- Índices para agregações rápidas
CREATE INDEX idx_mv_kpis_competencia ON mv_kpis_agregados(competencia);
CREATE INDEX idx_mv_kpis_cnes ON mv_kpis_agregados(cnes_key);
CREATE INDEX idx_mv_kpis_categoria ON mv_kpis_agregados(categoria);

-- 3. VIEW MATERIALIZADA: Tendência mensal (já pré-calculada)
DROP MATERIALIZED VIEW IF EXISTS mv_tendencia_mensal CASCADE;

CREATE MATERIALIZED VIEW mv_tendencia_mensal AS
SELECT 
    competencia,
    mes_nome,
    ano,
    mes,
    SUM(quantidade_aprovada) as producao_total,
    SUM(valor_aprovado) as valor_total,
    COUNT(DISTINCT cnes_key) as unidades_ativas,
    COUNT(*) as total_procedimentos
FROM mv_producao_consolidada
GROUP BY competencia, mes_nome, ano, mes
ORDER BY ano, mes;

-- Índice para ordenação rápida
CREATE INDEX idx_mv_tendencia_comp ON mv_tendencia_mensal(competencia);

-- Atualizar estatísticas
ANALYZE mv_producao_consolidada;
ANALYZE mv_kpis_agregados;
ANALYZE mv_tendencia_mensal;

-- Verificar tamanho das views
SELECT 
    schemaname,
    matviewname as view_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
FROM pg_matviews
WHERE matviewname LIKE 'mv_%'
ORDER BY matviewname;

SELECT '✅ Views materializadas criadas com sucesso!' as status;
SELECT '⚡ Dashboard agora vai carregar 10-100x mais rápido!' as info;
