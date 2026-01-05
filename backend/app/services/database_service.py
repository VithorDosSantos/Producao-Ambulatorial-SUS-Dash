"""
Serviço para consultas aos bancos de dados PAPA e Espelho
"""
import pandas as pd
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging

from ..database import engine_papa, engine_espelho

logger = logging.getLogger(__name__)

class DatabaseService:
    """Serviço centralizado para queries aos bancos"""
    
    @staticmethod
    def get_competencias_disponiveis() -> List[Dict[str, str]]:
        """
        Retorna lista de competências (meses) disponíveis no banco PAPA
        
        Returns:
            Lista de dicts com {'codigo': '202501', 'nome': 'Jan/2025', 'ordem': '202501'}
        """
        query = """
        SELECT DISTINCT 
            competencia as codigo,
            TO_CHAR(TO_DATE(competencia, 'YYYYMM'), 'Mon/YYYY') as nome,
            competencia as ordem
        FROM atendimento
        WHERE competencia IS NOT NULL
        ORDER BY competencia DESC
        """
        
        try:
            df = pd.read_sql(query, engine_papa)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Erro ao buscar competências: {str(e)}")
            return []
    
    @staticmethod
    def get_categorias_disponiveis() -> List[str]:
        """
        Retorna lista de categorias (tipos de unidade) disponíveis
        
        Returns:
            Lista de strings com nomes das categorias (UPA, HOSPITAL, SAMU, etc.)
        """
        query = """
        SELECT DISTINCT categoria
        FROM categoria_unidade
        ORDER BY categoria
        """
        
        try:
            df = pd.read_sql(query, engine_papa)
            return df['categoria'].tolist()
        except Exception as e:
            logger.error(f"Erro ao buscar categorias: {str(e)}")
            # Fallback com categorias padrão do CSV
            return ['CASA ESPECIALIZADA', 'DEPARTAMENTO', 'HOSPITAL', 'SAMU', 'UNIDADE BASICA DE SAUDE', 'UPA']
    
    @staticmethod
    def get_unidades_disponiveis(categorias: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Retorna lista de unidades de saúde disponíveis
        
        Args:
            categorias: Filtro opcional por categorias (tipos de unidade)
            
        Returns:
            Lista de dicts com {'cnes': 'CNES', 'nome': 'Nome da Unidade', 'categoria': 'CATEGORIA'}
        """
        # Buscar unidades com suas categorias
        query = """
        SELECT DISTINCT 
            c.codigo_unidade as cnes,
            c.nome_estabelecimento as nome,
            c.categoria
        FROM categoria_unidade c
        """
        
        # Adiciona filtro de categorias se fornecido
        if categorias and len(categorias) > 0:
            cat_list = "', '".join(categorias)
            query += f" WHERE c.categoria IN ('{cat_list}')"
        
        query += " ORDER BY nome"
        
        try:
            df = pd.read_sql(query, engine_papa)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Erro ao buscar unidades: {str(e)}")
            return []
    
    @staticmethod
    def get_dados_papa_filtrados(
        competencias: List[str],
        categorias: Optional[List[str]] = None,
        unidades: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Busca dados de produção (PAPA) com filtros aplicados
        OTIMIZADO: Usa view materializada mv_producao_consolidada (10-100x mais rápido)
        
        Args:
            competencias: Lista de competências (YYYYMM)
            categorias: Lista de categorias (opcional)
            unidades: Lista de códigos CNES (opcional)
            
        Returns:
            DataFrame com os dados filtrados
        """
        # Query usando VIEW MATERIALIZADA (super rápido!)
        query = """
        SELECT 
            id_atendimento,
            cnes_key as CNES_KEY,
            cnpj,
            mes_nome as MES_NOME,
            codigo_procedimento,
            descricao_procedimento,
            categoria as Categoria,
            quantidade_aprovada as QTD_APROVADA,
            valor_aprovado as Valor_Produzido,
            quantidade_produzida as QTD_APRESENTADA,
            valor_procedimento as Valor_Apresentado_Final,
            unidade as Unidade
        FROM mv_producao_consolidada
        WHERE 1=1
        """
        
        # Adiciona filtro de competências
        if competencias:
            comp_list = "', '".join(competencias)
            query += f" AND competencia IN ('{comp_list}')"
        
        # Adiciona filtro de categorias
        if categorias and len(categorias) > 0:
            cat_list = "', '".join(categorias)
            query += f" AND categoria IN ('{cat_list}')"
        
        # Adiciona filtro de unidades
        if unidades and len(unidades) > 0:
            unid_list = "', '".join(unidades)
            query += f" AND cnes_key IN ('{unid_list}')"
        
        try:
            df = pd.read_sql(query, engine_papa)
            
            # Normalizar nomes das colunas para maiúsculas
            df.columns = ['id_atendimento', 'CNES_KEY', 'cnpj', 'MES_NOME', 'codigo_procedimento', 
                         'descricao_procedimento', 'Categoria', 'QTD_APROVADA', 'Valor_Produzido',
                         'QTD_APRESENTADA', 'Valor_Apresentado_Final', 'Unidade']
            
            return df
        except Exception as e:
            # Se view não existir, usar query tradicional como fallback
            logger.warning(f"View materializada não disponível, usando query tradicional: {str(e)}")
            return DatabaseService._get_dados_papa_fallback(competencias, categorias, unidades)
    
    @staticmethod
    def get_dados_espelho() -> pd.DataFrame:
        """
        Busca dados do teto orçamentário (Espelho)
        
        Returns:
            DataFrame com teto por unidade (CNES)
        """
        query = """
        SELECT 
            e.num_cnes as cnes_key,
            e.nome_estabelecimento as unidade,
            SUM(o.quantidade_fisica) as qtd_teto_fisico,
            SUM(o.total_orcado) as valor_teto
        FROM orcamentos_procedimentos o
        INNER JOIN estabelecimentos e ON o.id_estabelecimento = e.id_estabelecimento
        GROUP BY e.num_cnes, e.nome_estabelecimento
        """
        
        try:
            df = pd.read_sql(query, engine_espelho)
            # Converter colunas para maiúsculas para padronizar com PAPA
            df.columns = ['CNES_KEY', 'Unidade', 'QTD_TETO_FISICO', 'Valor_Teto']
            return df
        except Exception as e:
            logger.error(f"Erro ao buscar dados Espelho: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def get_kpis_aggregated_sql(
        competencias: List[str],
        categorias: Optional[List[str]] = None,
        unidades: Optional[List[str]] = None
    ) -> dict:
        """Retorna KPIs agregados diretamente via SQL nas views materializadas.

        Retorna um dict com chaves compatíveis com `calcular_kpis_globais`.
        """
        # Garante lista de competencias
        if not competencias:
            competencias = [c['codigo'] for c in DatabaseService.get_competencias_disponiveis()]

        comp_filter = "', '".join(competencias)
        query = f"""
        SELECT
            COALESCE(SUM(valor_total_aprovado),0) AS producao_aprovada_valor,
            COALESCE(SUM(qtd_total_aprovada),0) AS producao_aprovada_qtd,
            COALESCE(SUM(valor_total_procedimento),0) AS valor_apresentado_valor,
            COALESCE(SUM(qtd_total_produzida),0) AS producao_apresentada_qtd
        FROM mv_kpis_agregados
        WHERE competencia IN ('{comp_filter}')
        """

        # filtros opcionais
        if categorias and len(categorias) > 0:
            cat_list = "', '".join(categorias)
            query += f" AND categoria IN ('{cat_list}')"
        if unidades and len(unidades) > 0:
            unid_list = "', '".join(unidades)
            query += f" AND cnes_key IN ('{unid_list}')"

        try:
            with engine_papa.connect() as conn:
                res = conn.execute(sa.text(query)).fetchone()
                producao_valor = float(res['producao_aprovada_valor'] or 0)
                producao_qtd = int(res['producao_aprovada_qtd'] or 0)
                apresentado_valor = float(res['valor_apresentado_valor'] or 0)
                apresentado_qtd = int(res['producao_apresentada_qtd'] or 0)

            # Teto: usar dados do espelho (pequeno, ok em memória)
            df_esp = DatabaseService.get_dados_espelho()
            if unidades and len(unidades) > 0:
                df_esp = df_esp[df_esp['CNES_KEY'].isin(unidades)]

            # numero de meses
            num_meses = len(competencias)
            teto_base_valor = float(df_esp['Valor_Teto'].sum()) if not df_esp.empty else 0.0
            teto_total_valor = teto_base_valor * num_meses

            teto_base_qtd = int(df_esp['QTD_TETO_FISICO'].sum()) if not df_esp.empty else 0
            teto_total_qtd = teto_base_qtd * num_meses

            saldo = teto_total_valor - producao_valor
            percentual = (producao_valor / teto_total_valor * 100) if teto_total_valor > 0 else 0

            return {
                'teto_total_valor': float(teto_total_valor),
                'teto_total_qtd': int(teto_total_qtd),
                'producao_aprovada_valor': float(producao_valor),
                'producao_aprovada_qtd': int(producao_qtd),
                'producao_apresentada_valor': float(apresentado_valor),
                'producao_apresentada_qtd': int(apresentado_qtd),
                'saldo': float(saldo),
                'percentual_execucao': float(percentual),
                'saldo_percentual': float(100 - percentual)
            }
        except Exception as e:
            logger.error(f"Erro ao buscar KPIs via SQL: {str(e)}")
            return {}

    @staticmethod
    def get_producao_por_unidade_sql(
        competencias: List[str],
        categorias: Optional[List[str]] = None,
        unidades: Optional[List[str]] = None,
        top_n: int = 10
    ) -> list:
        """Retorna produção agregada por unidade via SQL (top N)."""
        if not competencias:
            competencias = [c['codigo'] for c in DatabaseService.get_competencias_disponiveis()]
        comp_filter = "', '".join(competencias)
        query = f"""
        SELECT cnes_key AS CNES_KEY, unidade AS Unidade,
               SUM(valor_total_aprovado) AS Valor_Produzido,
               SUM(valor_total_procedimento) AS Valor_Apresentado_Final,
               SUM(qtd_total_aprovada) AS QTD_APROVADA,
               SUM(qtd_total_produzida) AS QTD_APRESENTADA
        FROM mv_kpis_agregados
        WHERE competencia IN ('{comp_filter}')
        """
        if categorias and len(categorias) > 0:
            cat_list = "', '".join(categorias)
            query += f" AND categoria IN ('{cat_list}')"
        if unidades and len(unidades) > 0:
            unid_list = "', '".join(unidades)
            query += f" AND cnes_key IN ('{unid_list}')"
        query += "\nGROUP BY cnes_key, unidade\nORDER BY Valor_Produzido DESC\nLIMIT :limit"

        try:
            with engine_papa.connect() as conn:
                result = conn.execute(sa.text(query), {'limit': top_n})
                rows = [dict(r) for r in result.fetchall()]

            # trazer teto do espelho para cálculo de percentual (pequeno)
            df_esp = DatabaseService.get_dados_espelho()
            results = []
            num_meses = len(competencias)
            for r in rows:
                cnes = str(r.get('CNES_KEY'))
                teto_row = df_esp[df_esp['CNES_KEY'] == cnes]
                teto_valor = float(teto_row['Valor_Teto'].sum()) if not teto_row.empty else 0.0
                teto_total = teto_valor * num_meses
                percentual = (r.get('Valor_Produzido', 0) / teto_total * 100) if teto_total > 0 else 0
                results.append({
                    'cnes': cnes,
                    'unidade': r.get('Unidade'),
                    'valor_producao': float(r.get('Valor_Produzido', 0)),
                    'valor_apresentado': float(r.get('Valor_Apresentado_Final', 0)),
                    'qtd_aprovada': int(r.get('QTD_APROVADA', 0)),
                    'qtd_apresentada': int(r.get('QTD_APRESENTADA', 0)),
                    'teto_valor': float(teto_total),
                    'percentual_execucao': float(percentual)
                })

            return results
        except Exception as e:
            logger.error(f"Erro em get_producao_por_unidade_sql: {str(e)}")
            return []

    @staticmethod
    def get_distribuicao_categoria_sql(
        competencias: List[str],
        categorias: Optional[List[str]] = None,
        unidades: Optional[List[str]] = None
    ) -> list:
        if not competencias:
            competencias = [c['codigo'] for c in DatabaseService.get_competencias_disponiveis()]
        comp_filter = "', '".join(competencias)
        query = f"""
        SELECT categoria, SUM(valor_total_aprovado) AS Producao
        FROM mv_kpis_agregados
        WHERE competencia IN ('{comp_filter}')
        """
        if categorias and len(categorias) > 0:
            cat_list = "', '".join(categorias)
            query += f" AND categoria IN ('{cat_list}')"
        if unidades and len(unidades) > 0:
            unid_list = "', '".join(unidades)
            query += f" AND cnes_key IN ('{unid_list}')"
        query += "\nGROUP BY categoria\nORDER BY Producao DESC"

        try:
            with engine_papa.connect() as conn:
                result = conn.execute(sa.text(query))
                rows = [dict(r) for r in result.fetchall()]
            return [{'categoria': r['categoria'], 'valor_producao': float(r['producao'])} for r in rows]
        except Exception as e:
            logger.error(f"Erro em get_distribuicao_categoria_sql: {str(e)}")
            return []

    @staticmethod
    def get_tendencia_mensal_sql(
        competencias: List[str],
        categorias: Optional[List[str]] = None,
        unidades: Optional[List[str]] = None
    ) -> list:
        if not competencias:
            competencias = [c['codigo'] for c in DatabaseService.get_competencias_disponiveis()]
        comp_filter = "', '".join(competencias)
        query = f"""
        SELECT competencia AS mes_codigo, mes_nome AS mes, SUM(valor_total_aprovado) AS valor_aprovado,
               SUM(valor_total_procedimento) AS valor_apresentado, SUM(qtd_total_produzida) as qtd
        FROM mv_kpis_agregados
        WHERE competencia IN ('{comp_filter}')
        """
        if categorias and len(categorias) > 0:
            cat_list = "', '".join(categorias)
            query += f" AND categoria IN ('{cat_list}')"
        if unidades and len(unidades) > 0:
            unid_list = "', '".join(unidades)
            query += f" AND cnes_key IN ('{unid_list}')"
        query += "\nGROUP BY competencia, mes_nome\nORDER BY competencia"

        try:
            with engine_papa.connect() as conn:
                result = conn.execute(sa.text(query))
                rows = [dict(r) for r in result.fetchall()]
            # calcular percentual de execução por mês usando espelho
            df_esp = DatabaseService.get_dados_espelho()
            dados = []
            num_meses = len(competencias)
            for r in rows:
                # teto por todos os CNES (ou considerar unidades filter?) - usar total geral
                teto_total = float(df_esp['Valor_Teto'].sum()) * num_meses if not df_esp.empty else 0
                perc = (r.get('valor_aprovado', 0) / teto_total * 100) if teto_total > 0 else 0
                dados.append({
                    'mes': r.get('mes'),
                    'mes_codigo': r.get('mes_codigo'),
                    'mes_ordem': r.get('mes_codigo'),
                    'valor_aprovado': float(r.get('valor_aprovado', 0)),
                    'valor_apresentado': float(r.get('valor_apresentado', 0)),
                    'valor_teto': float(teto_total),
                    'percentual_execucao': float(perc)
                })
            return dados
        except Exception as e:
            logger.error(f"Erro em get_tendencia_mensal_sql: {str(e)}")
            return []
    
    @staticmethod
    def consolidar_producao_teto(
        df_papa: pd.DataFrame,
        df_espelho: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Faz JOIN entre produção (PAPA) e teto (Espelho)
        
        Args:
            df_papa: DataFrame com dados de produção
            df_espelho: DataFrame com dados de teto
            
        Returns:
            DataFrame consolidado
        """
        if df_papa.empty:
            return pd.DataFrame()
        
        if df_espelho.empty:
            logger.warning("Espelho vazio, usando apenas dados PAPA")
            df_papa['QTD_TETO_FISICO'] = 0
            df_papa['Valor_Teto'] = 0.0
            return df_papa
        
        # JOIN por CNES_KEY
        df_merged = pd.merge(
            df_papa,
            df_espelho[['CNES_KEY', 'QTD_TETO_FISICO', 'Valor_Teto']],
            on='CNES_KEY',
            how='left'
        )
        
        # Preenche valores nulos
        df_merged['QTD_TETO_FISICO'].fillna(0, inplace=True)
        df_merged['Valor_Teto'].fillna(0.0, inplace=True)
        
        return df_merged
    
    @staticmethod
    def _get_dados_papa_fallback(
        competencias: List[str],
        categorias: Optional[List[str]] = None,
        unidades: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Fallback: Query tradicional caso views materializadas não existam
        """
        query = """
        SELECT 
            a.id_atendimento,
            a.codigo_unidade as CNES_KEY,
            u.cnpj,
            a.competencia as MES_NOME,
            a.codigo_procedimento,
            p.descricao_procedimento,
            CASE 
                WHEN p.complexidade = '01' THEN 'ATENÇÃO BÁSICA'
                WHEN p.complexidade = '02' THEN 'MÉDIA COMPLEXIDADE'
                WHEN p.complexidade = '03' THEN 'ALTA COMPLEXIDADE'
                ELSE 'OUTROS'
            END as Categoria,
            a.quantidade_aprovada as QTD_APROVADA,
            a.valor_aprovado as Valor_Produzido,
            a.quantidade_produzida as QTD_APRESENTADA,
            a.valor_procedimento as Valor_Apresentado_Final,
            a.codigo_unidade as Unidade
        FROM atendimento a
        INNER JOIN unidade_saude u ON a.codigo_unidade = u.codigo_unidade
        INNER JOIN procedimento p ON a.codigo_procedimento = p.codigo_procedimento
        WHERE u.natureza_juridica = '1031'
        """
        
        if competencias:
            comp_list = "', '".join(competencias)
            query += f" AND a.competencia IN ('{comp_list}')"
        
        if unidades and len(unidades) > 0:
            unid_list = "', '".join(unidades)
            query += f" AND a.codigo_unidade IN ('{unid_list}')"
        
        try:
            df = pd.read_sql(query, engine_papa)
            df.columns = ['id_atendimento', 'CNES_KEY', 'cnpj', 'MES_NOME', 'codigo_procedimento', 
                         'descricao_procedimento', 'Categoria', 'QTD_APROVADA', 'Valor_Produzido',
                         'QTD_APRESENTADA', 'Valor_Apresentado_Final', 'Unidade']
            
            if categorias and len(categorias) > 0:
                df = df[df['Categoria'].isin(categorias)]
            
            return df
        except Exception as e:
            logger.error(f"Erro no fallback: {str(e)}")
            return pd.DataFrame()

# Instância singleton
db_service = DatabaseService()
