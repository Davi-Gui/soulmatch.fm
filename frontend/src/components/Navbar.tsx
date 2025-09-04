import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Music, User, BarChart3, Heart, LogOut, Menu, X } from 'lucide-react';
import './Navbar.css';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <Music className="brand-icon" />
          <span>SoulMatch.fm</span>
        </Link>

        {user && (
          <>
            <div className={`navbar-menu ${isMenuOpen ? 'active' : ''}`}>
              <Link 
                to="/dashboard" 
                className={`navbar-link ${isActive('/dashboard') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <BarChart3 size={20} />
                Dashboard
              </Link>
              <Link 
                to="/profile" 
                className={`navbar-link ${isActive('/profile') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <User size={20} />
                Perfil
              </Link>
              <Link 
                to="/compatibility" 
                className={`navbar-link ${isActive('/compatibility') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <Heart size={20} />
                Compatibilidade
              </Link>
              <Link 
                to="/analysis" 
                className={`navbar-link ${isActive('/analysis') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <BarChart3 size={20} />
                Análise
              </Link>
            </div>

            <div className="navbar-user">
              {user.image_url && (
                <img 
                  src={user.image_url} 
                  alt={user.display_name} 
                  className="user-avatar"
                />
              )}
              <span className="user-name">{user.display_name || 'Usuário'}</span>
              <button 
                onClick={handleLogout}
                className="logout-btn"
                title="Sair"
              >
                <LogOut size={20} />
              </button>
            </div>

            <button 
              className="menu-toggle"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
