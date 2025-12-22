import React from 'react';
import { formatarBRL, formatarNumero, formatarPercentual, getCorExecucao } from '../utils/formatters';
import type { LinhaTabela } from '../types';

interface DataTableProps {
  data: LinhaTabela[];
  loading: boolean;
  onDownload: () => void;
}

const DataTable: React.FC<DataTableProps> = ({ data, loading, onDownload }) => {
  if (loading) {
    return <div className="h-64 bg-gray-100 rounded-lg animate-pulse"></div>;
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
        <p className="text-gray-500">Nenhum dado disponível</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">📋 Detalhes da Execução por Unidade</h2>
        <button
          onClick={onDownload}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <span>⬇️</span>
          <span>Baixar CSV</span>
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Unidade</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">CNES</th>
              <th className="px-4 py-3 text-right font-semibold text-gray-700">QTD Orçada</th>
              <th className="px-4 py-3 text-right font-semibold text-gray-700">Valor Orçado</th>
              <th className="px-4 py-3 text-right font-semibold text-gray-700">QTD Aprov.</th>
              <th className="px-4 py-3 text-right font-semibold text-gray-700">Valor Aprov.</th>
              <th className="px-4 py-3 text-right font-semibold text-gray-700">Saldo</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-700">Execução %</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={row.cnes} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-4 py-3 text-gray-800 font-medium">{row.unidade}</td>
                <td className="px-4 py-3 text-gray-600">{row.cnes}</td>
                <td className="px-4 py-3 text-right text-gray-700">{formatarNumero(row.qtd_teto)}</td>
                <td className="px-4 py-3 text-right text-gray-700">{formatarBRL(row.valor_teto)}</td>
                <td className="px-4 py-3 text-right text-gray-700">{formatarNumero(row.qtd_aprovada)}</td>
                <td className="px-4 py-3 text-right text-gray-700">{formatarBRL(row.valor_aprovado)}</td>
                <td
                  className="px-4 py-3 text-right font-semibold"
                  style={{ color: row.saldo < 0 ? '#1abc9c' : '#e74c3c' }}
                >
                  {formatarBRL(row.saldo)}
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="flex items-center justify-center gap-2">
                    <span
                      className="font-bold"
                      style={{ color: getCorExecucao(row.percentual_execucao) }}
                    >
                      {formatarPercentual(row.percentual_execucao)}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;
