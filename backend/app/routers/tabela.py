"""
Router para tabela detalhada e exportação
"""
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from typing import List, Optional
import pandas as pd
from io import StringIO, BytesIO
import logging

from ..models.schemas import LinhaTabela
from ..services.database_service import DatabaseService
from ..utils.state import app_state
from ..services.agregacoes import filtrar_consolidado, preparar_tabela_detalhada
from ..utils.helpers import formatar_brl, formatar_geral

router = APIRouter(prefix="/tabela-detalhada", tags=["Tabela"])
logger = logging.getLogger(__name__)
db_service = DatabaseService()


@router.get("", response_model=List[LinhaTabela])
async def get_tabela_detalhada(
    competencias: List[str] = Query(default=[], description="Lista de competências selecionadas"),
    categorias: List[str] = Query(default=[], description="Filtrar por categorias"),
    unidades: List[str] = Query(default=[], description="Filtrar por unidades (CNES)")
):
    """
    Retorna tabela detalhada de execução por unidade.
    
    Inclui:
    - Dados de cada unidade (nome, CNES, categoria)
    - Valores orçados, apresentados e aprovados
    - Quantidades
    - Saldo e percentual de execução
    
    Args:
        competencias: Lista de competências (obrigatório)
        categorias: Filtro de categorias (opcional)
        unidades: Filtro de unidades (opcional)
        
    Returns:
        Lista de linhas da tabela
    """
    try:
        # Se houver dados carregados via upload, usa eles
        if app_state.tem_dados():
            df_papa = app_state.df_papa
            df_teto = app_state.df_teto
            if competencias:
                df_papa = app_state.filtrar_papa_por_competencias(competencias)
            if categorias:
                df_papa = df_papa[df_papa['Categoria'].isin(categorias)]
            if unidades:
                df_papa = df_papa[df_papa['CNES_KEY'].isin(unidades)]
            from ..services.agregacoes import consolidar_producao_teto, preparar_tabela_detalhada
            num_meses = len(competencias) if competencias else len(df_papa['MES_NOME'].unique())
            df_consolidado = consolidar_producao_teto(df_papa, df_teto)
            df_consolidado = filtrar_consolidado(df_consolidado, categorias=categorias, unidades=unidades)
            if df_consolidado.empty:
                return []
            df_tabela = preparar_tabela_detalhada(df_consolidado, num_meses)
            resultado = []
            for _, row in df_tabela.iterrows():
                resultado.append(LinhaTabela(
                    unidade=row['Unidade'],
                    cnes=row['CNES_KEY'],
                    categoria=row['Categoria'],
                    qtd_teto=int(row['QTD_Teto_Acumulado']),
                    valor_teto=float(row['Teto_Acumulado']),
                    qtd_apresentada=int(row['QTD_APRESENTADA']),
                    valor_apresentado=float(row['Valor_Apresentado_Final']),
                    qtd_aprovada=int(row['QTD_APROVADA']),
                    valor_aprovado=float(row['Valor_Produzido']),
                    saldo=float(row['Saldo_Monetario']),
                    percentual_execucao=float(row['Execucao_Percentual'])
                ))
            return resultado
        # Caso contrário, usa banco normalmente
        df_papa = db_service.get_dados_papa_filtrados(
            competencias=competencias if competencias else None,
            categorias=categorias if categorias else None,
            unidades=unidades if unidades else None
        )
        if df_papa.empty:
            return []
        df_espelho = db_service.get_dados_espelho()
        num_meses = len(competencias) if competencias else len(df_papa['MES_NOME'].unique())
        df_consolidado = db_service.consolidar_producao_teto(df_papa, df_espelho)
        df_consolidado = filtrar_consolidado(df_consolidado, categorias=categorias, unidades=unidades)
        if df_consolidado.empty:
            return []
        df_tabela = preparar_tabela_detalhada(df_consolidado, num_meses)
        resultado = []
        for _, row in df_tabela.iterrows():
            resultado.append(LinhaTabela(
                unidade=row['Unidade'],
                cnes=row['CNES_KEY'],
                categoria=row['Categoria'],
                qtd_teto=int(row['QTD_Teto_Acumulado']),
                valor_teto=float(row['Teto_Acumulado']),
                qtd_apresentada=int(row['QTD_APRESENTADA']),
                valor_apresentado=float(row['Valor_Apresentado_Final']),
                qtd_aprovada=int(row['QTD_APROVADA']),
                valor_aprovado=float(row['Valor_Produzido']),
                saldo=float(row['Saldo_Monetario']),
                percentual_execucao=float(row['Execucao_Percentual'])
            ))
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {str(e)}")
