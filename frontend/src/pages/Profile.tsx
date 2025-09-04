import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userAPI } from '../services/api';
import { User, Music, Users, Calendar, MapPin } from 'lucide-react';
import './Profile.css';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await userAPI.getMusicalProfile();
      setProfile(response.data);
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="profile-loading">
        <div className="spinner"></div>
        <p>Carregando perfil...</p>
      </div>
    );
  }

  return (
    <div className="profile">
      <div className="container">
        <div className="profile-header">
          <div className="profile-avatar">
            {user?.image_url ? (
              <img src={user.image_url} alt={user.display_name} />
            ) : (
              <User size={64} />
            )}
          </div>
          <div className="profile-info">
            <h1>{user?.display_name || 'Usuário'}</h1>
            <p className="profile-email">{user?.email}</p>
            {user?.country && (
              <p className="profile-location">
                <MapPin size={16} />
                {user.country}
              </p>
            )}
            <p className="profile-followers">
              <Users size={16} />
              {user?.followers || 0} seguidores
            </p>
          </div>
        </div>

        {profile && (
          <div className="profile-stats">
            <div className="stat-item">
              <Music size={24} />
              <div>
                <h3>{profile.total_tracks_played || 0}</h3>
                <p>Músicas Tocadas</p>
              </div>
            </div>
            <div className="stat-item">
              <Users size={24} />
              <div>
                <h3>{profile.unique_artists || 0}</h3>
                <p>Artistas Únicos</p>
              </div>
            </div>
            <div className="stat-item">
              <Calendar size={24} />
              <div>
                <h3>{profile.unique_genres || 0}</h3>
                <p>Gêneros</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
