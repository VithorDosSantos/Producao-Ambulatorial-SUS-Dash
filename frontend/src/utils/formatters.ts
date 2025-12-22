/**
 * Funções utilitárias para formatação
 */

export function formatarBRL(valor: number): string {
  if (valor === 0 || valor === null) return 'R$ 0,00';
  
  try {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor);
  } catch {
    return 'R$ 0,00';
  }
}

export function formatarNumero(valor: number): string {
  if (valor === 0 || valor === null) return '0';
  
  try {
    return new Intl.NumberFormat('pt-BR').format(valor);
  } catch {
    return '0';
  }
}

export function formatarPercentual(valor: number): string {
  if (valor === null || valor === undefined) return '0,0%';
  
  try {
    return `${valor.toFixed(1).replace('.', ',')}%`;
  } catch {
    return '0,0%';
  }
}

export function getCorExecucao(percentual: number): string {
  if (percentual >= 80) return '#2ecc71'; // Verde
  if (percentual >= 50) return '#f39c12'; // Laranja
  return '#e74c3c'; // Vermelho
}
