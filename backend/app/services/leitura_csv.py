"""
Serviço de leitura e parsing de arquivos CSV (PAPA e Espelho)
"""
import pandas as pd
import numpy as np
from io import BytesIO
from typing import Tuple, List, Optional
import re
from ..utils.helpers import (
    normalizar_texto, 
    apenas_digitos, 
    formatar_competencia_nome, 
    get_mes_ano_competencia
)


def detectar_separador(conteudo_bytes: bytes) -> str:
    """
    Detecta o separador CSV (';' ou ',') baseado na primeira linha.
    
    Args:
        conteudo_bytes: Conteúdo do arquivo em bytes
        
    Returns:
        Separador detectado
    """
    try:
        primeira_linha = conteudo_bytes.split(b'\n')[0].decode('latin1', errors='ignore')
        return ';' if primeira_linha.count(';') > primeira_linha.count(',') else ','
    except Exception:
        return ';'


def limpar_colunas_bom(colunas: List[str]) -> List[str]:
    """
    Remove caracteres BOM e não alfanuméricos do início dos nomes das colunas.
    
    Args:
        colunas: Lista de nomes de colunas
        
    Returns:
        Lista de colunas limpas
    """
    colunas_limpas = []
    for col in colunas:
        match = re.search(r'[A-Za-z0-9_]', col)
        if match:
            col_limpa = col[match.start():]
        else:
            col_limpa = col
        colunas_limpas.append(col_limpa.strip())
    return colunas_limpas


def ler_csv_papa(conteudo_bytes: bytes, nome_arquivo: str) -> pd.DataFrame:
    """
    Lê arquivo PAPA (produção) e retorna DataFrame processado.
    
    Args:
        conteudo_bytes: Conteúdo do arquivo em bytes
        nome_arquivo: Nome do arquivo para logging
        
    Returns:
        DataFrame com dados processados
    """
    if not conteudo_bytes or len(conteudo_bytes) == 0:
        raise ValueError(f"Arquivo {nome_arquivo} está vazio")
    
    # Detecta separador
    sep = detectar_separador(conteudo_bytes)
    
    # Lê CSV
    df = pd.read_csv(
        BytesIO(conteudo_bytes), 
        dtype=str, 
        encoding='latin1', 
        sep=sep, 
        on_bad_lines='skip'
    )
    
    if df.empty:
        raise ValueError(f"Arquivo {nome_arquivo} resultou em DataFrame vazio")
    
    # Limpa nomes das colunas (remove BOM)
    df.columns = limpar_colunas_bom(df.columns.tolist())
    
    return df


def ler_csv_espelho(conteudo_bytes: bytes) -> pd.DataFrame:
    """
    Lê arquivo Espelho (teto orçamentário) e retorna DataFrame processado.
    
    Args:
        conteudo_bytes: Conteúdo do arquivo em bytes
        
    Returns:
        DataFrame com dados processados
    """
    if not conteudo_bytes or len(conteudo_bytes) == 0:
        raise ValueError("Arquivo Espelho está vazio")
    
    df = pd.read_csv(
        BytesIO(conteudo_bytes),
        dtype=str,
        encoding='latin1',
        sep=';',
        on_bad_lines='skip'
    )
    
    if df.empty:
        raise ValueError("Arquivo Espelho resultou em DataFrame vazio")
    
    # Limpa nomes das colunas
    df.columns = [col.strip() for col in df.columns]
    
    return df


def encontrar_coluna(df: pd.DataFrame, candidatos: List[str]) -> Optional[str]:
    """
    Encontra coluna no DataFrame baseado em lista de candidatos.
    
    Args:
        df: DataFrame
        candidatos: Lista de nomes possíveis para a coluna
        
    Returns:
        Nome da coluna encontrada ou None
    """
    cols_map_norm = {normalizar_texto(c): c for c in df.columns}
    
    for key in candidatos:
        # Busca por normalização
        if normalizar_texto(key) in cols_map_norm:
            return cols_map_norm[normalizar_texto(key)]
        
        # Busca literal case-insensitive
        literal_lower = next((c for c in df.columns if c.lower() == key.lower()), None)
        if literal_lower:
            return literal_lower
        
        # Busca parcial
        for col in df.columns:
            if key.upper() in col.upper():
                return col
    
    return None


def encontrar_coluna_valor_teto(df_columns: List[str]) -> Optional[str]:
    """
    Busca robusta para a coluna de valor no arquivo Teto/Espelho.
    
    Args:
        df_columns: Lista de nomes de colunas
        
    Returns:
        Nome da coluna encontrada ou None
    """
    # Prioridade 1: Total Orçado (aceita 'ORAADO', 'ORCADO', etc.)
    for col_orig in df_columns:
        col_limpo = normalizar_texto(col_orig).replace(' ', '')
        if 'TOTAL' in col_limpo and ('ORAADO' in col_limpo or 'ORCADO' in col_limpo):
            return col_orig
    
    # Prioridade 2: Orçamentário
    for col_orig in df_columns:
        col_limpo = normalizar_texto(col_orig).replace(' ', '')
        if 'ORAAMENTARIO' in col_limpo or 'ORCAMENTARIO' in col_limpo:
            return col_orig
    
    # Prioridade 3: Outras variações
    for col_orig in df_columns:
        col_limpo = normalizar_texto(col_orig).replace(' ', '')
        if 'TETO' in col_limpo and 'VALOR' in col_limpo:
            return col_orig
        if 'VLRTOTAL' in col_limpo or 'VALORTOTAL' in col_limpo:
            return col_orig
        if 'VALORMON' in col_limpo:
            return col_orig
        if 'VALORFINANCEIRO' in col_limpo:
            return col_orig
    
    return None
