import React from 'react';
import ReactECharts from 'echarts-for-react';
import { formatarBRL } from '../utils/formatters';
import type { TendenciaMensal } from '../types';

interface LineChartProps {
  data: TendenciaMensal[];
  loading: boolean;
}

const LineChart: React.FC<LineChartProps> = ({ data, loading }) => {
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
      text: 'Histórico Mensal de Produção Aprovada, Apresentada vs. Teto Orçado',
      left: 'center',
      top: '2%',
      textStyle: { fontSize: 16, fontWeight: 'bold', color: '#2c3e50' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        let result = `<strong style="font-size: 14px;">${params[0].axisValue}</strong><br/>`;
        params.forEach((item: any) => {
          result += `${item.marker} <span style="font-weight: 600;">${item.seriesName}:</span> ${formatarBRL(item.value)}<br/>`;
        });
        return result;
      },
    },
    legend: {
      top: '10%',
      data: ['Valor Aprovado', 'Valor Apresentado', 'Valor Teto'],
      itemWidth: 30,
      itemHeight: 14,
      textStyle: { fontSize: 13, fontWeight: 500 },
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '8%',
      top: '22%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.map((d) => d.mes),
      axisLabel: {
        rotate: data.length > 6 ? 45 : 0,
        fontSize: 12,
        fontWeight: 500,
      },
      axisTick: {
        alignWithLabel: true,
      },
    },
    yAxis: {
      type: 'value',
      name: 'Valor (R$)',
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 600,
      },
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 1000000) return `R$ ${(value / 1000000).toFixed(1)}M`;
          if (value >= 1000) return `R$ ${(value / 1000).toFixed(0)}k`;
          return `R$ ${value.toFixed(0)}`;
        },
        fontSize: 11,
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#e0e0e0',
        },
      },
    },
    series: [
      {
        name: 'Valor Teto',
        type: 'bar',
        data: data.map((d) => d.valor_teto),
        itemStyle: { 
          color: '#e3f2fd',
          borderColor: '#2196f3',
          borderWidth: 2,
        },
        barMaxWidth: 60,
        z: 1,
      },
      {
        name: 'Valor Apresentado',
        type: 'bar',
        data: data.map((d) => d.valor_apresentado),
        itemStyle: { 
          color: '#fff3e0',
          borderColor: '#ff9800',
          borderWidth: 2,
        },
        barMaxWidth: 60,
        z: 2,
      },
      {
        name: 'Valor Aprovado',
        type: 'bar',
        data: data.map((d) => d.valor_aprovado),
        itemStyle: { 
          color: '#4caf50',
          borderColor: '#2e7d32',
          borderWidth: 2,
        },
        barMaxWidth: 60,
        z: 3,
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '500px' }} />;
};

export default LineChart;
