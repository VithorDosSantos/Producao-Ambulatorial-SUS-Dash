-- ============================================================
-- Script de Criação do Banco de Dados - Sistema de Espelho de Unidades
-- Baseado no arquivo: espelhoUnidades-2501.csv
-- Data: 12/12/2025
-- ============================================================

-- Criar banco de dados (descomente se necessário criar o banco)
-- CREATE DATABASE espelho_unidades;
-- \c espelho_unidades;

-- ============================================================
-- TABELA: financiamentos
-- Descrição: Armazena os tipos de financiamento (MAC, etc)
-- ============================================================
CREATE TABLE financiamentos (
    id_financiamento SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    descricao VARCHAR(255),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA: estabelecimentos
-- Descrição: Armazena informações dos estabelecimentos de saúde
-- ============================================================
CREATE TABLE estabelecimentos (
    id_estabelecimento SERIAL PRIMARY KEY,
    num_cnes VARCHAR(20) UNIQUE NOT NULL,
    nome_estabelecimento VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA: procedimentos
-- Descrição: Armazena os procedimentos médicos/de saúde
-- ============================================================
CREATE TABLE procedimentos (
    id_procedimento SERIAL PRIMARY KEY,
    codigo_procedimento VARCHAR(20) UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    tipo_apuracao VARCHAR(50), -- 'Proced.', 'Sub-Grupo', etc
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA: competencias
-- Descrição: Armazena os períodos de competência (ano/mês)
-- ============================================================
CREATE TABLE competencias (
    id_competencia SERIAL PRIMARY KEY,
    competencia VARCHAR(6) UNIQUE NOT NULL, -- YYYYMM (202506)
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_mes CHECK (mes BETWEEN 1 AND 12),
    CONSTRAINT chk_ano CHECK (ano BETWEEN 2000 AND 2100)
);

-- ============================================================
-- TABELA: orcamentos_procedimentos
-- Descrição: Tabela principal que armazena os orçamentos dos procedimentos
-- por estabelecimento e competência (dados do CSV)
-- ============================================================
CREATE TABLE orcamentos_procedimentos (
    id_orcamento SERIAL PRIMARY KEY,
    id_financiamento INTEGER NOT NULL,
    id_procedimento INTEGER NOT NULL,
    id_estabelecimento INTEGER NOT NULL,
    id_competencia INTEGER NOT NULL,
    
    -- Dados físicos e financeiros
    quantidade_fisica INTEGER DEFAULT 0,
    valor_medio_unitario NUMERIC(12, 2) DEFAULT 0.00,
    valor_orcamentario NUMERIC(12, 2) DEFAULT 0.00,
    percentual_incremento NUMERIC(5, 2) DEFAULT 0.00,
    valor_incremento NUMERIC(12, 2) DEFAULT 0.00,
    total_orcado NUMERIC(12, 2) DEFAULT 0.00,
    
    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_criacao VARCHAR(100),
    usuario_atualizacao VARCHAR(100),
    
    -- Chaves estrangeiras
    CONSTRAINT fk_financiamento FOREIGN KEY (id_financiamento) 
        REFERENCES financiamentos(id_financiamento) ON DELETE RESTRICT,
    CONSTRAINT fk_procedimento FOREIGN KEY (id_procedimento) 
        REFERENCES procedimentos(id_procedimento) ON DELETE RESTRICT,
    CONSTRAINT fk_estabelecimento FOREIGN KEY (id_estabelecimento) 
        REFERENCES estabelecimentos(id_estabelecimento) ON DELETE RESTRICT,
    CONSTRAINT fk_competencia FOREIGN KEY (id_competencia) 
        REFERENCES competencias(id_competencia) ON DELETE RESTRICT,
    
    -- Constraint de unicidade
    CONSTRAINT uk_orcamento UNIQUE (id_financiamento, id_procedimento, id_estabelecimento, id_competencia),
    
    -- Checks de validação
    CONSTRAINT chk_quantidade_fisica CHECK (quantidade_fisica >= 0),
    CONSTRAINT chk_valor_medio_unitario CHECK (valor_medio_unitario >= 0),
    CONSTRAINT chk_valor_orcamentario CHECK (valor_orcamentario >= 0),
    CONSTRAINT chk_percentual_incremento CHECK (percentual_incremento >= 0),
    CONSTRAINT chk_total_orcado CHECK (total_orcado >= 0)
);

-- ============================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================

-- Índices na tabela orcamentos_procedimentos
CREATE INDEX idx_orcamento_financiamento ON orcamentos_procedimentos(id_financiamento);
CREATE INDEX idx_orcamento_procedimento ON orcamentos_procedimentos(id_procedimento);
CREATE INDEX idx_orcamento_estabelecimento ON orcamentos_procedimentos(id_estabelecimento);
CREATE INDEX idx_orcamento_competencia ON orcamentos_procedimentos(id_competencia);
CREATE INDEX idx_orcamento_data_criacao ON orcamentos_procedimentos(data_criacao);

-- Índices nas tabelas de lookup
CREATE INDEX idx_estabelecimento_cnes ON estabelecimentos(num_cnes);
CREATE INDEX idx_procedimento_codigo ON procedimentos(codigo_procedimento);
CREATE INDEX idx_competencia_ano_mes ON competencias(ano, mes);

-- ============================================================
-- FUNÇÕES E TRIGGERS
-- ============================================================

-- Função para atualizar o campo data_atualizacao automaticamente
CREATE OR REPLACE FUNCTION atualizar_data_atualizacao()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualização automática
CREATE TRIGGER trigger_estabelecimento_atualizacao
    BEFORE UPDATE ON estabelecimentos
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_data_atualizacao();

CREATE TRIGGER trigger_procedimento_atualizacao
    BEFORE UPDATE ON procedimentos
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_data_atualizacao();

CREATE TRIGGER trigger_orcamento_atualizacao
    BEFORE UPDATE ON orcamentos_procedimentos
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_data_atualizacao();

-- ============================================================
-- VIEWS ÚTEIS PARA CONSULTAS
-- ============================================================

-- View com todos os dados consolidados (similar ao CSV original)
CREATE OR REPLACE VIEW vw_orcamentos_completo AS
SELECT 
    f.codigo as financiamento,
    p.codigo_procedimento,
    p.descricao as descricao_procedimento,
    o.quantidade_fisica,
    o.valor_medio_unitario,
    o.valor_orcamentario,
    o.percentual_incremento,
    o.valor_incremento,
    o.total_orcado,
    p.tipo_apuracao,
    c.competencia,
    e.num_cnes,
    e.nome_estabelecimento,
    o.data_criacao,
    o.data_atualizacao
FROM orcamentos_procedimentos o
INNER JOIN financiamentos f ON o.id_financiamento = f.id_financiamento
INNER JOIN procedimentos p ON o.id_procedimento = p.id_procedimento
INNER JOIN estabelecimentos e ON o.id_estabelecimento = e.id_estabelecimento
INNER JOIN competencias c ON o.id_competencia = c.id_competencia;

-- View de resumo por estabelecimento
CREATE OR REPLACE VIEW vw_resumo_por_estabelecimento AS
SELECT 
    e.num_cnes,
    e.nome_estabelecimento,
    c.competencia,
    COUNT(DISTINCT o.id_procedimento) as total_procedimentos,
    SUM(o.quantidade_fisica) as total_quantidade,
    SUM(o.total_orcado) as total_orcamento
FROM orcamentos_procedimentos o
INNER JOIN estabelecimentos e ON o.id_estabelecimento = e.id_estabelecimento
INNER JOIN competencias c ON o.id_competencia = c.id_competencia
GROUP BY e.num_cnes, e.nome_estabelecimento, c.competencia;

-- View de resumo por procedimento
CREATE OR REPLACE VIEW vw_resumo_por_procedimento AS
SELECT 
    p.codigo_procedimento,
    p.descricao,
    p.tipo_apuracao,
    c.competencia,
    COUNT(DISTINCT o.id_estabelecimento) as total_estabelecimentos,
    SUM(o.quantidade_fisica) as total_quantidade,
    AVG(o.valor_medio_unitario) as media_valor_unitario,
    SUM(o.total_orcado) as total_orcamento
FROM orcamentos_procedimentos o
INNER JOIN procedimentos p ON o.id_procedimento = p.id_procedimento
INNER JOIN competencias c ON o.id_competencia = c.id_competencia
GROUP BY p.codigo_procedimento, p.descricao, p.tipo_apuracao, c.competencia;

-- View de resumo financeiro por competência
CREATE OR REPLACE VIEW vw_resumo_financeiro_competencia AS
SELECT 
    c.competencia,
    c.ano,
    c.mes,
    f.codigo as financiamento,
    COUNT(DISTINCT o.id_estabelecimento) as total_estabelecimentos,
    COUNT(DISTINCT o.id_procedimento) as total_procedimentos,
    SUM(o.quantidade_fisica) as total_quantidade,
    SUM(o.total_orcado) as total_orcamento
FROM orcamentos_procedimentos o
INNER JOIN competencias c ON o.id_competencia = c.id_competencia
INNER JOIN financiamentos f ON o.id_financiamento = f.id_financiamento
GROUP BY c.competencia, c.ano, c.mes, f.codigo;

-- ============================================================
-- FUNÇÕES AUXILIARES PARA IMPORTAÇÃO DE DADOS
-- ============================================================

-- Função para obter ou criar financiamento
CREATE OR REPLACE FUNCTION obter_ou_criar_financiamento(p_codigo VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id_financiamento INTO v_id FROM financiamentos WHERE codigo = p_codigo;
    
    IF v_id IS NULL THEN
        INSERT INTO financiamentos (codigo) VALUES (p_codigo) RETURNING id_financiamento INTO v_id;
    END IF;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Função para obter ou criar estabelecimento
CREATE OR REPLACE FUNCTION obter_ou_criar_estabelecimento(p_cnes VARCHAR, p_nome VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id_estabelecimento INTO v_id FROM estabelecimentos WHERE num_cnes = p_cnes;
    
    IF v_id IS NULL THEN
        INSERT INTO estabelecimentos (num_cnes, nome_estabelecimento) 
        VALUES (p_cnes, p_nome) RETURNING id_estabelecimento INTO v_id;
    ELSE
        UPDATE estabelecimentos SET nome_estabelecimento = p_nome WHERE id_estabelecimento = v_id;
    END IF;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Função para obter ou criar procedimento
CREATE OR REPLACE FUNCTION obter_ou_criar_procedimento(p_codigo VARCHAR, p_descricao TEXT, p_tipo_apuracao VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id_procedimento INTO v_id FROM procedimentos WHERE codigo_procedimento = p_codigo;
    
    IF v_id IS NULL THEN
        INSERT INTO procedimentos (codigo_procedimento, descricao, tipo_apuracao) 
        VALUES (p_codigo, p_descricao, p_tipo_apuracao) RETURNING id_procedimento INTO v_id;
    ELSE
        UPDATE procedimentos 
        SET descricao = p_descricao, tipo_apuracao = p_tipo_apuracao 
        WHERE id_procedimento = v_id;
    END IF;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Função para obter ou criar competência
CREATE OR REPLACE FUNCTION obter_ou_criar_competencia(p_competencia VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
    v_ano INTEGER;
    v_mes INTEGER;
BEGIN
    SELECT id_competencia INTO v_id FROM competencias WHERE competencia = p_competencia;
    
    IF v_id IS NULL THEN
        v_ano := SUBSTRING(p_competencia, 1, 4)::INTEGER;
        v_mes := SUBSTRING(p_competencia, 5, 2)::INTEGER;
        
        INSERT INTO competencias (competencia, ano, mes) 
        VALUES (p_competencia, v_ano, v_mes) RETURNING id_competencia INTO v_id;
    END IF;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- COMENTÁRIOS NAS TABELAS (DOCUMENTATION)
-- ============================================================

COMMENT ON TABLE financiamentos IS 'Tipos de financiamento dos procedimentos (MAC, etc)';
COMMENT ON TABLE estabelecimentos IS 'Estabelecimentos de saúde cadastrados no CNES';
COMMENT ON TABLE procedimentos IS 'Procedimentos médicos e de saúde disponíveis';
COMMENT ON TABLE competencias IS 'Períodos de competência para orçamento (ano/mês)';
COMMENT ON TABLE orcamentos_procedimentos IS 'Orçamentos dos procedimentos por estabelecimento e competência';

COMMENT ON COLUMN orcamentos_procedimentos.quantidade_fisica IS 'Quantidade física do procedimento';
COMMENT ON COLUMN orcamentos_procedimentos.valor_medio_unitario IS 'Valor médio unitário do procedimento';
COMMENT ON COLUMN orcamentos_procedimentos.valor_orcamentario IS 'Valor orçamentário total';
COMMENT ON COLUMN orcamentos_procedimentos.percentual_incremento IS 'Percentual de incremento aplicado';
COMMENT ON COLUMN orcamentos_procedimentos.valor_incremento IS 'Valor do incremento';
COMMENT ON COLUMN orcamentos_procedimentos.total_orcado IS 'Valor total orçado (orçamentário + incremento)';

-- ============================================================
-- DADOS INICIAIS (EXEMPLO)
-- ============================================================

-- Inserir financiamento MAC se não existir
INSERT INTO financiamentos (codigo, descricao) 
VALUES ('MAC', 'Média e Alta Complexidade')
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================
-- SCRIPT DE VERIFICAÇÃO
-- ============================================================

-- Verificar estrutura criada
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Banco de dados criado com sucesso!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tabelas criadas:';
    RAISE NOTICE '  - financiamentos';
    RAISE NOTICE '  - estabelecimentos';
    RAISE NOTICE '  - procedimentos';
    RAISE NOTICE '  - competencias';
    RAISE NOTICE '  - orcamentos_procedimentos';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Views criadas:';
    RAISE NOTICE '  - vw_orcamentos_completo';
    RAISE NOTICE '  - vw_resumo_por_estabelecimento';
    RAISE NOTICE '  - vw_resumo_por_procedimento';
    RAISE NOTICE '  - vw_resumo_financeiro_competencia';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Pronto para importar dados!';
    RAISE NOTICE '========================================';
END $$;

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
