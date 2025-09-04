import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Music, Heart, BarChart3, Users, ArrowRight, Play } from 'lucide-react';
import './Home.css';

const Home: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="home">
      <div className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              Descubra sua <span className="highlight">compatibilidade musical</span>
            </h1>
            <p className="hero-subtitle">
              Conecte-se com pessoas que compartilham seus gostos musicais através da análise 
              inteligente dos seus dados do Spotify.
            </p>
            
            {user ? (
              <div className="hero-actions">
                <Link to="/dashboard" className="btn btn-primary btn-large">
                  <BarChart3 size={24} />
                  Ir para Dashboard
                </Link>
                <Link to="/compatibility" className="btn btn-secondary btn-large">
                  <Heart size={24} />
                  Encontrar Matches
                </Link>
              </div>
            ) : (
              <div className="hero-actions">
                <Link to="/login" className="btn btn-primary btn-large">
                  <Play size={24} />
                  Conectar com Spotify
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <h2 className="section-title">Como funciona</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <Music size={48} />
              </div>
              <h3>Análise Musical</h3>
              <p>
                Analisamos seus dados de escuta do Spotify, incluindo gêneros, 
                artistas e características de áudio das suas músicas favoritas.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <BarChart3 size={48} />
              </div>
              <h3>Algoritmo Inteligente</h3>
              <p>
                Utilizamos machine learning e clustering para identificar padrões 
                musicais e calcular compatibilidade entre usuários.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <Heart size={48} />
              </div>
              <h3>Encontre Matches</h3>
              <p>
                Descubra pessoas com gostos musicais similares e explore 
                músicas em comum para expandir seu repertório.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-section">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">100%</div>
              <div className="stat-label">Baseado no Spotify</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">AI</div>
              <div className="stat-label">Machine Learning</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">∞</div>
              <div className="stat-label">Possibilidades</div>
            </div>
          </div>
        </div>
      </div>

      {!user && (
        <div className="cta-section">
          <div className="container">
            <div className="cta-content">
              <h2>Pronto para descobrir sua compatibilidade musical?</h2>
              <p>Conecte-se com seu Spotify e comece a explorar</p>
              <Link to="/login" className="btn btn-primary btn-large">
                <Play size={24} />
                Começar Agora
                <ArrowRight size={20} />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
