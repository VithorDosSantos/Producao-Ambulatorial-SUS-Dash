"""
Modelos de dados (schemas) para validação e documentação da API
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class KPIResponse(BaseModel):
    """Resposta com KPIs globais"""
    teto_total_valor: float = Field(..., description="Valor total do teto orçamentário")
    teto_total_qtd: int = Field(..., description="Quantidade total orçada")
    producao_aprovada_valor: float = Field(..., description="Valor total aprovado")
    producao_aprovada_qtd: int = Field(..., description="Quantidade total aprovada")
    producao_apresentada_valor: float = Field(..., description="Valor total apresentado")
    producao_apresentada_qtd: int = Field(..., description="Quantidade total apresentada")
    saldo: float = Field(..., description="Saldo monetário (teto - produção)")
    percentual_execucao: float = Field(..., description="Percentual de execução")
    saldo_percentual: float = Field(..., description="Percentual restante")


class UnidadeProducao(BaseModel):
    """Dados de produção por unidade"""
    unidade: str
    cnes: str
    valor_teto: float
    valor_aprovado: float
    valor_apresentado: float
    percentual_execucao: float


class CategoriaDistribuicao(BaseModel):
    """Distribuição por categoria"""
    categoria: str
    valor_producao: float
    percentual_execucao: float


class TendenciaMensal(BaseModel):
    """Dados de tendência mensal"""
    mes: str
    mes_codigo: str
    mes_ordem: str
    valor_aprovado: float
    valor_apresentado: float
    valor_teto: float
    percentual_execucao: float


class LinhaTabela(BaseModel):
    """Linha da tabela detalhada"""
    unidade: str
    cnes: str
    categoria: str
    qtd_teto: int
    valor_teto: float
    qtd_apresentada: int
    valor_apresentado: float
    qtd_aprovada: int
    valor_aprovado: float
    saldo: float
    percentual_execucao: float


class FiltrosResponse(BaseModel):
    """Resposta com opções de filtros"""
    competencias: List[dict] = Field(..., description="Lista de competências disponíveis")
    categorias: List[str] = Field(..., description="Lista de categorias")
    unidades: List[dict] = Field(..., description="Lista de unidades com CNES")


class UploadResponse(BaseModel):
    """Resposta do upload de arquivos"""
    success: bool
    message: str
    detalhes: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada"""
    error: bool = True
    message: str
    detalhes: Optional[str] = None
