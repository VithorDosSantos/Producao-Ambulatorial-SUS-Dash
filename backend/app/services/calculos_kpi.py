"""
Serviço de cálculo de KPIs e métricas agregadas
"""
import pandas as pd
from typing import Dict, List, Optional


def calcular_kpis_globais(
    df_consolidado: pd.DataFrame,
    num_meses: int
) -> Dict[str, float]:
    """
    Calcula KPIs globais do dashboard.
    
    Args:
        df_consolidado: DataFrame consolidado com Teto × Produção
        num_meses: Número de meses para multiplicação do teto
        
    Returns:
        Dicionário com métricas calculadas
    """
    # IMPORTANTE: Teto é por unidade, não por procedimento!
    # Agrupa por CNES para pegar teto apenas UMA VEZ por unidade
    df_teto_unico = df_consolidado.groupby('CNES_KEY').agg({
        'Valor_Teto': 'first',  # Pega o primeiro (todos são iguais para o mesmo CNES)
        'QTD_TETO_FISICO': 'first'
    }).reset_index()
    
    teto_base_valor = df_teto_unico['Valor_Teto'].sum()
    teto_total_valor = teto_base_valor * num_meses
    
    teto_base_qtd = df_teto_unico['QTD_TETO_FISICO'].sum()
    teto_total_qtd = teto_base_qtd * num_meses
    
    producao_aprovada = df_consolidado['Valor_Produzido'].sum()
    valor_apresentado = df_consolidado['Valor_Apresentado_Final'].sum()
    
    qtd_aprovada = df_consolidado['QTD_APROVADA'].sum()
    qtd_apresentada = df_consolidado['QTD_APRESENTADA'].sum()
    
    saldo = teto_total_valor - producao_aprovada
    percentual_exec = (producao_aprovada / teto_total_valor * 100) if teto_total_valor > 0 else 0
    
    return {
        'teto_total_valor': float(teto_total_valor),
        'teto_total_qtd': int(teto_total_qtd),
        'producao_aprovada_valor': float(producao_aprovada),
        'producao_aprovada_qtd': int(qtd_aprovada),
        'producao_apresentada_valor': float(valor_apresentado),
        'producao_apresentada_qtd': int(qtd_apresentada),
        'saldo': float(saldo),
        'percentual_execucao': float(percentual_exec),
        'saldo_percentual': float(100 - percentual_exec)
    }


def calcular_producao_por_unidade(
    df_consolidado: pd.DataFrame,
    num_meses: int,
    top_n: Optional[int] = None
) -> List[Dict]:
    """
    Calcula produção por unidade para gráfico de barras.
    
    Args:
        df_consolidado: DataFrame consolidado
        num_meses: Número de meses
        top_n: Retorna apenas top N unidades (opcional)
        
    Returns:
        Lista de dicionários com dados por unidade
    """
    # Agrupa por unidade (CNES_KEY) somando produção e pegando teto uma vez
    df_agrupado = df_consolidado.groupby(['CNES_KEY', 'Unidade']).agg({
        'Valor_Teto': 'first',  # Teto é único por unidade
        'QTD_TETO_FISICO': 'first',
        'Valor_Produzido': 'sum',  # Soma a produção de todos os procedimentos
        'Valor_Apresentado_Final': 'sum',
        'QTD_APROVADA': 'sum',
        'QTD_APRESENTADA': 'sum'
    }).reset_index()
    
    # Calcula teto acumulado
    df_agrupado['Teto_Acumulado'] = df_agrupado['Valor_Teto'] * num_meses
    
    # Ordena e pega top N
    df_agrupado = df_agrupado.sort_values('Valor_Produzido', ascending=False)
    if top_n:
        df_agrupado = df_agrupado.head(top_n)
    
    resultado = []
    for _, row in df_agrupado.iterrows():
        resultado.append({
            'unidade': row['Unidade'],
            'cnes': row['CNES_KEY'],
            'valor_teto': float(row['Teto_Acumulado']),
            'valor_aprovado': float(row['Valor_Produzido']),
            'valor_apresentado': float(row['Valor_Apresentado_Final']),
            'percentual_execucao': float((row['Valor_Produzido'] / row['Teto_Acumulado'] * 100) if row['Teto_Acumulado'] > 0 else 0)
        })
    
    return resultado


def calcular_distribuicao_categoria(
    df_consolidado: pd.DataFrame,
    num_meses: int
) -> List[Dict]:
    """
    Calcula distribuição por categoria para gráfico donut.
    
    Args:
        df_consolidado: DataFrame consolidado
        num_meses: Número de meses
        
    Returns:
        Lista de dicionários com dados por categoria
    """
    # Primeiro, pega teto único por unidade
    df_teto_unico = df_consolidado.groupby('CNES_KEY').agg({
        'Valor_Teto': 'first'
    }).reset_index()
    
    # Agrupa por Categoria somando produção
    df_cat = df_consolidado.groupby('Categoria').agg(
        Producao=('Valor_Produzido', 'sum')
    ).reset_index()
    
    # Total do teto (único para todas as categorias)
    teto_total_base = df_teto_unico['Valor_Teto'].sum()
    teto_total = teto_total_base * num_meses
    
    resultado = []
    for _, row in df_cat.iterrows():
        perc_exec = (row['Producao'] / teto_total * 100) if teto_total > 0 else 0
        
        resultado.append({
            'categoria': row['Categoria'],
            'valor_producao': float(row['Producao']),
            'percentual_execucao': float(perc_exec)
        })
    
    return sorted(resultado, key=lambda x: x['valor_producao'], reverse=True)


def calcular_tendencia_mensal(
    df_papa: pd.DataFrame,
    df_teto: pd.DataFrame,
    cnes_selecionados: Optional[List[str]] = None
) -> List[Dict]:
    """
    Calcula tendência mensal de produção.
    
    Args:
        df_papa: DataFrame com dados PAPA
        df_teto: DataFrame com teto agrupado
        cnes_selecionados: Lista de CNES para filtrar (opcional)
        
    Returns:
        Lista de dicionários com dados por mês
    """
    # Filtra por CNES se especificado
    if cnes_selecionados:
        df_papa = df_papa[df_papa['CNES_KEY'].isin(cnes_selecionados)].copy()
    
    # Agrupa por mês
    tendencia = df_papa.groupby(['MES_NOME', 'MES_ORDEM_NUMERICA', 'MES_NOME_FORMATADO']).agg(
        Valor_Aprovado=('Valor_Aprovado_Bruto', 'sum'),
        Valor_Apresentado=('Valor_Apresentado_Bruto', 'sum')
    ).reset_index()
    
    # Calcula teto mensal
    if cnes_selecionados:
        teto_mensal = df_teto[df_teto['CNES_KEY'].isin(cnes_selecionados)]['Valor_Teto'].sum()
    else:
        teto_mensal = df_teto['Valor_Teto'].sum()
    
    tendencia['Valor_Teto'] = teto_mensal
    tendencia['Percentual_Execucao'] = tendencia.apply(
        lambda x: (x['Valor_Aprovado'] / x['Valor_Teto'] * 100) if x['Valor_Teto'] > 0 else 0,
        axis=1
    )
    
    # Ordena por mês
    tendencia = tendencia.sort_values('MES_ORDEM_NUMERICA')
    
    # Formata nome do mês (remove código inicial)
    tendencia['Mes_Display'] = tendencia['MES_NOME_FORMATADO'].str.replace(r'^\d{4,6} - ', '', regex=True)
    
    resultado = []
    for _, row in tendencia.iterrows():
        resultado.append({
            'mes': row['Mes_Display'],
            'mes_codigo': row['MES_NOME'],
            'mes_ordem': row['MES_ORDEM_NUMERICA'],
            'valor_aprovado': float(row['Valor_Aprovado']),
            'valor_apresentado': float(row['Valor_Apresentado']),
            'valor_teto': float(row['Valor_Teto']),
            'percentual_execucao': float(row['Percentual_Execucao'])
        })
    
    return resultado
