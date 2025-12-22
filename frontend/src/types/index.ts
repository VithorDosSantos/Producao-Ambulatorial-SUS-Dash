/**
 * Tipos de dados do Dashboard SIA/SUS
 */

export interface KPIData {
  teto_total_valor: number;
  teto_total_qtd: number;
  producao_aprovada_valor: number;
  producao_aprovada_qtd: number;
  producao_apresentada_valor: number;
  producao_apresentada_qtd: number;
  saldo: number;
  percentual_execucao: number;
  saldo_percentual: number;
}

export interface UnidadeProducao {
  unidade: string;
  cnes: string;
  valor_teto: number;
  valor_aprovado: number;
  valor_apresentado: number;
  percentual_execucao: number;
}

export interface CategoriaDistribuicao {
  categoria: string;
  valor_producao: number;
  percentual_execucao: number;
}

export interface TendenciaMensal {
  mes: string;
  mes_codigo: string;
  mes_ordem: string;
  valor_aprovado: number;
  valor_apresentado: number;
  valor_teto: number;
  percentual_execucao: number;
}

export interface LinhaTabela {
  unidade: string;
  cnes: string;
  categoria: string;
  qtd_teto: number;
  valor_teto: number;
  qtd_apresentada: number;
  valor_apresentado: number;
  qtd_aprovada: number;
  valor_aprovado: number;
  saldo: number;
  percentual_execucao: number;
}

export interface Competencia {
  codigo: string;
  nome: string;
  ordem: string;
}

export interface Unidade {
  nome: string;
  cnes: string;
}

export interface FiltrosData {
  competencias: Competencia[];
  categorias: string[];
  unidades: Unidade[];
}

export interface UploadResponse {
  success: boolean;
  message: string;
  detalhes?: any;
}
