"""
Router para visão geral (gráficos de barras e donut)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from ..models.schemas import UnidadeProducao, CategoriaDistribuicao
from ..services.database_service import DatabaseService
from ..services.agregacoes import filtrar_consolidado, consolidar_producao_teto
from ..utils.state import app_state

router = APIRouter(prefix="/visao-geral", tags=["Visão Geral"])
logger = logging.getLogger(__name__)
db_service = DatabaseService()


@router.get("/unidades", response_model=List[UnidadeProducao])
async def get_producao_por_unidade(
    competencias: List[str] = Query(default=[], description="Lista de competências selecionadas"),
    categorias: List[str] = Query(default=[], description="Filtrar por categorias"),
    unidades: List[str] = Query(default=[], description="Filtrar por unidades (CNES)"),
    top: int = Query(10, ge=1, le=50, description="Top N unidades (máx 50)")
):
    """
    Retorna dados de produção por unidade para gráfico de barras.
    
    Comparação: Valor Orçado (Teto Acumulado) × Valor Aprovado
    
    Args:
        competencias: Lista de competências (obrigatório)
        categorias: Filtro de categorias (opcional)
        unidades: Filtro de unidades (opcional)
        top: Número de unidades a retornar (default 10)
        
    Returns:
        Lista com dados de produção por unidade
    """
    try:
        # Se houver dados carregados via upload, usar eles
        if app_state.tem_dados():
            df_papa = app_state.df_papa.copy()
            df_teto = app_state.df_teto.copy()
            
            if competencias:
                df_papa = app_state.filtrar_papa_por_competencias(competencias)
            
            # Filtro de unidades no PAPA
            if unidades:
                df_papa = df_papa[df_papa['CNES_KEY'].isin(unidades)]
            
            # Filtro de categoria no TETO (categoria está no df_teto, não no df_papa)
            if categorias:
                # Remove emojis das categorias no df_teto para comparação
                df_teto['Categoria_Limpa'] = df_teto['Categoria'].apply(
                    lambda x: ''.join([c for i, c in enumerate(x) if c.isalpha() or c == ' ' or (i > 0 and not c.isalpha())]).strip()
                )
                df_teto = df_teto[df_teto['Categoria_Limpa'].isin(categorias)]
                df_teto = df_teto.drop(columns=['Categoria_Limpa'])
            
            df_consolidado = consolidar_producao_teto(df_papa, df_teto)
            # Não precisa filtrar novamente - já filtramos antes da consolidação
            # Ordena por valor aprovado e pega o top N
            df_consolidado = df_consolidado.sort_values(by='Valor_Produzido', ascending=False).head(top)
            resultado = []
            for _, row in df_consolidado.iterrows():
                resultado.append(UnidadeProducao(
                    unidade=row['Unidade'],
                    cnes=row['CNES_KEY'],
                    valor_teto=float(row['Valor_Teto']),
                    valor_aprovado=float(row['Valor_Produzido']),
                    valor_apresentado=float(row['Valor_Apresentado_Final']) if 'Valor_Apresentado_Final' in row else 0.0,
                    percentual_execucao=float(row['Percentual_Execucao'])
                ))
            return resultado
        # Caso contrário, usa banco normalmente
        dados = db_service.get_producao_por_unidade_sql(
            competencias=competencias if competencias else None,
            categorias=categorias if categorias else None,
            unidades=unidades if unidades else None,
            top_n=top
        )
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {str(e)}")


@router.get("/categorias", response_model=List[CategoriaDistribuicao])
async def get_distribuicao_categorias(
    competencias: List[str] = Query(default=[], description="Lista de competências selecionadas"),
    categorias: List[str] = Query(default=[], description="Filtrar por categorias"),
    unidades: List[str] = Query(default=[], description="Filtrar por unidades (CNES)")
):
    """
    Retorna distribuição de produção por categoria para gráfico donut/pizza.
    
    Args:
        competencias: Lista de competências (obrigatório)
        categorias: Filtro de categorias (opcional)
        unidades: Filtro de unidades (opcional)
        
    Returns:
        Lista com distribuição por categoria
    """
    try:
        # Se houver dados carregados via upload, usar eles
        if app_state.tem_dados():
            df_papa = app_state.df_papa.copy()
            df_teto = app_state.df_teto.copy()
            
            if competencias:
                df_papa = app_state.filtrar_papa_por_competencias(competencias)
            
            # Filtro de unidades no PAPA
            if unidades:
                df_papa = df_papa[df_papa['CNES_KEY'].isin(unidades)]
            
            # Filtro de categoria no TETO (categoria está no df_teto, não no df_papa)
            if categorias:
                # Remove emojis das categorias no df_teto para comparação
                df_teto['Categoria_Limpa'] = df_teto['Categoria'].apply(
                    lambda x: ''.join([c for i, c in enumerate(x) if c.isalpha() or c == ' ' or (i > 0 and not c.isalpha())]).strip()
                )
                df_teto = df_teto[df_teto['Categoria_Limpa'].isin(categorias)]
                df_teto = df_teto.drop(columns=['Categoria_Limpa'])
            
            df_consolidado = consolidar_producao_teto(df_papa, df_teto)
            # Não precisa filtrar novamente - já filtramos antes da consolidação
            
            # Agrupa por categoria
            df_cat = df_consolidado.groupby('Categoria').agg(
                valor_producao=('Valor_Produzido', 'sum')
            ).reset_index()
            
            # Total produzido (soma de todas as categorias)
            total_produzido = df_cat['valor_producao'].sum()
            
            resultado = []
            for _, row in df_cat.iterrows():
                # Percentual = (produção da categoria / produção total) * 100
                perc_exec = (row['valor_producao'] / total_produzido * 100) if total_produzido > 0 else 0.0
                resultado.append(CategoriaDistribuicao(
                    categoria=row['Categoria'],
                    valor_producao=float(row['valor_producao']),
                    percentual_execucao=float(perc_exec)
                ))
            return sorted(resultado, key=lambda x: x.valor_producao, reverse=True)
        # Caso contrário, usa banco normalmente
        dados = db_service.get_distribuicao_categoria_sql(
            competencias=competencias if competencias else None,
            categorias=categorias if categorias else None,
            unidades=unidades if unidades else None
        )
        
        # Calcula percentual para dados do banco também
        total_produzido = sum(d['valor_producao'] for d in dados)
        resultado = []
        for d in dados:
            perc_exec = (d['valor_producao'] / total_produzido * 100) if total_produzido > 0 else 0.0
            resultado.append(CategoriaDistribuicao(
                categoria=d['categoria'],
                valor_producao=d['valor_producao'],
                percentual_execucao=perc_exec
            ))
        return sorted(resultado, key=lambda x: x.valor_producao, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {str(e)}")
