/**
 * Serviço de comunicação com a API Backend
 */
import axios, { AxiosInstance } from 'axios';
import type {
  KPIData,
  UnidadeProducao,
  CategoriaDistribuicao,
  TendenciaMensal,
  LinhaTabela,
  FiltrosData,
  UploadResponse
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    // Usa a URL do backend em produção ou localhost em desenvolvimento
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      paramsSerializer: {
        indexes: null, // Serializa arrays como param=val1&param=val2
      },
    });
  }

  // ==================== UPLOAD ====================

  async uploadPAPA(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await this.api.post('/upload/papa', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async uploadEspelho(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post('/upload/espelho', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getUploadStatus() {
    const response = await this.api.get('/upload/status');
    return response.data;
  }

  async resetDados() {
    const response = await this.api.delete('/upload/reset');
    return response.data;
  }

  // ==================== FILTROS ====================

  async getCompetencias() {
    const response = await this.api.get('/filtros/competencias');
    return response.data;
  }

  async getCategorias() {
    const response = await this.api.get('/filtros/categorias');
    return response.data;
  }

  async getUnidades(categorias?: string[]) {
    const params = categorias ? { categorias } : {};
    const response = await this.api.get('/filtros/unidades', { params });
    return response.data;
  }

  async getTodosFiltros(): Promise<FiltrosData> {
    console.log('[API] Fazendo requisição para /filtros/todos');
    const response = await this.api.get('/filtros/todos');
    console.log('[API] Resposta recebida:', response);
    const data = response.data;
    console.log('[API] Dados:', data);
    return data;
  }

  // ==================== KPIs ====================

  async getKPIs(
    competencias: string[],
    categorias?: string[],
    unidades?: string[]
  ): Promise<KPIData> {
    const params: any = { competencias };
    if (categorias && categorias.length > 0) params.categorias = categorias;
    if (unidades && unidades.length > 0) params.unidades = unidades;

    const response = await this.api.get('/kpis', { params });
    return response.data;
  }

  // ==================== VISÃO GERAL ====================

  async getProducaoPorUnidade(
    competencias: string[],
    categorias?: string[],
    unidades?: string[],
    top: number = 10
  ): Promise<UnidadeProducao[]> {
    const params: any = { competencias, top };
    if (categorias && categorias.length > 0) params.categorias = categorias;
    if (unidades && unidades.length > 0) params.unidades = unidades;

    const response = await this.api.get('/visao-geral/unidades', { params });
    return response.data;
  }

  async getDistribuicaoCategorias(
    competencias: string[],
    categorias?: string[],
    unidades?: string[]
  ): Promise<CategoriaDistribuicao[]> {
    const params: any = { competencias };
    if (categorias && categorias.length > 0) params.categorias = categorias;
    if (unidades && unidades.length > 0) params.unidades = unidades;

    const response = await this.api.get('/visao-geral/categorias', { params });
    return response.data;
  }

  // ==================== TENDÊNCIA ====================

  async getTendenciaMensal(
    competencias: string[],
    categorias?: string[],
    unidades?: string[]
  ): Promise<TendenciaMensal[]> {
    const params: any = { competencias };
    if (categorias && categorias.length > 0) params.categorias = categorias;
    if (unidades && unidades.length > 0) params.unidades = unidades;

    const response = await this.api.get('/tendencia-mensal', { params });
    return response.data;
  }

  // ==================== TABELA ====================

  async getTabelaDetalhada(
    competencias: string[],
    categorias?: string[],
    unidades?: string[]
  ): Promise<LinhaTabela[]> {
    const params: any = { competencias };
    if (categorias && categorias.length > 0) params.categorias = categorias;
    if (unidades && unidades.length > 0) params.unidades = unidades;

    const response = await this.api.get('/tabela-detalhada', { params });
    return response.data;
  }

  getDownloadCSVUrl(
    competencias: string[],
    categorias?: string[],
    unidades?: string[]
  ): string {
    const params = new URLSearchParams();
    competencias.forEach(c => params.append('competencias', c));
    if (categorias) categorias.forEach(c => params.append('categorias', c));
    if (unidades) unidades.forEach(u => params.append('unidades', u));

    return `/api/tabela-detalhada/download/csv?${params.toString()}`;
  }
}

export const apiService = new ApiService();
