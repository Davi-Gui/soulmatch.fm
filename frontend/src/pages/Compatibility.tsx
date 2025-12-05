import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { compatibilityAPI, userAPI } from '../services/api';
import { Heart, Users, Search, Trash2, UserPlus } from 'lucide-react';
import toast from 'react-hot-toast';
import './Compatibility.css';

const Compatibility: React.FC = () => {
  const { user } = useAuth();
  const [matches, setMatches] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Novos estados para a busca
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

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

  // 1. Função que busca o usuário pelo NOME
  const handleSearchUser = async () => {
    if (!searchTerm.trim()) {
      toast.error('Digite um nome para buscar');
      return;
    }
    
    setIsSearching(true);
    setSearchResults([]); // Limpa resultados anteriores

    try {
      const response = await userAPI.searchUsers(searchTerm);
      if (response.data.length === 0) {
        toast('Nenhum usuário encontrado com esse nome', { icon: '🔍' });
      }
      setSearchResults(response.data);
    } catch (error) {
      toast.error('Erro na busca');
    } finally {
      setIsSearching(false);
    }
  };

  // 2. Função que calcula usando o ID do usuário encontrado
  const handleCalculate = async (targetUserId: number, targetUserName: string) => {
    try {
      toast.loading(`Calculando com ${targetUserName}...`, { id: 'calc' });
      const response = await compatibilityAPI.calculateCompatibility(targetUserId);
      toast.success(`Compatibilidade: ${(response.data.overall_score * 100).toFixed(1)}%`, { id: 'calc' });
      
      setSearchResults([]); // Limpa a busca
      setSearchTerm('');    // Limpa o campo
      loadTopMatches();     // Atualiza a lista de baixo
    } catch (error) {
      toast.error('Erro ao calcular compatibilidade', { id: 'calc' });
    }
  };

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
        <p>Carregando...</p>
      </div>
    );
  }

  return (
    <div className="compatibility">
      <div className="container">
        <div className="compatibility-header">
          <h1>Compatibilidade Musical</h1>
          <p>Busque amigos pelo nome e descubra o quão parecidos vocês são</p>
        </div>

        {/* --- ÁREA DE BUSCA --- */}
        <div className="search-section">
          <div className="search-card">
            <h3>Buscar Usuário</h3>
            <div className="search-input">
              <input
                type="text"
                placeholder="Digite o nome do seu amigo (ex: João)"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearchUser()}
              />
              <button onClick={handleSearchUser} className="btn btn-primary" disabled={isSearching}>
                <Search size={20} />
                {isSearching ? 'Buscando...' : 'Buscar'}
              </button>
            </div>

            {/* Lista de Resultados da Busca */}
            {searchResults.length > 0 && (
              <div className="search-results" style={{marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '10px'}}>
                {searchResults.map((resultUser) => (
                  <div key={resultUser.id} style={{
                    background: '#282828', padding: '15px', borderRadius: '8px', 
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                  }}>
                    <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                      {resultUser.image_url ? (
                        <img src={resultUser.image_url} alt={resultUser.display_name} style={{width: '40px', height: '40px', borderRadius: '50%'}} />
                      ) : (
                        <div style={{width: '40px', height: '40px', borderRadius: '50%', background: '#444', display: 'flex', alignItems: 'center', justifyContent: 'center'}}><Users size={20} color="white"/></div>
                      )}
                      <span style={{color: 'white', fontWeight: 600}}>{resultUser.display_name}</span>
                    </div>
                    
                    <button 
                      onClick={() => handleCalculate(resultUser.id, resultUser.display_name)}
                      className="btn btn-primary"
                      style={{padding: '8px 16px', fontSize: '0.9rem'}}
                    >
                      Ver Match
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* --- LISTA DE MATCHES SALVOS --- */}
        <div className="matches-section">
          <h2>Seus Matches Salvos</h2>
          {matches.length > 0 ? (
            <div className="matches-grid">
              {matches.map((match) => {
                const otherUser = match.user1_id === user?.id ? match.user2 : match.user1;
                const displayName = otherUser?.display_name || `ID: ${otherUser?.id}`;
                const imageUrl = otherUser?.image_url;

                return (
                <div key={match.id} className="match-card">
                  <div className="match-score">
                    <Heart size={24} />
                    <span>{(match.overall_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="match-details">
                    <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px'}}>
                      {imageUrl ? (
                        <img src={imageUrl} alt={displayName} style={{width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover'}} />
                      ) : (
                        <div style={{width: '40px', height: '40px', borderRadius: '50%', background: '#333', display: 'flex', alignItems: 'center', justifyContent: 'center'}}><Users size={20} color="white"/></div>
                      )}
                      <h3 style={{margin: 0, fontSize: '1.3rem'}}>{displayName}</h3>
                    </div>

                    <div className="match-breakdown">
                      <div className="breakdown-item">
                        <span>Similaridade Sonora</span>
                        <span>{(match.audio_features_similarity * 100).toFixed(1)}%</span>
                      </div>
                      <div className="breakdown-item">
                        <span>Gosto por Artistas</span>
                        <span>{(match.artist_similarity * 100).toFixed(1)}%</span>
                      </div>
                      <div className="breakdown-item">
                        <span>Músicas em Comum</span>
                        <span>{match.common_tracks}</span>
                      </div>
                    </div>
                    <button onClick={() => handleDeleteScore(match.id)} className="btn-delete" style={{marginTop: '15px', background: 'transparent', border: 'none', color: '#ff4444', cursor: 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '5px'}}>
                        <Trash2 size={14} /> Apagar
                    </button>
                  </div>
                </div>
              )})}
            </div>
          ) : (
            <div className="empty-matches">
              <UserPlus size={64} style={{marginBottom: '16px', color: '#333'}} />
              <h3>Nenhum match ainda</h3>
              <p>Busque um amigo acima para calcular!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compatibility;