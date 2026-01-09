"""
Router para filtros (competências, categorias, unidades)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..models.schemas import FiltrosResponse
from ..services.database_service import db_service
from ..utils.state import app_state

router = APIRouter(prefix="/filtros", tags=["Filtros"])


@router.get("/competencias")
async def get_competencias():
    """
    Retorna lista de competências (meses) disponíveis.
    Usa dados em memória se houver upload, senão busca do banco.
    
    Returns:
        Lista ordenada de competências com código, nome e ordem
    """
    try:
        # Se há dados em memória (upload feito), usa eles
        if app_state.papa_df is not None and not app_state.papa_df.empty:
            competencias_unicas = sorted(app_state.papa_df['COMPETENCIA'].unique().tolist())
            competencias = [{"codigo": comp, "nome": comp, "ordem": i+1} for i, comp in enumerate(competencias_unicas)]
            return {
                "competencias": competencias,
                "total": len(competencias)
            }
        
        # Senão, busca do banco
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
    Usa dados em memória se houver upload, senão busca do banco.
    
    Returns:
        Lista de categorias (ATENÇÃO BÁSICA, MÉDIA COMPLEXIDADE, etc.)
    """
    try:
        # Se há dados em memória (upload feito), usa eles
        if app_state.papa_df is not None and not app_state.papa_df.empty:
            if 'CATEGORIA' in app_state.papa_df.columns:
                categorias = sorted(app_state.papa_df['CATEGORIA'].dropna().unique().tolist())
                return {
                    "categorias": categorias,
                    "total": len(categorias)
                }
        
        # Senão, busca do banco
        categorias = db_service.get_categorias_disponiveis()
        
        return {
            "categorias": categorias,
            "total": len(categorias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias: {str(e)}")


@router.get("/unidades")
async def get_unidades(categorias: Optional[List[str]] = Query(None)):
    """
    Retorna lista de unidades de saúde.
    Usa dados em memória se houver upload, senão busca do banco.
    
    Pode ser filtrada por categoria(s).
    
    Args:
        categorias: Lista opcional de categorias para filtrar
        
    Returns:
        Lista de unidades com nome e CNES
    """
    try:
        # Se há dados em memória (upload feito), usa eles
        if app_state.papa_df is not None and not app_state.papa_df.empty:
            df = app_state.papa_df.copy()
            
            # Filtrar por categoria se especificado
            if categorias:
                df = df[df['CATEGORIA'].isin(categorias)]
            
            # Pegar unidades únicas
            if 'UNIDADE' in df.columns and 'CNES' in df.columns:
                unidades_df = df[['UNIDADE', 'CNES']].drop_duplicates().sort_values('UNIDADE')
                unidades = [{"nome": row['UNIDADE'], "cnes": str(row['CNES'])} for _, row in unidades_df.iterrows()]
                return {
                    "unidades": unidades,
                    "total": len(unidades),
                    "filtro_aplicado": categorias is not None
                }
        
        # Senão, busca do banco
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

