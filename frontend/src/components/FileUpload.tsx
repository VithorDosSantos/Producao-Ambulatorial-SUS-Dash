import React, { useState } from 'react';
import { apiService } from '../services/api';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [papaFiles, setPapaFiles] = useState<File[]>([]);
  const [espelhoFile, setEspelhoFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handlePapaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPapaFiles(Array.from(e.target.files));
    }
  };

  const handleEspelhoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setEspelhoFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (papaFiles.length === 0 || !espelhoFile) {
      setMessage({ type: 'error', text: 'É necessário selecionar todos os arquivos antes de processar.' });
      return;
    }

    setUploading(true);
    setMessage(null);

    try {
      console.log('[Upload] Enviando arquivos PAPA...');
      await apiService.uploadPAPA(papaFiles);
      console.log('[Upload] PAPA enviado com sucesso');
      
      console.log('[Upload] Enviando arquivo Espelho...');
      await apiService.uploadEspelho(espelhoFile);
      console.log('[Upload] Espelho enviado com sucesso');
      
      setMessage({ type: 'success', text: 'Arquivos processados com sucesso. Carregando dados...' });
      
      // Aguarda 2.5 segundos para garantir que o backend consolidou os dados
      setTimeout(() => {
        console.log('[Upload] Redirecionando para dashboard...');
        onUploadSuccess();
      }, 2500);
    } catch (error: any) {
      console.error('[Upload] Erro:', error);
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Erro ao processar arquivos. Verifique o formato e tente novamente.' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200">
        {/* Header com gradiente sutil */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 px-8 py-6">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900">Importação de Dados SIA/SUS</h2>
              <p className="text-sm text-gray-600 mt-1">Sistema de análise de produção ambulatorial e teto financeiro</p>
            </div>
          </div>
        </div>

        {/* Corpo do formulário */}
        <div className="px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Upload PAPA */}
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <label className="block text-base font-semibold text-gray-900 mb-1">
                    Arquivos PAPA (Produção Ambulatorial)
                  </label>
                  <p className="text-sm text-gray-500 mb-3">
                    Selecione um ou mais arquivos de produção em formato CSV
                  </p>
                  
                  <div className="relative">
                    <input
                      type="file"
                      multiple
                      accept=".csv"
                      onChange={handlePapaChange}
                      className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent file:mr-4 file:py-3 file:px-4 file:rounded-l-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:cursor-pointer transition-colors"
                    />
                  </div>
                  
                  {papaFiles.length > 0 && (
                    <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm font-medium text-blue-900">
                        {papaFiles.length} {papaFiles.length === 1 ? 'arquivo selecionado' : 'arquivos selecionados'}
                      </p>
                      <ul className="mt-2 space-y-1">
                        {papaFiles.slice(0, 3).map((file, index) => (
                          <li key={index} className="text-xs text-blue-700 truncate">• {file.name}</li>
                        ))}
                        {papaFiles.length > 3 && (
                          <li className="text-xs text-blue-700">• e mais {papaFiles.length - 3} arquivo(s)...</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Upload Espelho */}
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <label className="block text-base font-semibold text-gray-900 mb-1">
                    Arquivo Espelho (Teto Financeiro)
                  </label>
                  <p className="text-sm text-gray-500 mb-3">
                    Selecione o arquivo de teto orçamentário em formato CSV
                  </p>
                  
                  <div className="relative">
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleEspelhoChange}
                      className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent file:mr-4 file:py-3 file:px-4 file:rounded-l-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 file:cursor-pointer transition-colors"
                    />
                  </div>
                  
                  {espelhoFile && (
                    <div className="mt-3 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
                      <p className="text-sm font-medium text-indigo-900">Arquivo selecionado</p>
                      <p className="text-xs text-indigo-700 mt-1 truncate">• {espelhoFile.name}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Informações adicionais */}
          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <svg className="w-5 h-5 text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="text-sm text-gray-600">
                <p className="font-medium text-gray-900 mb-1">Requisitos dos arquivos:</p>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Formato: CSV (valores separados por vírgula ou ponto e vírgula)</li>
                  <li>Codificação: UTF-8 ou Latin-1</li>
                  <li>Os arquivos devem seguir o padrão de nomenclatura do DATASUS</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Botão de processamento */}
          <button
            onClick={handleUpload}
            disabled={uploading || papaFiles.length === 0 || !espelhoFile}
            className="w-full py-4 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center justify-center space-x-2"
          >
            {uploading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Processando arquivos...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Processar e Analisar Dados</span>
              </>
            )}
          </button>

          {/* Mensagem de feedback */}
          {message && (
            <div className={`mt-6 p-4 rounded-lg border-l-4 ${
              message.type === 'success' 
                ? 'bg-green-50 border-green-500 text-green-800' 
                : 'bg-red-50 border-red-500 text-red-800'
            }`}>
              <div className="flex items-start space-x-3">
                {message.type === 'success' ? (
                  <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
                <p className="text-sm font-medium">{message.text}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
