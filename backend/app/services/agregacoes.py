"""
Serviço de agregações e consolidação de dados
"""
import pandas as pd
from typing import Optional
from .limpeza_dados import optimize_dtypes


def consolidar_producao_teto(
    df_papa: pd.DataFrame,
    df_teto: pd.DataFrame
) -> pd.DataFrame:
    """
    Agrupa produção por CNES e faz INNER JOIN com o Teto.
    
    Esta é a função central que replica a lógica do processar_consolidado
    do código Streamlit original.
    
    Args:
        df_papa: DataFrame com dados PAPA processados
        df_teto: DataFrame com teto agrupado por CNES
        
    Returns:
        DataFrame consolidado com Teto × Produção
    """
    if df_papa.empty or df_teto.empty:
        return pd.DataFrame(columns=[
            'CNES_KEY', 'Unidade', 'Categoria', 'Valor_Teto', 'QTD_TETO_FISICO',
            'Valor_Produzido', 'Valor_Apresentado_Final', 'QTD_APROVADA', 'QTD_APRESENTADA',
            'Saldo', 'Percentual_Execucao'
        ])
    
    # Agrupa produção por CNES
    prod_data = df_papa.groupby('CNES_KEY').agg(
        Valor_Produzido=('Valor_Aprovado_Bruto', 'sum'),
        Valor_Apresentado_Final=('Valor_Apresentado_Bruto', 'sum'),
        QTD_APROVADA=('QTD_APROVADA', 'sum'),
        QTD_APRESENTADA=('QTD_APRESENTADA', 'sum')
    ).reset_index()
    
    # INNER JOIN: Apenas estabelecimentos que têm Teto E Produção
    final = pd.merge(df_teto, prod_data, on='CNES_KEY', how='inner').fillna(0)
    
    if final.empty:
        return pd.DataFrame(columns=[
            'CNES_KEY', 'Unidade', 'Categoria', 'Valor_Teto', 'QTD_TETO_FISICO',
            'Valor_Produzido', 'Valor_Apresentado_Final', 'QTD_APROVADA', 'QTD_APRESENTADA',
            'Saldo', 'Percentual_Execucao'
        ])
    
    # Corrige nome de unidade desconhecida
    final['Unidade'] = final['Unidade'].astype(str).replace(['0', '0.0'], 'Unidade Desconhecida')
    
    # Calcula saldo e percentual (usando Teto BASE, não acumulado)
    final['Saldo'] = final['Valor_Teto'] - final['Valor_Produzido']
    final['Percentual_Execucao'] = final.apply(
        lambda x: (x['Valor_Produzido'] / x['Valor_Teto'] * 100) if x['Valor_Teto'] > 0 else 0,
        axis=1
    )
    
    # Otimiza tipos
    final = optimize_dtypes(final)
    
    return final


def filtrar_consolidado(
    df: pd.DataFrame,
    categorias: Optional[list] = None,
    unidades: Optional[list] = None
) -> pd.DataFrame:
    """
    Aplica filtros de categoria e unidade ao DataFrame consolidado.
    
    Args:
        df: DataFrame consolidado
        categorias: Lista de categorias para filtrar (opcional)
        unidades: Lista de unidades (CNES) para filtrar (opcional)
        
    Returns:
        DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    if categorias and len(categorias) > 0:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
    
    if unidades and len(unidades) > 0:
        # Unidades são CNES_KEY, não nomes
        df_filtrado = df_filtrado[df_filtrado['CNES_KEY'].isin(unidades)]
    
    return df_filtrado


def preparar_tabela_detalhada(
    df_consolidado: pd.DataFrame,
    num_meses: int
) -> pd.DataFrame:
    """
    Prepara DataFrame para exportação em tabela detalhada.
    
    Args:
        df_consolidado: DataFrame consolidado
        num_meses: Número de meses para acumular o teto
        
    Returns:
        DataFrame formatado para exibição
    """
    df = df_consolidado.copy()
    
    # Calcula valores acumulados
    df['QTD_Teto_Acumulado'] = df['QTD_TETO_FISICO'] * num_meses
    df['Teto_Acumulado'] = df['Valor_Teto'] * num_meses
    df['Saldo_Monetario'] = df['Teto_Acumulado'] - df['Valor_Produzido']
    df['Execucao_Percentual'] = df.apply(
        lambda row: (row['Valor_Produzido'] / row['Teto_Acumulado'] * 100) if row['Teto_Acumulado'] > 0 else 0,
        axis=1
    ).clip(0, 100)
    
    # Seleciona colunas relevantes
    colunas = [
        'Unidade', 'CNES_KEY', 'Categoria',
        'QTD_Teto_Acumulado', 'Teto_Acumulado',
        'QTD_APRESENTADA', 'Valor_Apresentado_Final',
        'QTD_APROVADA', 'Valor_Produzido',
        'Saldo_Monetario', 'Execucao_Percentual'
    ]
    
    return df[colunas]
