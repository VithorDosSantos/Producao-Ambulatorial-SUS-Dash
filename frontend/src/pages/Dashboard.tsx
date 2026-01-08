import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import Filters from '../components/Filters';
import KPICard from '../components/KPICard';
import BarChart from '../components/BarChart';
import DonutChart from '../components/DonutChart';
import LineChart from '../components/LineChart';
import DataTable from '../components/DataTable';
import type {
  KPIData,
  UnidadeProducao,
  CategoriaDistribuicao,
  TendenciaMensal,
  LinhaTabela,
  Competencia,
  Unidade
} from '../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const isLoadingRef = useRef(false);
  const loadTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Filtros
  const [competencias, setCompetencias] = useState<Competencia[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [unidades, setUnidades] = useState<Unidade[]>([]);

  // Seleções
  const [selectedCompetencias, setSelectedCompetencias] = useState<string[]>([]);
  const [selectedCategorias, setSelectedCategorias] = useState<string[]>([]);
  const [selectedUnidades, setSelectedUnidades] = useState<string[]>([]);

  // Dados
  const [kpiData, setKpiData] = useState<KPIData | null>(null);
  const [unidadeData, setUnidadeData] = useState<UnidadeProducao[]>([]);
  const [categoriaData, setCategoriaData] = useState<CategoriaDistribuicao[]>([]);
  const [tendenciaData, setTendenciaData] = useState<TendenciaMensal[]>([]);
  const [tabelaData, setTabelaData] = useState<LinhaTabela[]>([]);

  // Aba ativa
  const [activeTab, setActiveTab] = useState<'visao' | 'tendencia' | 'tabela'>('visao');

  const loadFiltros = async () => {
    try {
      const data = await apiService.getTodosFiltros();
      
      if (!data.competencias || data.competencias.length === 0) {
        alert('Erro: Nenhuma competência foi retornada do servidor');
        return;
      }
      
      setCompetencias(data.competencias);
      setCategorias(data.categorias);
      setUnidades(data.unidades);
      
      const codigosCompetencias = data.competencias.map(c => c.codigo);
      setSelectedCompetencias(codigosCompetencias);
    } catch (error) {
      console.error('Erro ao carregar filtros:', error);
      alert('Erro ao carregar filtros: ' + (error as any).message);
    }
  };

  const loadData = async () => {
    if (selectedCompetencias.length === 0) return;

    // Prevenir múltiplas chamadas simultâneas
    if (isLoadingRef.current) return;

    isLoadingRef.current = true;
    setLoading(true);
    try {
      const [kpi, unidade, categoria, tendencia, tabela] = await Promise.all([
        apiService.getKPIs(selectedCompetencias, selectedCategorias, selectedUnidades),
        apiService.getProducaoPorUnidade(selectedCompetencias, selectedCategorias, selectedUnidades, 10),
        apiService.getDistribuicaoCategorias(selectedCompetencias, selectedCategorias, selectedUnidades),
        apiService.getTendenciaMensal(selectedCompetencias, selectedCategorias, selectedUnidades),
        apiService.getTabelaDetalhada(selectedCompetencias, selectedCategorias, selectedUnidades),
      ]);

      console.log('[Dashboard] KPIs recebidos:', kpi);
      console.log('[Dashboard] Unidades recebidas:', unidade);
      console.log('[Dashboard] Categorias recebidas:', categoria);
      console.log('[Dashboard] Tendência recebida:', tendencia);
      console.log('[Dashboard] Tabela recebida:', tabela?.length, 'linhas');

      setKpiData(kpi);
      setUnidadeData(unidade);
      setCategoriaData(categoria);
      setTendenciaData(tendencia);
      setTabelaData(tabela);
    } catch (error: any) {
      console.error('Erro ao carregar dados:', error);
      alert(error.response?.data?.detail || 'Erro ao carregar dados do banco de dados');
    } finally {
      setLoading(false);
      setInitialLoad(false);
      isLoadingRef.current = false;
    }
  };

  // Carrega filtros ao montar o componente
  useEffect(() => {
    loadFiltros();
  }, []);

  // Carrega dados quando filtros mudarem (com debounce)
  useEffect(() => {
    // Limpar timeout anterior (debounce)
    if (loadTimeoutRef.current) {
      clearTimeout(loadTimeoutRef.current);
    }
    
    if (selectedCompetencias.length > 0) {
      loadTimeoutRef.current = setTimeout(() => {
        loadData();
      }, 800); // 800ms de debounce
    }
    
    // Cleanup ao desmontar
    return () => {
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
      }
    };
  }, [selectedCompetencias, selectedCategorias, selectedUnidades]);

  const handleDownload = () => {
    const url = apiService.getDownloadCSVUrl(selectedCompetencias, selectedCategorias, selectedUnidades);
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 pb-12">
      {/* Header Profissional */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex-shrink-0 hover:opacity-80 transition-opacity"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Sistema de Gestão Estratégica SIA/SUS</h1>
                <p className="text-sm text-gray-600 mt-0.5">Análise de Produção Ambulatorial e Execução Orçamentária</p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-sm">
              <div className="px-4 py-2 bg-green-50 text-green-700 rounded-lg border border-green-200">
                <span className="font-semibold">PostgreSQL Conectado</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 mt-8">
        {/* Filtros */}
        <Filters
          competencias={competencias}
          categorias={categorias}
          unidades={unidades}
          selectedCompetencias={selectedCompetencias}
          selectedCategorias={selectedCategorias}
          selectedUnidades={selectedUnidades}
          onCompetenciasChange={setSelectedCompetencias}
          onCategoriasChange={setSelectedCategorias}
          onUnidadesChange={setSelectedUnidades}
          loading={loading}
        />

        {/* KPIs */}
        <KPICard data={kpiData} loading={loading} />

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8 border border-gray-200">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('visao')}
              className={`flex-1 py-4 px-6 font-semibold transition-all relative group ${
                activeTab === 'visao'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 bg-white hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Visão Geral</span>
              </div>
              {activeTab === 'visao' && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-600"></div>
              )}
            </button>
            <button
              onClick={() => setActiveTab('tendencia')}
              className={`flex-1 py-4 px-6 font-semibold transition-all relative group ${
                activeTab === 'tendencia'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 bg-white hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                <span>Tendência Mensal</span>
              </div>
              {activeTab === 'tendencia' && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-600"></div>
              )}
            </button>
            <button
              onClick={() => setActiveTab('tabela')}
              className={`flex-1 py-4 px-6 font-semibold transition-all relative group ${
                activeTab === 'tabela'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 bg-white hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Dados Detalhados</span>
              </div>
              {activeTab === 'tabela' && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-600"></div>
              )}
            </button>
          </div>

          <div className="p-6">
            {activeTab === 'visao' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <BarChart data={unidadeData} loading={loading} />
                <DonutChart
                  data={categoriaData}
                  execucaoGlobal={kpiData?.percentual_execucao || 0}
                  loading={loading}
                />
              </div>
            )}

            {activeTab === 'tendencia' && (
              <LineChart data={tendenciaData} loading={loading} />
            )}

            {activeTab === 'tabela' && (
              <DataTable data={tabelaData} loading={loading} onDownload={handleDownload} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
