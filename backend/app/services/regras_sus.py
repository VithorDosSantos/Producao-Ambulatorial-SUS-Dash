"""
Serviço com regras de negócio SUS: processamento de PAPA e Espelho
"""
import pandas as pd
import numpy as np
from typing import List, Optional
from .leitura_csv import encontrar_coluna, encontrar_coluna_valor_teto, ler_csv_papa
from .limpeza_dados import limpar_coluna_numerica, optimize_dtypes, classificar_unidade
from ..utils.helpers import apenas_digitos, get_mes_ano_competencia, formatar_competencia_nome


def processar_papa(
    df: pd.DataFrame,
    nome_arquivo: str,
    filtrar_municipal: bool = True
) -> pd.DataFrame:
    """
    Processa arquivo PAPA aplicando todas as regras SUS.
    
    Args:
        df: DataFrame bruto do PAPA
        nome_arquivo: Nome do arquivo para logging
        filtrar_municipal: Se deve filtrar por Natureza Jurídica 1031
        
    Returns:
        DataFrame processado
    """
    # Filtro por Natureza Jurídica 1031 (Municipal)
    col_nat_jur = encontrar_coluna(df, ['PA_NAT_JUR'])
    if col_nat_jur and filtrar_municipal:
        df = df[df[col_nat_jur].astype(str) == '1031'].copy()
    
    # Remove coluna de natureza jurídica se existir
    if col_nat_jur and col_nat_jur in df.columns:
        df = df.drop(columns=[col_nat_jur])
    
    # COMPETÊNCIA: Prioridade PA_MVM sobre PA_CMP (Fallback)
    comp_col_name = encontrar_coluna(df, ['PA_MVM', 'MVM', 'PA_CMP', 'CMP'])
    
    if comp_col_name:
        comp_value = df[comp_col_name].iloc[0] if not df.empty and df[comp_col_name].any() else "999999"
        mes_nome_simplificado = apenas_digitos(str(comp_value))
        df['MES_NOME'] = mes_nome_simplificado
        df['MES_ORDEM_NUMERICA'] = get_mes_ano_competencia(mes_nome_simplificado)
        df['MES_NOME_FORMATADO'] = formatar_competencia_nome(mes_nome_simplificado)
    else:
        df['MES_ORDEM_NUMERICA'] = '999999'
        df['MES_NOME'] = 'Desconhecido'
        df['MES_NOME_FORMATADO'] = 'Desconhecido'
    
    # VALOR APROVADO (obrigatório)
    col_val_aprovado = encontrar_coluna(df, ['PA_VALAPR', 'VALAPR'])
    if col_val_aprovado is None:
        raise ValueError(f"Coluna PA_VALAPR não encontrada no arquivo {nome_arquivo}")
    
    df['Valor_Aprovado_Bruto'] = pd.to_numeric(
        limpar_coluna_numerica(df[col_val_aprovado]), 
        errors='coerce'
    ).fillna(0).astype('float32')
    
    # VALOR APRESENTADO (fallback = aprovado)
    col_val_apresentado = encontrar_coluna(df, ['PA_VALPRO', 'VALPRO'])
    if col_val_apresentado:
        df['Valor_Apresentado_Bruto'] = pd.to_numeric(
            limpar_coluna_numerica(df[col_val_apresentado]), 
            errors='coerce'
        ).fillna(0).astype('float32')
    else:
        df['Valor_Apresentado_Bruto'] = df['Valor_Aprovado_Bruto'].copy()
    
    # QUANTIDADE APROVADA
    col_qtd = encontrar_coluna(df, ['PA_QTDAPR', 'QTDAPR', 'QUANTIDADE'])
    if col_qtd:
        df['QTD_APROVADA'] = pd.to_numeric(
            limpar_coluna_numerica(df[col_qtd]), 
            errors='coerce'
        ).fillna(0).astype('int32')
    else:
        df['QTD_APROVADA'] = np.int32(0)
    
    # QUANTIDADE APRESENTADA (fallback = aprovada)
    col_qtd_apresentada = encontrar_coluna(df, ['PA_QTDPROD', 'PA_QTDPRO', 'QTDPROD'])
    if col_qtd_apresentada:
        df['QTD_APRESENTADA'] = pd.to_numeric(
            limpar_coluna_numerica(df[col_qtd_apresentada]), 
            errors='coerce'
        ).fillna(0).astype('int32')
    else:
        df['QTD_APRESENTADA'] = df['QTD_APROVADA'].copy()
    
    # CNES (preenchimento com 7 dígitos)
    col_cnes = encontrar_coluna(df, ['PA_CODUNI', 'CODUNI', 'CNES'])
    if col_cnes is None:
        raise ValueError(f"Coluna CNES não encontrada no arquivo {nome_arquivo}")
    
    df['CNES_KEY'] = df[col_cnes].astype(str).str.strip().str.replace('"', '').str.zfill(7)
    
    # Otimiza tipos de dados
    df = optimize_dtypes(df)
    
    return df


def processar_espelho(df: pd.DataFrame, mapa_categorias: Optional[dict] = None) -> pd.DataFrame:
    """
    Processa arquivo Espelho (Teto) aplicando regras SUS.
    
    Args:
        df: DataFrame bruto do Espelho
        mapa_categorias: Dicionário com mapeamento CNES -> Categoria
        
    Returns:
        DataFrame agrupado por CNES com Valor_Teto e QTD_TETO_FISICO
    """
    # Encontra coluna de valor do teto
    col_teto = encontrar_coluna_valor_teto(df.columns.tolist())
    
    if col_teto is None:
        # Fallback
        col_teto = encontrar_coluna(df, ['ORCAMENTARIO'])
    
    # Encontra coluna de quantidade
    col_qtd_teto = encontrar_coluna(df, ['FISICO', 'QTD_TETO', 'QTD'])
    
    # Converte valores
    if col_teto:
        df['Valor_Teto'] = pd.to_numeric(
            limpar_coluna_numerica(df[col_teto]), 
            errors='coerce'
        ).fillna(0).astype('float32')
    else:
        df['Valor_Teto'] = np.float32(0.0)
    
    if col_qtd_teto:
        df['QTD_TETO_FISICO'] = pd.to_numeric(
            limpar_coluna_numerica(df[col_qtd_teto]), 
            errors='coerce'
        ).fillna(0).astype('int32')
    else:
        df['QTD_TETO_FISICO'] = np.int32(0)
    
    # Encontra colunas de CNES e Nome
    from ..utils.helpers import normalizar_texto
    
    headers_norm = [normalizar_texto(c) for c in df.columns]
    idx_cnes = next((i for i, h in enumerate(headers_norm) if 'NUM_CNES' in h or 'CNES' in h or 'COD_UNIDADE' in h), None)
    idx_nome = next((i for i, h in enumerate(headers_norm) if ('NOME' in h and 'ESTAB' in h) or 'UNIDADE' in h), None)
    
    if idx_cnes is None:
        raise ValueError("Coluna CNES não encontrada no arquivo Espelho")
    
    col_cnes = df.columns[idx_cnes]
    col_nome = df.columns[idx_nome] if idx_nome is not None else col_cnes
    
    # CNES com 7 dígitos
    df['CNES_KEY'] = df[col_cnes].astype(str).str.strip().str.replace('"', '').str.zfill(7)
    df['Unidade'] = df[col_nome].astype(str)
    
    # Agrupa por CNES
    teto_agrupado = df.groupby(['CNES_KEY', 'Unidade']).agg(
        Valor_Teto=('Valor_Teto', 'sum'),
        QTD_TETO_FISICO=('QTD_TETO_FISICO', 'sum')
    ).reset_index()
    
    # Aplica classificação de categoria
    teto_agrupado['Categoria'] = teto_agrupado.apply(
        lambda row: classificar_unidade(
            row['Unidade'], 
            cnes=row['CNES_KEY'], 
            mapa_categorias=mapa_categorias
        ),
        axis=1
    )
    
    # Otimiza tipos
    teto_agrupado = optimize_dtypes(teto_agrupado)
    
    return teto_agrupado
