import React from 'react';
import ReactECharts from 'echarts-for-react';
import { formatarBRL } from '../utils/formatters';
import type { UnidadeProducao } from '../types';

interface BarChartProps {
  data: UnidadeProducao[];
  loading: boolean;
}

const BarChart: React.FC<BarChartProps> = ({ data, loading }) => {
  if (loading) {
    return <div className="h-96 bg-gray-100 rounded-lg animate-pulse"></div>;
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
        <p className="text-gray-500">Nenhum dado disponível</p>
      </div>
    );
  }

  const option = {
    title: {
      text: 'Performance por Unidade: Valor Aprovado vs. Valor Orçado (Top 10)',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold', color: '#2c3e50' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        let result = `<strong>${params[0].name}</strong><br/>`;
        params.forEach((item: any) => {
          result += `${item.marker} ${item.seriesName}: ${formatarBRL(item.value)}<br/>`;
        });
        return result;
      },
    },
    legend: {
      top: 30,
      data: ['Valor Orçado (Teto)', 'Valor Aprovado'],
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.map((d) => d.unidade.substring(0, 20)),
      axisLabel: { interval: 0, rotate: 45, fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: 'Valor (R$)',
      axisLabel: {
        formatter: (value: number) => `R$ ${(value / 1000).toFixed(0)}k`,
      },
    },
    series: [
      {
        name: 'Valor Orçado (Teto)',
        type: 'bar',
        data: data.map((d) => d.valor_teto),
        itemStyle: { color: '#e74c3c' },
      },
      {
        name: 'Valor Aprovado',
        type: 'bar',
        data: data.map((d) => d.valor_aprovado),
        itemStyle: { color: '#3498db' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '500px' }} />;
};

export default BarChart;
