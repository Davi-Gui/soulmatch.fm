import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';
import { Music, Loader } from 'lucide-react';
import toast from 'react-hot-toast';
import './Login.css';

const Login: React.FC = () => {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {

    // Check if this is a callback from Spotify
    const code = searchParams.get('code');
    const error = searchParams.get('error');

    if (error) {
      toast.error('Erro na autenticação com Spotify');
      return;
    }

    if (code) {
      handleSpotifyCallback(code);
    }

        // If user is already logged in, redirect to dashboard
    if (user) {
      navigate('/dashboard');
      return;
    }
  }, [user, navigate, searchParams]);

  const handleSpotifyCallback = async (code: string) => {
    setIsLoading(true);
    try {
      // The backend will handle the OAuth callback
      // We need to make a request to our backend with the code
      const response = await fetch(`/auth/callback?code=${code}`);
      const data = await response.json();

      if (response.ok) {
        login(data.access_token, data.user);
        navigate('/dashboard');
      } else {
        throw new Error(data.detail || 'Erro na autenticação');
      }
    } catch (error) {
      console.error('Erro no callback:', error);
      toast.error('Erro ao conectar com Spotify');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSpotifyLogin = async () => {
    setIsLoading(true);
    try {
      console.log("Tentando conectar ao backend...");
      const response = await authAPI.getLoginUrl();
      console.log("Resposta do backend:", response.data);

      const { auth_url } = response.data;
      
      if (auth_url) {
        window.location.href = auth_url;
      } else {
        throw new Error("URL de login não recebida");
      }
    } catch (error) {
      console.error('Erro ao obter URL de login:', error);
      toast.error('Erro de conexão: Verifique se o Backend (Python) está rodando!');
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="login-loading">
        <div className="loading-content">
          <Loader className="spinner" size={48} />
          <h2>Conectando com Spotify...</h2>
          <p>Aguarde enquanto processamos sua autenticação</p>
        </div>
      </div>
    );
  }

  return (
    <div className="login">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <Music className="login-icon" size={64} />
            <h1>SoulMatch.fm</h1>
            <p>Conecte-se com seu Spotify para descobrir sua compatibilidade musical</p>
          </div>

          <div className="login-content">
            <button 
              onClick={handleSpotifyLogin}
              className="spotify-login-btn"
              disabled={isLoading}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/>
              </svg>
              Conectar com Spotify
            </button>

            <div className="login-info">
              <h3>O que você pode fazer:</h3>
              <ul>
                <li>Analisar seus gostos musicais</li>
                <li>Encontrar pessoas com gostos similares</li>
                <li>Descobrir novas músicas</li>
                <li>Ver estatísticas detalhadas</li>
              </ul>
            </div>

            <div className="login-privacy">
              <p>
                <strong>Privacidade:</strong> Apenas acessamos seus dados públicos do Spotify 
                e histórico de escuta. Não armazenamos informações pessoais sensíveis.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
