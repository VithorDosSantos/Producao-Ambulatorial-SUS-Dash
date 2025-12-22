"""
Serviço de limpeza e normalização de dados
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import os


def limpar_coluna_numerica(serie: pd.Series) -> pd.Series:
    """
    Limpa e prepara colunas monetárias/numéricas brasileiras para conversão float.
    
    Args:
        serie: Série Pandas com valores monetários
        
    Returns:
        Série limpa pronta para conversão numérica
    """
    s_str = serie.astype(str)
    s_clean = s_str.str.replace('R$', '', regex=False).str.strip()
    s_clean = s_clean.str.replace('.', '', regex=False)
    s_clean = s_clean.str.replace(',', '.', regex=False)
    return s_clean.fillna('0')


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduz o uso de memória convertendo colunas para tipos menores.
    
    Args:
        df: DataFrame a ser otimizado
        
    Returns:
        DataFrame otimizado
    """
    for col in df.columns:
        # Downcast floats
        if df[col].dtype == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float', errors='ignore')
        # Downcast integers
        elif df[col].dtype == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer', errors='ignore')
    return df


def classificar_unidade(
    nome: str, 
    cnes: Optional[str] = None, 
    mapa_categorias: Optional[Dict[str, str]] = None
) -> str:
    """
    Classifica unidade por categoria usando mapeamento CSV ou lógica padrão.
    
    Args:
        nome: Nome da unidade
        cnes: Código CNES da unidade
        mapa_categorias: Dicionário com mapeamento CNES -> Categoria
        
    Returns:
        Categoria com emoji
    """
    from ..utils.helpers import normalizar_texto
    
    # Se houver mapeamento e CNES, usa o mapeamento
    if mapa_categorias and cnes and cnes in mapa_categorias:
        categoria = mapa_categorias[cnes]
        # Adiciona emojis às categorias
        emojis = {
            'UPA': '🚨 UPA',
            'HOSPITAL': '🏥 HOSPITAL',
            'SAMU': '🚑 SAMU',
            'CASA ESPECIALIZADA': '🏢 CASA ESPECIALIZADA',
            'DEPARTAMENTO': '📋 DEPARTAMENTO',
            'UNIDADE BASICA DE SAUDE': '💉 UNIDADE BASICA DE SAUDE'
        }
        return emojis.get(categoria, f'📍 {categoria}')
    
    # Lógica padrão (fallback)
    nome_norm = normalizar_texto(nome)
    
    if 'UPA' in nome_norm:
        return '🚨 UPA'
    if 'HOSP' in nome_norm or 'SANTA CASA' in nome_norm:
        return '🏥 HOSPITAL'
    if 'SAMU' in nome_norm or 'USA' in nome_norm or 'USB' in nome_norm or 'MOTOLANCIA' in nome_norm or 'AMBULANCHA' in nome_norm:
        return '🚑 SAMU'
    if 'CAPS' in nome_norm or 'CASA' in nome_norm or 'CEO' in nome_norm or 'CENTRO DE ESPECIALIDADES' in nome_norm or 'CTA' in nome_norm:
        return '🏢 CASA ESPECIALIZADA'
    if 'DERE' in nome_norm or 'DEPARTAMENTO' in nome_norm or 'CENTRAL DE REGULACAO' in nome_norm:
        return '📋 DEPARTAMENTO'
    if 'UBS' in nome_norm or 'UMS' in nome_norm or 'ESF' in nome_norm or 'UNIDADE' in nome_norm:
        return '💉 UNIDADE BASICA DE SAUDE'
    
    return '📍 OUTROS'


def carregar_mapa_categorias(caminho_csv: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Carrega mapeamento de CNES -> Categoria do arquivo filtro_CATEGORIA.csv.
    
    Args:
        caminho_csv: Caminho para o arquivo CSV (opcional)
        
    Returns:
        Dicionário com mapeamento ou None se não encontrar
    """
    if caminho_csv is None:
        # Tenta encontrar o arquivo na raiz do projeto
        caminho_csv = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'filtro_CATEGORIA.csv')
    
    try:
        if os.path.exists(caminho_csv):
            df_cat = pd.read_csv(caminho_csv, sep=';', encoding='latin1', dtype=str)
            df_cat.columns = [c.strip() for c in df_cat.columns]
            
            if 'Num_CNES' in df_cat.columns and 'Categoria' in df_cat.columns:
                df_cat['Num_CNES'] = df_cat['Num_CNES'].astype(str).str.strip()
                df_cat['Categoria'] = df_cat['Categoria'].str.strip().str.upper()
                return dict(zip(df_cat['Num_CNES'], df_cat['Categoria']))
    except Exception:
        pass
    
    return None
