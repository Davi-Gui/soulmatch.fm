import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

interface Features {
  danceability: number;
  energy: number;
  valence: number;
  acousticness: number;
  instrumentalness: number;
  liveness: number;
  speechiness: number;
}

interface Props {
  user1Name: string;
  user2Name: string;
  features1: Features;
  features2: Features;
}

// Mapeamento para nomes bonitos em Português
const FEATURE_LABELS: { [key: string]: string } = {
  danceability: 'Dançabilidade',
  energy: 'Energia',
  valence: 'Positividade',
  acousticness: 'Acústico',
  instrumentalness: 'Instrumental',
  liveness: 'Ao Vivo',
  speechiness: 'Fala/Letra'
};

const ComparisonChart: React.FC<Props> = ({ user1Name, user2Name, features1, features2 }) => {
  // Estado para controlar quais filtros estão ativos
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);

  // Carrega todas as chaves inicialmente
  useEffect(() => {
    if (features1) {
      setSelectedKeys(Object.keys(features1));
    }
  }, [features1]);

  if (!features1 || !features2) {
    return <div style={{color: 'white', textAlign: 'center', padding: '20px'}}>Dados insuficientes</div>;
  }

  // Função para ligar/desligar uma característica
  const toggleFeature = (key: string) => {
    if (selectedKeys.includes(key)) {
      // Se já tem, remove (mas impede de remover o último para não quebrar o gráfico)
      if (selectedKeys.length > 3) {
        setSelectedKeys(selectedKeys.filter(k => k !== key));
      }
    } else {
      // Se não tem, adiciona
      setSelectedKeys([...selectedKeys, key]);
    }
  };

  // Filtrar os dados com base na seleção
  // Precisamos fechar o ciclo do radar repetindo o primeiro ponto no final
  const filterAndCloseLoop = (dataObj: any) => {
    const values = selectedKeys.map(k => dataObj[k as keyof Features]);
    return [...values, values[0]];
  };

  const labels = selectedKeys.map(k => FEATURE_LABELS[k] || k);
  const theta = [...labels, labels[0]]; // Fecha o ciclo das labels

  const data1 = filterAndCloseLoop(features1);
  const data2 = filterAndCloseLoop(features2);

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      
      {/* --- PAINEL DE CONTROLE (CHECKBOXES) --- */}
      <div style={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: '10px', 
        justifyContent: 'center',
        marginBottom: '20px',
        padding: '10px',
        background: '#282828',
        borderRadius: '12px',
        width: '100%'
      }}>
        {Object.keys(features1).map((key) => (
          <button
            key={key}
            onClick={() => toggleFeature(key)}
            style={{
              background: selectedKeys.includes(key) ? 'rgba(29, 185, 84, 0.2)' : 'transparent',
              border: `1px solid ${selectedKeys.includes(key) ? '#1db954' : '#555'}`,
              color: selectedKeys.includes(key) ? '#1db954' : '#888',
              padding: '6px 12px',
              borderRadius: '20px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: 600,
              transition: 'all 0.2s ease'
            }}
          >
            {FEATURE_LABELS[key] || key}
          </button>
        ))}
      </div>

      {/* --- O GRÁFICO --- */}
      <div style={{ width: '100%', height: '400px', background: '#181818', borderRadius: '16px', padding: '10px' }}>
        <Plot
          data={[
            {
              type: 'scatterpolar',
              r: data1,
              theta: theta,
              fill: 'toself',
              name: user1Name,
              line: { color: '#1db954' },
              fillcolor: 'rgba(29, 185, 84, 0.2)'
            },
            {
              type: 'scatterpolar',
              r: data2,
              theta: theta,
              fill: 'toself',
              name: user2Name,
              line: { color: '#ffffff' },
              fillcolor: 'rgba(255, 255, 255, 0.1)'
            },
          ]}
          layout={{
            polar: {
              radialaxis: {
                visible: true,
                range: [0, 1],
                color: '#666',
                gridcolor: '#333',
                tickfont: { size: 9 }
              },
              angularaxis: {
                color: '#fff',
                gridcolor: '#333'
              },
              bgcolor: 'rgba(0,0,0,0)',
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff', family: 'Inter, sans-serif' },
            showlegend: true,
            legend: { orientation: 'h', y: -0.15, font: {size: 14} },
            margin: { t: 30, b: 60, l: 50, r: 50 },
            autosize: true,
          }}
          style={{ width: '100%', height: '100%' }}
          config={{ displayModeBar: false }}
        />
      </div>
      
      <p style={{color: '#666', fontSize: '0.8rem', marginTop: '10px'}}>
        * Clique nos botões acima para filtrar características
      </p>
    </div>
  );
};

export default ComparisonChart;