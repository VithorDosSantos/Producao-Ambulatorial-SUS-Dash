import React from 'react';
import { formatarBRL, formatarNumero, formatarPercentual, getCorExecucao } from '../utils/formatters';
import type { KPIData } from '../types';

interface KPICardProps {
  data: KPIData | null;
  loading: boolean;
}

const KPICard: React.FC<KPICardProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-2xl p-6 shadow-lg animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!data) return null;

  const execColor = getCorExecucao(data.percentual_execucao);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {/* Card 1: ORÇADO */}
      <div className="bg-gradient-to-br from-blue-50 to-white rounded-2xl p-6 shadow-lg border border-blue-200 hover:shadow-xl transition-all hover:scale-105">
        <div className="flex items-center space-x-3 mb-4">
          <div className="flex-shrink-0 w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900 uppercase tracking-wide">
            Orçado
          </h3>
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Quantidade Orçada</p>
            <p className="text-2xl font-bold text-blue-600">{formatarNumero(data.teto_total_qtd)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Valor Teto</p>
            <p className="text-2xl font-bold text-blue-600">{formatarBRL(data.teto_total_valor)}</p>
          </div>
        </div>
      </div>

      {/* Card 2: APRESENTADO */}
      <div className="bg-gradient-to-br from-orange-50 to-white rounded-2xl p-6 shadow-lg border border-orange-200 hover:shadow-xl transition-all hover:scale-105">
        <div className="flex items-center space-x-3 mb-4">
          <div className="flex-shrink-0 w-10 h-10 bg-orange-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900 uppercase tracking-wide">
            Apresentado
          </h3>
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Quantidade Apresentada</p>
            <p className="text-2xl font-bold text-orange-600">{formatarNumero(data.producao_apresentada_qtd)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Valor Apresentado</p>
            <p className="text-2xl font-bold text-orange-600">{formatarBRL(data.producao_apresentada_valor)}</p>
          </div>
        </div>
      </div>

      {/* Card 3: APROVADO */}
      <div className="bg-gradient-to-br from-green-50 to-white rounded-2xl p-6 shadow-lg border border-green-200 hover:shadow-xl transition-all hover:scale-105">
        <div className="flex items-center space-x-3 mb-4">
          <div className="flex-shrink-0 w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900 uppercase tracking-wide">
            Aprovado
          </h3>
        </div>
        <div className="space-y-3 mb-3">
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Quantidade Aprovada</p>
            <p className="text-2xl font-bold text-green-600">{formatarNumero(data.producao_aprovada_qtd)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Valor Aprovado</p>
            <p className="text-2xl font-bold text-green-600">{formatarBRL(data.producao_aprovada_valor)}</p>
          </div>
        </div>
        
        {/* Execução */}
        <div className="mt-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-gray-700">Execução:</span>
            <span className="text-lg font-bold" style={{ color: execColor }}>
              {formatarPercentual(data.percentual_execucao)}
            </span>
          </div>
          
          {/* Barra de progresso */}
          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(data.percentual_execucao, 100)}%`,
                backgroundColor: execColor,
              }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KPICard;
