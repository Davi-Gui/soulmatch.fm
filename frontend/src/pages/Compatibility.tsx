import React, { useState, useEffect } from 'react';
import { compatibilityAPI } from '../services/api';
import { Heart, Users, TrendingUp, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import './Compatibility.css';

const Compatibility: React.FC = () => {
  const [matches, setMatches] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchUserId, setSearchUserId] = useState('');

  useEffect(() => {
    loadTopMatches();
  }, []);

  const loadTopMatches = async () => {
    try {
      const response = await compatibilityAPI.getTopMatches();
      setMatches(response.data);
    } catch (error) {
      console.error('Erro ao carregar matches:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchCompatibility = async () => {
    if (!searchUserId) {
      toast.error('Digite um ID de usuário');
      return;
    }

    try {
      const response = await compatibilityAPI.calculateCompatibility(parseInt(searchUserId));
      toast.success(`Compatibilidade: ${(response.data.overall_score * 100).toFixed(1)}%`);
    } catch (error) {
      console.error('Erro ao calcular compatibilidade:', error);
      toast.error('Erro ao calcular compatibilidade');
    }
  };

  if (isLoading) {
    return (
      <div className="compatibility-loading">
        <div className="spinner"></div>
        <p>Carregando compatibilidades...</p>
      </div>
    );
  }

  return (
    <div className="compatibility">
      <div className="container">
        <div className="compatibility-header">
          <h1>Compatibilidade Musical</h1>
          <p>Encontre pessoas com gostos musicais similares aos seus</p>
        </div>

        <div className="search-section">
          <div className="search-card">
            <h3>Calcular Compatibilidade</h3>
            <div className="search-input">
              <input
                type="number"
                placeholder="Digite o ID do usuário"
                value={searchUserId}
                onChange={(e) => setSearchUserId(e.target.value)}
              />
              <button onClick={handleSearchCompatibility} className="btn btn-primary">
                <Search size={20} />
                Calcular
              </button>
            </div>
          </div>
        </div>

        <div className="matches-section">
          <h2>Seus Melhores Matches</h2>
          {matches.length > 0 ? (
            <div className="matches-grid">
              {matches.map((match) => (
                <div key={match.id} className="match-card">
                  <div className="match-score">
                    <Heart size={24} />
                    <span>{(match.overall_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="match-details">
                    <h3>Usuário {match.user1_id === 1 ? match.user2_id : match.user1_id}</h3>
                    <div className="match-breakdown">
                      <div className="breakdown-item">
                        <span>Características de Áudio</span>
                        <span>{(match.audio_features_similarity * 100).toFixed(1)}%</span>
                      </div>
                      <div className="breakdown-item">
                        <span>Artistas</span>
                        <span>{(match.artist_similarity * 100).toFixed(1)}%</span>
                      </div>
                      <div className="breakdown-item">
                        <span>Músicas em Comum</span>
                        <span>{match.common_tracks}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-matches">
              <Users size={64} />
              <h3>Nenhum match encontrado</h3>
              <p>Conecte-se com mais usuários para encontrar compatibilidades</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compatibility;
