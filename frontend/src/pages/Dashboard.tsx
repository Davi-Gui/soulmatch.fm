import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userAPI, analysisAPI } from '../services/api';
// 1. IMPORTANTE: Adicione o useNavigate aqui
import { useNavigate } from 'react-router-dom';
import { Music, Users, Heart, BarChart3, RefreshCw, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';
import './Dashboard.css';

interface DashboardStats {
  totalTracks: number;
  totalArtists: number;
  compatibilityScore: number;
  clusterId?: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  // 2. Inicialize o hook de navegação
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
      
      const [profileResponse, analysisResponse] = await Promise.all([
        userAPI.getMusicalProfile().catch(() => null),
        analysisAPI.getMyAnalysis().catch(() => null)
      ]);

      if (profileResponse?.data) {
        const profile = profileResponse.data;
        setStats({
          totalTracks: profile.total_tracks_played || 0,
          totalArtists: profile.unique_artists || 0,
          compatibilityScore: 0, 
          clusterId: profile.cluster_id
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
              <h3>--</h3>
              <p>Matches Encontrados</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <BarChart3 size={32} />
            </div>
            <div className="stat-content">
              <h3>{stats?.clusterId !== null && stats?.clusterId !== undefined ? `Cluster ${stats.clusterId}` : '--'}</h3>
              <p>Grupo Musical</p>
            </div>
          </div>
        </div>

        <div className="dashboard-actions">
          {/* CARTÃO 1: COMPATIBILIDADE */}
          <div className="action-card">
            <div className="action-icon">
              <Heart size={48} />
            </div>
            <h3>Encontrar Matches</h3>
            <p>Descubra pessoas com gostos musicais similares aos seus</p>
            {/* 3. Adicione o onClick aqui */}
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/compatibility')}
            >
              Explorar Compatibilidade
            </button>
          </div>

          {/* CARTÃO 2: ANÁLISE */}
          <div className="action-card">
            <div className="action-icon">
              <BarChart3 size={48} />
            </div>
            <h3>Análise Detalhada</h3>
            <p>Veja gráficos e estatísticas detalhadas do seu perfil musical</p>
            {/* 3. Adicione o onClick aqui */}
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/analysis')}
            >
              Ver Análise
            </button>
          </div>

          {/* CARTÃO 3: PADRÕES (Vai para Análise também) */}
          <div className="action-card">
            <div className="action-icon">
              <TrendingUp size={48} />
            </div>
            <h3>Padrões de Escuta</h3>
            <p>Analise seus hábitos de escuta e descubra tendências</p>
            {/* 3. Adicione o onClick aqui */}
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/analysis')}
            >
              Ver Padrões
            </button>
          </div>
        </div>

        {!stats && (
          <div className="empty-state">
            <Music size={64} />
            <h2>Nenhum dado encontrado</h2>
            <p>Conecte-se com o Spotify e sincronize seus dados para começar</p>
            <button onClick={handleSyncData} className="btn btn-primary">
              <RefreshCw size={20} />
              Sincronizar Dados
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;