"""
Router para tendência mensal (série temporal)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
import pandas as pd

from ..models.schemas import TendenciaMensal
from ..services.database_service import DatabaseService
from ..services.agregacoes import filtrar_consolidado

router = APIRouter(prefix="/tendencia-mensal", tags=["Tendência Mensal"])
logger = logging.getLogger(__name__)
db_service = DatabaseService()


@router.get("", response_model=List[TendenciaMensal])
async def get_tendencia_mensal(
    competencias: List[str] = Query(default=[], description="Lista de competências selecionadas"),
    categorias: List[str] = Query(default=[], description="Filtrar por categorias"),
    unidades: List[str] = Query(default=[], description="Filtrar por unidades (CNES)")
):
    """
    Retorna série temporal de produção mensal.
    
    Mostra evolução de:
    - Valor Aprovado
    - Valor Apresentado
    - Valor Teto (linha de referência)
    
    Args:
        competencias: Lista de competências (obrigatório)
        categorias: Filtro de categorias (opcional)
        unidades: Filtro de unidades (opcional)
        
    Returns:
        Lista com dados mensais ordenados
    """
    try:
        from ..utils.state import app_state
        from ..services.agregacoes import consolidar_producao_teto
        from ..services.calculos_kpi import calcular_tendencia_mensal

        if app_state.tem_dados():
            df_papa = app_state.df_papa.copy()
            df_teto = app_state.df_teto.copy()
            
            # Filtra por competências, categorias e unidades
            if competencias:
                df_papa = app_state.filtrar_papa_por_competencias(competencias)
            
            # Filtro de unidades no PAPA
            if unidades:
                df_papa = df_papa[df_papa['CNES_KEY'].isin(unidades)]
            
            # Filtro de categoria no TETO
            if categorias:
                # Remove emojis das categorias no df_teto para comparação
                df_teto['Categoria_Limpa'] = df_teto['Categoria'].apply(
                    lambda x: ''.join([c for i, c in enumerate(x) if c.isalpha() or c == ' ' or (i > 0 and not c.isalpha())]).strip()
                )
                df_teto = df_teto[df_teto['Categoria_Limpa'].isin(categorias)]
                df_teto = df_teto.drop(columns=['Categoria_Limpa'])
            
            df_consolidado = consolidar_producao_teto(df_papa, df_teto)
            tendencia = calcular_tendencia_mensal(df_papa, df_teto)
            return tendencia
        else:
            dados = db_service.get_tendencia_mensal_sql(
                competencias=competencias if competencias else None,
                categorias=categorias if categorias else None,
                unidades=unidades if unidades else None
            )
            return dados
    except Exception as e:
        logger.error(f"Erro em get_tendencia_mensal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {str(e)}")
