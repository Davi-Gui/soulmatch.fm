import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userAPI, analysisAPI, compatibilityAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Music, Users, Heart, BarChart3, RefreshCw, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';
import './Dashboard.css';

interface DashboardStats {
  totalTracks: number;
  totalArtists: number;
  matchesCount: number;
  clusterId?: number;
  musicPersona?: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      const [profileResponse, analysisResponse, matchesResponse] = await Promise.all([
        userAPI.getMusicalProfile().catch(() => null),
        analysisAPI.getMyAnalysis().catch(() => null),
        compatibilityAPI.getTopMatches().catch(() => ({ data: [] }))
      ]);

      if (profileResponse?.data) {
        const profile = profileResponse.data;
        const analysis = analysisResponse?.data;

        setStats({
          totalTracks: profile.total_tracks_played || 0,
          totalArtists: profile.unique_artists || 0,
          matchesCount: matchesResponse?.data ? matchesResponse.data.length : 0,
          clusterId: profile.cluster_id,
          musicPersona: analysis?.music_persona || "Indefinido"
        });
      }
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      toast.error('Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncData = async () => {
    try {
      setIsSyncing(true);
      await userAPI.syncData();
      await analysisAPI.performClustering(1);
      toast.success('Dados sincronizados com sucesso!');
      await loadDashboardData();
    } catch (error) {
      console.error('Erro ao sincronizar dados:', error);
      toast.error('Erro ao sincronizar dados');
    } finally {
      setIsSyncing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Carregando dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="container">
        <div className="dashboard-header">
          <div className="welcome-section">
            <h1>Bem-vindo, {user?.display_name || 'Usuário'}!</h1>
            <p>Veja suas estatísticas musicais e descubra sua compatibilidade</p>
          </div>
          
          <button 
            onClick={handleSyncData}
            disabled={isSyncing}
            className="sync-btn"
          >
            <RefreshCw className={isSyncing ? 'spinning' : ''} size={20} />
            {isSyncing ? 'Sincronizando...' : 'Sincronizar Dados'}
          </button>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <Music size={32} />
            </div>
            <div className="stat-content">
              <h3>{stats?.totalTracks || 0}</h3>
              <p>Músicas Tocadas</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Users size={32} />
            </div>
            <div className="stat-content">
              <h3>{stats?.totalArtists || 0}</h3>
              <p>Artistas Únicos</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Heart size={32} />
            </div>
            <div className="stat-content">
              <h3>{stats?.matchesCount !== undefined ? stats.matchesCount : '--'}</h3>
              <p>Matches Encontrados</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <BarChart3 size={32} />
            </div>
            <div className="stat-content">
              <h3 style={{fontSize: stats?.musicPersona && stats.musicPersona.length > 15 ? '1.5rem' : '2rem'}}>
                {stats?.musicPersona || (stats?.clusterId !== undefined ? `Grupo ${stats.clusterId}` : '--')}
              </h3>
              <p>Sua Vibe Musical</p>
            </div>
          </div>
        </div>

        <div className="dashboard-actions">
          <div className="action-card">
            <div className="action-icon">
              <Heart size={48} />
            </div>
            <h3>Encontrar Matches</h3>
            <p>Descubra pessoas com gostos musicais similares aos seus</p>
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/compatibility')}
            >
              Explorar Compatibilidade
            </button>
          </div>

          <div className="action-card">
            <div className="action-icon">
              <BarChart3 size={48} />
            </div>
            <h3>Análise Detalhada</h3>
            <p>Veja gráficos e estatísticas detalhadas do seu perfil musical</p>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/analysis')}
            >
              Ver Análise
            </button>
          </div>

          <div className="action-card">
            <div className="action-icon">
              <TrendingUp size={48} />
            </div>
            <h3>Padrões de Escuta</h3>
            <p>Analise seus hábitos de escuta e descubra tendências</p>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/analysis')}
            >
              Ver Padrões
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;