"""
Funções auxiliares e utilitárias reutilizáveis
"""
import unicodedata
import re
from typing import Optional


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto removendo acentos e caracteres especiais.
    
    Args:
        texto: Texto a ser normalizado
        
    Returns:
        Texto normalizado em maiúsculas
    """
    if not isinstance(texto, str):
        return str(texto)
    
    text_norm = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return ''.join(e for e in text_norm if e.isalnum() or e.isspace() or e == '_').strip().upper()


def apenas_digitos(texto: str) -> str:
    """Extrai apenas os dígitos de uma string."""
    return ''.join(filter(str.isdigit, str(texto)))


def formatar_brl(valor: float) -> str:
    """
    Formata valor monetário para padrão brasileiro.
    
    Args:
        valor: Valor numérico
        
    Returns:
        String formatada (ex: "R$ 1.234,56")
    """
    if valor == 0 or valor is None:
        return "R$ 0,00"
    try:
        return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


def formatar_geral(valor: float) -> str:
    """
    Formata número inteiro para padrão brasileiro.
    
    Args:
        valor: Valor numérico
        
    Returns:
        String formatada (ex: "1.234")
    """
    if valor == 0 or valor is None:
        return "0"
    try:
        return "{:,.0f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0"


def formatar_competencia_nome(comp_code: str) -> str:
    """
    Formata código de competência para nome legível.
    
    Args:
        comp_code: Código da competência (ex: "2501")
        
    Returns:
        String formatada (ex: "2501 - JAN/25")
    """
    comp_limpo = apenas_digitos(str(comp_code).strip())
    
    if len(comp_limpo) == 4:
        mes_num = comp_limpo[2:]
        prefix_display = comp_limpo[:2]
    elif len(comp_limpo) == 6:
        mes_num = comp_limpo[4:]
        prefix_display = comp_limpo[2:4]
    else:
        return comp_code
    
    meses_abrev = {
        '01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'ABR', 
        '05': 'MAI', '06': 'JUN', '07': 'JUL', '08': 'AGO', 
        '09': 'SET', '10': 'OUT', '11': 'NOV', '12': 'DEZ'
    }
    
    nome_mes = meses_abrev.get(mes_num.zfill(2), 'INV')
    return f"{comp_limpo} - {nome_mes}/{prefix_display}"


def get_mes_ano_competencia(cmp_value: str) -> str:
    """
    Converte competência para formato YYYYMM para ordenação.
    
    Args:
        cmp_value: Código da competência
        
    Returns:
        String no formato YYYYMM
    """
    try:
        cmp_str = apenas_digitos(str(cmp_value))
        if len(cmp_str) == 4:
            cmp_str = "20" + cmp_str
        if len(cmp_str) != 6:
            return "999999"
        return cmp_str
    except Exception:
        return "999999"


def get_color_hex(execucao_perc: float) -> str:
    """
    Retorna cor hex baseada no percentual de execução.
    
    Args:
        execucao_perc: Percentual de execução (0-100)
        
    Returns:
        Código de cor hexadecimal
    """
    if execucao_perc >= 80:
        return '#2ecc71'  # Verde
    elif execucao_perc >= 50:
        return '#f39c12'  # Laranja
    else:
        return '#e74c3c'  # Vermelho
