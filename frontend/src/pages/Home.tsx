import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Sistema de Gestão Estratégica SIA/SUS</h1>
                <p className="text-sm text-gray-600 mt-1">Análise de Produção Ambulatorial e Execução Orçamentária</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Bem-vindo ao Sistema de Análise SIA/SUS
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Plataforma integrada para monitoramento e análise de dados de produção ambulatorial, 
            execução orçamentária e indicadores de saúde pública.
          </p>
        </div>

        {/* Opções de Fonte de Dados */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Escolha a Fonte de Dados</h3>
            <p className="text-gray-600">Selecione como deseja utilizar o sistema</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Opção 1: Banco de Dados */}
            <div className="bg-white rounded-2xl p-8 shadow-lg border-2 border-gray-200 hover:border-blue-500 transition-all">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                  </svg>
                </div>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3 text-center">Usar Banco de Dados</h4>
              <p className="text-gray-600 mb-6 text-center">
                Acesse dados já importados no PostgreSQL com consultas otimizadas e análises históricas completas.
              </p>
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Dados permanentes e históricos
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Performance otimizada
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Análises complexas
                </div>
              </div>
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:from-blue-700 hover:to-indigo-700 transition-all flex items-center justify-center space-x-2"
              >
                <span>Acessar Dashboard</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>

            {/* Opção 2: Upload de Arquivos CSV */}
            <div className="bg-white rounded-2xl p-8 shadow-lg border-2 border-gray-200 hover:border-green-500 transition-all">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-green-600 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3 text-center">Usar Arquivos PAPA/TETO</h4>
              <p className="text-gray-600 mb-6 text-center">
                Faça upload de arquivos CSV do PAPA e TETO para análise temporária e exploratória de dados.
              </p>
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Análise rápida sem banco
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Formato CSV padrão
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Teste de novos dados
                </div>
              </div>
              <button
                onClick={() => setShowUpload((v) => !v)}
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:from-green-700 hover:to-emerald-700 transition-all flex items-center justify-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>{showUpload ? 'Fechar Upload' : 'Fazer Upload de CSV'}</span>
              </button>
            </div>
          </div>

          {/* Upload Component */}
          {showUpload && (
            <div className="mt-8 max-w-4xl mx-auto">
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 border-2 border-green-200">
                <FileUpload onUploadSuccess={() => {
                  setShowUpload(false);
                  navigate('/dashboard');
                }} />
              </div>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* Card 1 */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200 hover:shadow-xl transition-all">
            <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Análise em Tempo Real</h3>
            <p className="text-gray-600">
              Visualize dados atualizados da produção ambulatorial com filtros avançados por competência, categoria e unidade.
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200 hover:shadow-xl transition-all">
            <div className="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Controle Orçamentário</h3>
            <p className="text-gray-600">
              Monitore execução orçamentária com comparativos entre valores aprovados, apresentados e teto financeiro.
            </p>
          </div>

          {/* Card 3 */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200 hover:shadow-xl transition-all">
            <div className="w-14 h-14 bg-indigo-100 rounded-xl flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Relatórios Detalhados</h3>
            <p className="text-gray-600">
              Gere relatórios completos com gráficos interativos, tendências mensais e exportação de dados em CSV.
            </p>
          </div>
        </div>



        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-12">
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">100%</div>
            <div className="text-sm text-gray-600 font-semibold">Dados Integrados</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">Real-Time</div>
            <div className="text-sm text-gray-600 font-semibold">Atualização</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200 text-center">
            <div className="text-3xl font-bold text-indigo-600 mb-2">PostgreSQL</div>
            <div className="text-sm text-gray-600 font-semibold">Banco de Dados</div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">Seguro</div>
            <div className="text-sm text-gray-600 font-semibold">Governamental</div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="container mx-auto px-6 text-center">
          <p className="text-gray-400">
            © 2025 Sistema de Gestão Estratégica SIA/SUS - Secretaria Municipal de Saúde
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
