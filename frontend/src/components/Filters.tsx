import React, { useState } from 'react';
import type { Competencia, Unidade } from '../types';

interface FiltersProps {
  competencias: Competencia[];
  categorias: string[];
  unidades: Unidade[];
  selectedCompetencias: string[];
  selectedCategorias: string[];
  selectedUnidades: string[];
  onCompetenciasChange: (values: string[]) => void;
  onCategoriasChange: (values: string[]) => void;
  onUnidadesChange: (values: string[]) => void;
  loading: boolean;
}

const Filters: React.FC<FiltersProps> = ({
  competencias,
  categorias,
  unidades,
  selectedCompetencias,
  selectedCategorias,
  selectedUnidades,
  onCompetenciasChange,
  onCategoriasChange,
  onUnidadesChange,
  loading,
}) => {
  const [expanded, setExpanded] = useState(true);

  const handleCheckboxChange = (
    value: string,
    selectedValues: string[],
    onChange: (values: string[]) => void
  ) => {
    if (selectedValues.includes(value)) {
      onChange(selectedValues.filter(v => v !== value));
    } else {
      onChange([...selectedValues, value]);
    }
  };

  const FilterCheckbox: React.FC<{
    id: string;
    label: string;
    checked: boolean;
    onChange: () => void;
    disabled?: boolean;
  }> = ({ id, label, checked, onChange, disabled }) => (
    <label
      className={`flex items-center p-2.5 rounded-lg cursor-pointer transition-all
        ${checked ? 'bg-blue-50 border-2 border-blue-500' : 'bg-white border-2 border-gray-200 hover:border-gray-300'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-sm'}
      `}
    >
      <input
        type="checkbox"
        id={id}
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="w-5 h-5 text-blue-600 bg-white border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
      />
      <span className={`ml-3 text-sm font-medium ${checked ? 'text-blue-900' : 'text-gray-700'}`}>
        {label}
      </span>
    </label>
  );

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
      <div className="flex justify-between items-center mb-4 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center space-x-3">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <h2 className="text-xl font-bold text-gray-900">Filtros de Análise</h2>
        </div>
        <span className="text-xl text-gray-500">{expanded ? '▼' : '▶'}</span>
      </div>

      {expanded && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Competências */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              Competência (Mês)
            </label>
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 max-h-60 overflow-y-auto space-y-2 custom-scrollbar">
              {competencias.map((comp) => (
                <FilterCheckbox
                  key={comp.codigo}
                  id={`comp-${comp.codigo}`}
                  label={comp.nome}
                  checked={selectedCompetencias.includes(comp.codigo)}
                  onChange={() => handleCheckboxChange(comp.codigo, selectedCompetencias, onCompetenciasChange)}
                  disabled={loading}
                />
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">Ctrl/Cmd + clique para múltipla seleção</p>
          </div>

          {/* Categorias */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              Categoria
            </label>
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 max-h-60 overflow-y-auto space-y-2 custom-scrollbar">
              {categorias.map((cat) => (
                <FilterCheckbox
                  key={cat}
                  id={`cat-${cat}`}
                  label={cat}
                  checked={selectedCategorias.includes(cat)}
                  onChange={() => handleCheckboxChange(cat, selectedCategorias, onCategoriasChange)}
                  disabled={loading}
                />
              ))}
            </div>
          </div>

          {/* Unidades */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-3">
              Unidade de Saúde
            </label>
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 max-h-60 overflow-y-auto space-y-2 custom-scrollbar">
              {unidades.map((uni) => (
                <FilterCheckbox
                  key={uni.cnes}
                  id={`uni-${uni.cnes}`}
                  label={uni.nome}
                  checked={selectedUnidades.includes(uni.cnes)}
                  onChange={() => handleCheckboxChange(uni.cnes, selectedUnidades, onUnidadesChange)}
                  disabled={loading}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
    </div>
  );
};

export default Filters;
