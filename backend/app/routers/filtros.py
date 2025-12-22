"""
Router para filtros (competências, categorias, unidades)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..models.schemas import FiltrosResponse
from ..services.database_service import db_service

router = APIRouter(prefix="/filtros", tags=["Filtros"])


@router.get("/competencias")
async def get_competencias():
    """
    Retorna lista de competências (meses) disponíveis no banco PAPA.
    
    Returns:
        Lista ordenada de competências com código, nome e ordem
    """
    try:
        competencias = db_service.get_competencias_disponiveis()
        
        return {
            "competencias": competencias,
            "total": len(competencias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar competências: {str(e)}")


@router.get("/categorias")
async def get_categorias():
    """
    Retorna lista de categorias de procedimentos disponíveis.
    
    Returns:
        Lista de categorias (ATENÇÃO BÁSICA, MÉDIA COMPLEXIDADE, etc.)
    """
    try:
        categorias = db_service.get_categorias_disponiveis()
        
        return {
            "categorias": categorias,
            "total": len(categorias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias: {str(e)}")


@router.get("/unidades")
async def get_unidades(
    categorias: Optional[List[str]] = Query(default=None, description="Filtrar por categorias")
):
    """
    Retorna lista de unidades de saúde do banco PAPA.
    
    Pode ser filtrada por categoria(s).
    
    Args:
        categorias: Lista opcional de categorias para filtrar
        
    Returns:
        Lista de unidades com nome e CNES
    """
    try:
        unidades = db_service.get_unidades_disponiveis(categorias=categorias)
        
        return {
            "unidades": unidades,
            "total": len(unidades),
            "filtro_aplicado": categorias is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar unidades: {str(e)}")


@router.get("/todos")
async def get_todos_filtros():
    """
    Retorna todos os filtros disponíveis em uma única requisição.
    Otimizado para carregar todos de uma vez.
    
    Returns:
        Competências, categorias e unidades
    """
    try:
        from ..utils.state import app_state
        if app_state.tem_dados():
            competencias = app_state.get_competencias()
            categorias = app_state.get_categorias()
            unidades = app_state.get_unidades()
        else:
            competencias = db_service.get_competencias_disponiveis()
            categorias = db_service.get_categorias_disponiveis()
            unidades = db_service.get_unidades_disponiveis()
        return FiltrosResponse(
            competencias=competencias,
            categorias=categorias,
            unidades=unidades
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar filtros: {str(e)}")

