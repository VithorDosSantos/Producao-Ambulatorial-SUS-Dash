import React from 'react';
import ReactECharts from 'echarts-for-react';
import { formatarBRL } from '../utils/formatters';
import type { CategoriaDistribuicao } from '../types';

interface DonutChartProps {
  data: CategoriaDistribuicao[];
  execucaoGlobal: number;
  loading: boolean;
}

const DonutChart: React.FC<DonutChartProps> = ({ data, execucaoGlobal, loading }) => {
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
      text: 'Distribuição por Categoria',
      subtext: `Execução Global: ${execucaoGlobal.toFixed(1)}%`,
      left: 'center',
      top: '5%',
      textStyle: { fontSize: 18, fontWeight: 'bold', color: '#2c3e50' },
      subtextStyle: { fontSize: 14, color: '#7f8c8d' },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `<strong>${params.name}</strong><br/>
                Valor: ${formatarBRL(params.value)}<br/>
                Participação: ${params.percent.toFixed(1)}%`;
      },
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      itemGap: 12,
      itemWidth: 14,
      itemHeight: 14,
      textStyle: {
        fontSize: 12,
        lineHeight: 18,
      },
      formatter: (name: string) => {
        const item = data.find((d) => d.categoria === name);
        return `${name}\n${item ? item.percentual_execucao.toFixed(1) : '0'}% exec.`;
      },
    },
    grid: {
      left: '5%',
      right: '30%',
      top: '15%',
      bottom: '5%',
      containLabel: true,
    },
    series: [
      {
        name: 'Produção',
        type: 'pie',
        radius: ['35%', '60%'],
        center: ['40%', '55%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
          },
        },
        labelLine: {
          show: false,
        },
        data: data.map((d) => ({
          value: d.valor_producao,
          name: d.categoria,
        })),
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '550px', width: '100%' }} />;
};

export default DonutChart;
