import React, { useState, useEffect } from 'react';
import { analysisAPI } from '../services/api';
import { BarChart3, TrendingUp, Clock, Music, ListMusic, Tags } from 'lucide-react';
import './Analysis.css';

const Analysis: React.FC = () => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showGenres, setShowGenres] = useState(false);

  useEffect(() => {
    loadAnalysis();
  }, []);

  const loadAnalysis = async () => {
    try {
      const response = await analysisAPI.getMyAnalysis();
      setAnalysis(response.data);
    } catch (error) {
      console.error('Erro ao carregar análise:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (ms: number) => {
    if (!ms) return '0 min';
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return `${minutes}:${Number(seconds) < 10 ? '0' : ''}${seconds} min`;
  };

  if (isLoading) {
    return (
      <div className="analysis-loading">
        <div className="spinner"></div>
        <p>Carregando análise...</p>
      </div>
    );
  }

  return (
    <div className="analysis">
      <div className="container">
        <div className="analysis-header">
          <h1>Análise Musical</h1>
          <p>Explore seu perfil musical detalhado</p>
        </div>

        {analysis ? (
          <div className="analysis-content">
            <div className="audio-features">
              <h2>Características de Áudio</h2>
              <div className="features-grid">
                {Object.entries(analysis.audio_features_profile).map(([key, value]) => {
                  const labels: {[key: string]: string} = {
                    danceability: 'Dançabilidade',
                    energy: 'Energia',
                    valence: 'Positividade',
                    acousticness: 'Acústico',
                    instrumentalness: 'Instrumental',
                    liveness: 'Ao Vivo',
                    speechiness: 'Fala',
                    tempo: 'Tempo (BPM)'
                  };
                  
                  const isTempo = key === 'tempo';
                  const displayValue = isTempo ? Math.round(value as number) : (value as number).toFixed(2);
                  const barWidth = isTempo ? Math.min((value as number) / 200 * 100, 100) : (value as number) * 100;

                  return (
                    <div key={key} className="feature-item">
                      <div className="feature-label">{labels[key] || key}</div>
                      <div className="feature-bar">
                        <div 
                          className="feature-fill" 
                          style={{ width: `${barWidth}%` }}
                        ></div>
                      </div>
                      <div className="feature-value">{displayValue}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="top-content">
              <div className="top-artists">
                <h3>Top Artistas</h3>
                <div className="top-list">
                  {analysis.top_artists.slice(0, 10).map((artist: any, index: number) => (
                    <div key={index} className="top-item">
                      <span className="rank">{index + 1}</span>
                      <span className="name">{artist.name}</span>
                      <span className="count">{artist.play_count} plays</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="top-tracks">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3 style={{ margin: 0 }}>{showGenres ? 'Top Gêneros' : 'Top Músicas'}</h3>
                  <button 
                    onClick={() => setShowGenres(!showGenres)}
                    style={{
                      background: 'none',
                      border: '1px solid #333',
                      borderRadius: '8px',
                      padding: '8px',
                      cursor: 'pointer',
                      color: '#1db954',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '0.9rem'
                    }}
                  >
                    {showGenres ? <ListMusic size={18} /> : <Tags size={18} />}
                    {showGenres ? 'Ver Músicas' : 'Ver Gêneros'}
                  </button>
                </div>
                
                <div className="top-list">
                  {showGenres ? (
                    analysis.top_genres.slice(0, 10).map((genre: string, index: number) => (
                      <div key={index} className="top-item">
                        <span className="rank">{index + 1}</span>
                        <span className="name" style={{ textTransform: 'capitalize' }}>{genre}</span>
                        <span className="count"></span>
                      </div>
                    ))
                  ) : (
                    analysis.top_tracks.slice(0, 10).map((track: any, index: number) => (
                      <div key={index} className="top-item">
                        <span className="rank">{index + 1}</span>
                        <span className="name">{track.name}</span>
                        <span className="count">{track.play_count} plays</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            <div className="listening-patterns">
              <h2>Padrões de Escuta</h2>
              <div className="patterns-grid">
                <div className="pattern-item">
                  <Music size={24} />
                  <div>
                    <h4>Total de Músicas</h4>
                    <p>{analysis.listening_patterns.total_tracks_played}</p>
                  </div>
                </div>
                <div className="pattern-item">
                  <TrendingUp size={24} />
                  <div>
                    <h4>Artistas Únicos</h4>
                    <p>{analysis.listening_patterns.unique_artists}</p>
                  </div>
                </div>
                <div className="pattern-item">
                  <BarChart3 size={24} />
                  <div>
                    <h4>Gêneros</h4>
                    <p>{analysis.listening_patterns.unique_genres}</p>
                  </div>
                </div>
                <div className="pattern-item">
                  <Clock size={24} />
                  <div>
                    <h4>Duração Média</h4>
                    <p>{formatDuration(analysis.listening_patterns.avg_session_duration)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="empty-analysis">
            <BarChart3 size={64} />
            <h2>Nenhuma análise encontrada</h2>
            <p>Sincronize seus dados do Spotify para ver a análise</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analysis;