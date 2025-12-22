-- =============================================
-- Script de Criação do Banco de Dados SIASUS
-- Sistema de Informações Ambulatoriais do SUS
-- =============================================

-- Criar o banco de dados
CREATE DATABASE siasus_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Portuguese_Brazil.1252'
    LC_CTYPE = 'Portuguese_Brazil.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE siasus_db IS 'Banco de dados para armazenamento de informações ambulatoriais do SUS';

-- Conectar ao banco de dados
\c siasus_db;

-- =============================================
-- Tabelas de Domínio/Referência
-- =============================================

-- Tabela de Municípios
CREATE TABLE municipio (
    codigo_municipio VARCHAR(6) PRIMARY KEY,
    nome_municipio VARCHAR(100),
    uf CHAR(2),
    codigo_regiao VARCHAR(10)
);

COMMENT ON TABLE municipio IS 'Municípios brasileiros';
COMMENT ON COLUMN municipio.codigo_municipio IS 'Código IBGE do município';

-- Tabela de Unidades de Saúde
CREATE TABLE unidade_saude (
    codigo_unidade VARCHAR(7) PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL,
    codigo_municipio VARCHAR(6) NOT NULL,
    tipo_gestao CHAR(2),
    condicao_estabelecimento CHAR(2),
    tipo_unidade VARCHAR(2),
    tipo_prestador VARCHAR(2),
    natureza_juridica VARCHAR(4),
    FOREIGN KEY (codigo_municipio) REFERENCES municipio(codigo_municipio)
);

COMMENT ON TABLE unidade_saude IS 'Unidades de saúde prestadoras de serviço';
COMMENT ON COLUMN unidade_saude.cnpj IS 'CNPJ da unidade de saúde';

-- Tabela de CBO (Classificação Brasileira de Ocupações)
CREATE TABLE cbo (
    codigo_cbo VARCHAR(6) PRIMARY KEY,
    descricao_cbo VARCHAR(200)
);

COMMENT ON TABLE cbo IS 'Classificação Brasileira de Ocupações';

-- Tabela de CID (Classificação Internacional de Doenças)
CREATE TABLE cid (
    codigo_cid VARCHAR(4) PRIMARY KEY,
    descricao_cid VARCHAR(200)
);

COMMENT ON TABLE cid IS 'Classificação Internacional de Doenças - CID10';

-- Tabela de Procedimentos
CREATE TABLE procedimento (
    codigo_procedimento VARCHAR(10) PRIMARY KEY,
    ultimo_digito CHAR(1),
    descricao_procedimento VARCHAR(300),
    tipo_financiamento VARCHAR(2),
    subtipo_financiamento VARCHAR(4),
    complexidade VARCHAR(2)
);

COMMENT ON TABLE procedimento IS 'Procedimentos ambulatoriais do SUS';

-- Tabela de Profissionais de Saúde
CREATE TABLE profissional (
    cns_profissional VARCHAR(15) PRIMARY KEY,
    codigo_cbo VARCHAR(6),
    FOREIGN KEY (codigo_cbo) REFERENCES cbo(codigo_cbo)
);

COMMENT ON TABLE profissional IS 'Profissionais de saúde que realizam atendimentos';
COMMENT ON COLUMN profissional.cns_profissional IS 'Cartão Nacional de Saúde do profissional';

-- =============================================
-- Tabela Principal - Atendimentos
-- =============================================

CREATE TABLE atendimento (
    id_atendimento SERIAL PRIMARY KEY,
    
    -- Dados da Unidade
    codigo_unidade VARCHAR(7) NOT NULL,
    cnpj_mantenedora VARCHAR(14),
    cnpj_contratado VARCHAR(14),
    
    -- Dados Temporais
    ano_mes_movimento VARCHAR(6) NOT NULL,
    competencia VARCHAR(6) NOT NULL,
    
    -- Dados do Procedimento
    codigo_procedimento VARCHAR(10) NOT NULL,
    
    -- Dados do Profissional
    cns_profissional VARCHAR(15),
    
    -- Dados do Paciente
    idade INTEGER,
    idade_minima INTEGER,
    idade_maxima INTEGER,
    faixa_idade CHAR(1),
    sexo CHAR(1),
    raca_cor VARCHAR(2),
    codigo_municipio_paciente VARCHAR(6),
    etnia VARCHAR(4),
    
    -- Dados Clínicos
    cid_principal VARCHAR(4),
    cid_secundario VARCHAR(4),
    cid_causas VARCHAR(4),
    carater_atendimento VARCHAR(2),
    
    -- Dados de Saída
    motivo_saida VARCHAR(2),
    obito SMALLINT DEFAULT 0,
    encerramento SMALLINT DEFAULT 0,
    permanencia SMALLINT DEFAULT 0,
    alta SMALLINT DEFAULT 0,
    transferencia SMALLINT DEFAULT 0,
    
    -- Dados Administrativos
    origem_documento CHAR(1),
    autorizacao VARCHAR(13),
    
    -- Dados de Quantidades e Valores
    quantidade_produzida INTEGER NOT NULL,
    quantidade_aprovada INTEGER NOT NULL,
    valor_procedimento DECIMAL(10, 2),
    valor_aprovado DECIMAL(10, 2),
    
    -- Dados de Diferença
    uf_diferenca SMALLINT DEFAULT 0,
    municipio_diferenca SMALLINT DEFAULT 0,
    valor_diferenca DECIMAL(10, 2) DEFAULT 0,
    
    -- Totalizadores
    numero_vpa_total DECIMAL(10, 2),
    numero_pa_total DECIMAL(10, 2),
    
    -- Dados Adicionais
    indicacao VARCHAR(1),
    codigo_ocorrencia VARCHAR(2),
    flag_quantidade CHAR(1),
    flag_erro CHAR(1),
    valor_complemento_federal DECIMAL(10, 2) DEFAULT 0,
    valor_complemento_local DECIMAL(10, 2) DEFAULT 0,
    valor_incremento DECIMAL(10, 2) DEFAULT 0,
    codigo_servico CHAR(1),
    codigo_ine VARCHAR(10),
    
    -- Campos de Controle
    nivel_complexidade VARCHAR(1),
    tipo_recurso_financiamento CHAR(1),
    regiao_contrato VARCHAR(4),
    incremento_outros VARCHAR(4),
    incremento_urgencia VARCHAR(4),
    
    -- Foreign Keys
    FOREIGN KEY (codigo_unidade) REFERENCES unidade_saude(codigo_unidade),
    FOREIGN KEY (codigo_procedimento) REFERENCES procedimento(codigo_procedimento),
    FOREIGN KEY (cns_profissional) REFERENCES profissional(cns_profissional),
    FOREIGN KEY (codigo_municipio_paciente) REFERENCES municipio(codigo_municipio),
    FOREIGN KEY (cid_principal) REFERENCES cid(codigo_cid),
    FOREIGN KEY (cid_secundario) REFERENCES cid(codigo_cid),
    FOREIGN KEY (cid_causas) REFERENCES cid(codigo_cid)
);

COMMENT ON TABLE atendimento IS 'Registro de atendimentos ambulatoriais realizados';
COMMENT ON COLUMN atendimento.ano_mes_movimento IS 'Ano e mês do movimento (YYYYMM)';
COMMENT ON COLUMN atendimento.competencia IS 'Competência do procedimento (YYYYMM)';

-- =============================================
-- Índices para Melhorar Performance
-- =============================================

CREATE INDEX idx_atendimento_unidade ON atendimento(codigo_unidade);
CREATE INDEX idx_atendimento_procedimento ON atendimento(codigo_procedimento);
CREATE INDEX idx_atendimento_profissional ON atendimento(cns_profissional);
CREATE INDEX idx_atendimento_municipio ON atendimento(codigo_municipio_paciente);
CREATE INDEX idx_atendimento_competencia ON atendimento(competencia);
CREATE INDEX idx_atendimento_data ON atendimento(ano_mes_movimento);
CREATE INDEX idx_atendimento_cid_principal ON atendimento(cid_principal);
CREATE INDEX idx_unidade_municipio ON unidade_saude(codigo_municipio);
CREATE INDEX idx_atendimento_sexo ON atendimento(sexo);
CREATE INDEX idx_atendimento_raca ON atendimento(raca_cor);

-- =============================================
-- Views Úteis
-- =============================================

-- View de resumo de atendimentos por unidade
CREATE OR REPLACE VIEW vw_atendimentos_por_unidade AS
SELECT 
    u.codigo_unidade,
    u.cnpj,
    m.nome_municipio,
    COUNT(a.id_atendimento) as total_atendimentos,
    SUM(a.quantidade_aprovada) as total_quantidade,
    SUM(a.valor_aprovado) as total_valor
FROM atendimento a
INNER JOIN unidade_saude u ON a.codigo_unidade = u.codigo_unidade
INNER JOIN municipio m ON u.codigo_municipio = m.codigo_municipio
GROUP BY u.codigo_unidade, u.cnpj, m.nome_municipio;

-- View de atendimentos por procedimento
CREATE OR REPLACE VIEW vw_atendimentos_por_procedimento AS
SELECT 
    p.codigo_procedimento,
    p.descricao_procedimento,
    COUNT(a.id_atendimento) as total_atendimentos,
    SUM(a.quantidade_aprovada) as total_quantidade,
    SUM(a.valor_aprovado) as total_valor
FROM atendimento a
INNER JOIN procedimento p ON a.codigo_procedimento = p.codigo_procedimento
GROUP BY p.codigo_procedimento, p.descricao_procedimento;

-- View de atendimentos por CID
CREATE OR REPLACE VIEW vw_atendimentos_por_cid AS
SELECT 
    c.codigo_cid,
    c.descricao_cid,
    COUNT(a.id_atendimento) as total_atendimentos
FROM atendimento a
INNER JOIN cid c ON a.cid_principal = c.codigo_cid
WHERE a.cid_principal IS NOT NULL AND a.cid_principal != '0000'
GROUP BY c.codigo_cid, c.descricao_cid;

-- View de perfil demográfico dos atendimentos
CREATE OR REPLACE VIEW vw_perfil_demografico AS
SELECT 
    a.sexo,
    a.raca_cor,
    CASE 
        WHEN a.idade < 1 THEN '0-1 ano'
        WHEN a.idade BETWEEN 1 AND 4 THEN '1-4 anos'
        WHEN a.idade BETWEEN 5 AND 9 THEN '5-9 anos'
        WHEN a.idade BETWEEN 10 AND 14 THEN '10-14 anos'
        WHEN a.idade BETWEEN 15 AND 19 THEN '15-19 anos'
        WHEN a.idade BETWEEN 20 AND 29 THEN '20-29 anos'
        WHEN a.idade BETWEEN 30 AND 39 THEN '30-39 anos'
        WHEN a.idade BETWEEN 40 AND 49 THEN '40-49 anos'
        WHEN a.idade BETWEEN 50 AND 59 THEN '50-59 anos'
        WHEN a.idade BETWEEN 60 AND 69 THEN '60-69 anos'
        WHEN a.idade >= 70 THEN '70+ anos'
        ELSE 'Não informado'
    END as faixa_etaria,
    COUNT(*) as total_atendimentos
FROM atendimento a
GROUP BY a.sexo, a.raca_cor, faixa_etaria;

COMMENT ON VIEW vw_atendimentos_por_unidade IS 'Resumo de atendimentos agrupados por unidade de saúde';
COMMENT ON VIEW vw_atendimentos_por_procedimento IS 'Resumo de atendimentos agrupados por tipo de procedimento';
COMMENT ON VIEW vw_atendimentos_por_cid IS 'Resumo de atendimentos agrupados por diagnóstico principal';
COMMENT ON VIEW vw_perfil_demografico IS 'Perfil demográfico dos pacientes atendidos';
