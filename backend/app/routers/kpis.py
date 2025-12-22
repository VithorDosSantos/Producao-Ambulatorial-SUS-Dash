"""
Router para KPIs (indicadores globais)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from ..models.schemas import KPIResponse
from ..services.calculos_kpi import calcular_kpis_globais
from ..services.database_service import db_service
from ..utils.state import app_state

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("", response_model=KPIResponse)
async def get_kpis(
    competencias: List[str] = Query(default=[], description="Lista de competências selecionadas"),
    categorias: List[str] = Query(default=[], description="Filtrar por categorias"),
    unidades: List[str] = Query(default=[], description="Filtrar por unidades (CNES)")
):
    """
    Retorna os KPIs globais do dashboard diretamente do banco de dados.
    
    Métricas incluídas:
    - Teto total (valor e quantidade orçada)
    - Produção aprovada (valor e quantidade)
    - Produção apresentada (valor e quantidade)
    - Saldo monetário
    - Percentual de execução
    
    Args:
        competencias: Lista de competências (YYYYMM)
        categorias: Filtro de categorias (opcional)
        unidades: Filtro de unidades por CNES (opcional)
        
    Returns:
        Objeto com todos os KPIs calculados
    """
    try:
        # Se houver dados carregados via upload, calcula KPIs a partir deles
        if app_state.tem_dados():
            # Filtra dados conforme filtros (categoria só em df_papa)
            df_papa = app_state.df_papa
            df_teto = app_state.df_teto
            if competencias:
                df_papa = app_state.filtrar_papa_por_competencias(competencias)
            if categorias:
                df_papa = df_papa[df_papa['Categoria'].isin(categorias)]
            if unidades:
                df_papa = df_papa[df_papa['CNES_KEY'].isin(unidades)]
            # Se não houver produção após filtro, retorna KPIs zerados com mensagem
            if df_papa.empty:
                logger.info("Filtro resultou em DataFrame de produção vazio. Retornando KPIs zerados.")
                return {
                    "mensagem": "Nenhum dado encontrado para os filtros aplicados.",
                    **KPIResponse(
                        teto_total_valor=0.0,
                        teto_total_qtd=0,
                        producao_aprovada_valor=0.0,
                        producao_aprovada_qtd=0,
                        producao_apresentada_valor=0.0,
                        producao_apresentada_qtd=0,
                        saldo=0.0,
                        percentual_execucao=0.0,
                        saldo_percentual=100.0
                    ).dict()
                }
            # Reconsolida produção (teto não deve ser filtrado por categoria)
            from ..services.agregacoes import consolidar_producao_teto
            df_consolidado = consolidar_producao_teto(df_papa, df_teto)
            # Se não houver produção consolidada (nenhum CNES com teto e produção), retorna KPIs zerados com mensagem
            if df_consolidado.empty:
                logger.info("JOIN produção+teto resultou em DataFrame vazio. Retornando KPIs zerados.")
                return {
                    "mensagem": "Nenhum dado encontrado após consolidação produção+teto.",
                    **KPIResponse(
                        teto_total_valor=0.0,
                        teto_total_qtd=0,
                        producao_aprovada_valor=0.0,
                        producao_aprovada_qtd=0,
                        producao_apresentada_valor=0.0,
                        producao_apresentada_qtd=0,
                        saldo=0.0,
                        percentual_execucao=0.0,
                        saldo_percentual=100.0
                    ).dict()
                }
            # Calcular número de meses para KPIs
            if competencias:
                num_meses = len(competencias)
            else:
                num_meses = len(df_papa['MES_NOME'].unique()) if 'MES_NOME' in df_papa.columns else 1
            kpis = calcular_kpis_globais(df_consolidado, num_meses)
            return KPIResponse(**kpis)
        # Caso contrário, usa banco normalmente
        if not competencias:
            comps_disponiveis = db_service.get_competencias_disponiveis()
            competencias = [c['codigo'] for c in comps_disponiveis]
        kpis = db_service.get_kpis_aggregated_sql(
            competencias=competencias,
            categorias=categorias if categorias else None,
            unidades=unidades if unidades else None
        )
        if not kpis or all((v == 0 or v == 0.0) for v in kpis.values()):
            logger.info("Consulta SQL retornou KPIs zerados. Retornando mensagem de dados não encontrados.")
            return {
                "mensagem": "Nenhum dado encontrado para os filtros aplicados.",
                **KPIResponse(
                    teto_total_valor=0.0,
                    teto_total_qtd=0,
                    producao_aprovada_valor=0.0,
                    producao_aprovada_qtd=0,
                    producao_apresentada_valor=0.0,
                    producao_apresentada_qtd=0,
                    saldo=0.0,
                    percentual_execucao=0.0,
                    saldo_percentual=100.0
                ).dict()
            }
        return KPIResponse(**kpis)
    except Exception as e:
        logger.error(f"Erro ao calcular KPIs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPIs: {str(e)}")
