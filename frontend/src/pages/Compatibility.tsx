import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext'; // Importar Auth
import { compatibilityAPI } from '../services/api';
import { Heart, Users, Search, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import './Compatibility.css';

const Compatibility: React.FC = () => {
  const { user } = useAuth(); // Pegar o usuário logado
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

    // Impede comparar consigo mesmo no frontend
    if (user && parseInt(searchUserId) === user.id) {
        toast.error('Você não pode calcular compatibilidade consigo mesmo!');
        return;
    }

    try {
      const response = await compatibilityAPI.calculateCompatibility(parseInt(searchUserId));
      toast.success(`Compatibilidade: ${(response.data.overall_score * 100).toFixed(1)}%`);
      loadTopMatches(); // Recarrega a lista para mostrar o novo cálculo
    } catch (error) {
      console.error('Erro ao calcular compatibilidade:', error);
      toast.error('Erro ao calcular. Verifique se o ID existe.');
    }
  };

  // Função para deletar um match antigo/errado
  const handleDeleteScore = async (scoreId: number) => {
      try {
          await compatibilityAPI.deleteScore(scoreId);
          toast.success('Histórico removido');
          loadTopMatches();
      } catch (error) {
          toast.error('Erro ao remover');
      }
  }

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
                placeholder="Digite o ID do usuário (ex: 1, 2)"
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
  {matches.map((match) => {
    // LÓGICA INTELIGENTE:
    // Se eu sou o user1, então o "outro" é o user2. E vice-versa.
    // Agora pegamos o OBJETO inteiro, não só o ID.
    const otherUser = match.user1_id === user?.id ? match.user2 : match.user1;
    
    // Fallback de segurança caso o objeto venha vazio (previne crash)
    const displayName = otherUser?.display_name || `Usuário ${otherUser?.id || 'Desconhecido'}`;
    const imageUrl = otherUser?.image_url;

    return (
      <div key={match.id} className="match-card">
        <div className="match-score">
          <Heart size={24} />
          <span>{(match.overall_score * 100).toFixed(1)}%</span>
        </div>
        
        <div className="match-details">
          {/* AQUI ESTÁ A MUDANÇA VISUAL: Foto + Nome */}
          <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px'}}>
            {imageUrl ? (
              <img 
                src={imageUrl} 
                alt={displayName} 
                style={{width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover'}} 
              />
            ) : (
              <div style={{width: '40px', height: '40px', borderRadius: '50%', background: '#333', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <Users size={20} color="white"/>
              </div>
            )}
            <h3 style={{margin: 0, fontSize: '1.3rem'}}>{displayName}</h3>
          </div>

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
                    {/* Botão para apagar cálculo antigo */}
                    <button 
                        onClick={() => handleDeleteScore(match.id)}
                        className="btn-delete"
                        style={{marginTop: '15px', background: 'transparent', border: 'none', color: '#ff4444', cursor: 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '5px'}}
                    >
                        <Trash2 size={14} /> Recalcular (Apagar)
                    </button>
                  </div>
                </div>
              )})}
            </div>
          ) : (
            <div className="empty-matches">
              <Users size={64} />
              <h3>Nenhum match encontrado</h3>
              <p>Digite um ID acima para começar</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compatibility;