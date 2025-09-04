# 🚀 Guia de Início Rápido - SoulMatch.fm

Este guia te ajudará a configurar e executar o projeto SoulMatch.fm em poucos minutos.

## ⚡ Início Rápido

> **⚠️ IMPORTANTE**: Se você está em um sistema Linux, leia primeiro o [Guia de Segurança](docs/SEGURANCA_LINUX.md) para evitar problemas que podem afetar seu sistema.

### 1. Pré-requisitos

#### Sistema Operacional
- **Linux** (Ubuntu 20.04+, Arch Linux, etc.)
- **macOS** (10.15+)
- **Windows** (10+ com WSL2 recomendado)

#### Software Necessário
- **Docker** (20.10+) e **Docker Compose** (2.0+)
- **Python** 3.9 ou superior
- **Node.js** 16+ e **npm** 8+
- **Git** 2.30+

#### Verificar Instalações
```bash
# Verificar versões
docker --version
docker-compose --version
python3 --version
node --version
npm --version
git --version
```

#### Recursos do Sistema
- **RAM**: Mínimo 4GB (recomendado 8GB+)
- **Espaço em Disco**: 2GB livres
- **Portas**: 3000 (frontend), 8000 (backend), 5432 (PostgreSQL)

### 2. Configuração do Spotify
1. Acesse [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Crie uma nova aplicação
3. Configure as URLs de redirecionamento:
   - `http://localhost:8000/auth/callback`
4. Anote o **Client ID** e **Client Secret**

### 3. Executar o Projeto

```bash
# Clone o repositório (se ainda não fez)
git clone <seu-repositorio>
cd soulmatch.fm

# Configure tudo automaticamente
./dev.sh setup

# Execute o projeto completo
./dev.sh run
```

**⚠️ Importante**: O script `./dev.sh setup` criará automaticamente um ambiente virtual Python na pasta `backend/venv` e instalará todas as dependências necessárias.

### 4. Acessar a Aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs

## 🔧 Configuração Manual

Se preferir configurar manualmente:

### Backend
```bash
cd backend

# Criar ambiente virtual (se não existir)
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Verificar se está no ambiente virtual
which python  # Deve mostrar: /caminho/para/soulmatch.fm/backend/venv/bin/python

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Edite o arquivo .env com suas credenciais

# Iniciar banco de dados
docker-compose up -d postgres

# Aguardar banco estar pronto (5-10 segundos)
sleep 5

# Inicializar banco
python init_db.py

# Executar servidor
python run.py
```

**💡 Dica**: Sempre ative o ambiente virtual antes de trabalhar no backend:
```bash
cd backend
source venv/bin/activate
```

### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Executar servidor de desenvolvimento
npm start
```

## 📝 Configuração do .env

Edite o arquivo `backend/.env` com suas credenciais:

```env
# Spotify API
SPOTIFY_CLIENT_ID=seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=seu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://localhost:8000/auth/callback

# Database
DATABASE_URL=postgresql://soulmatch_user:soulmatch_password@localhost:5432/soulmatch_db

# Security
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## 🎯 Como Usar

1. **Acesse** http://localhost:3000
2. **Clique** em "Conectar com Spotify"
3. **Autorize** o acesso aos seus dados do Spotify
4. **Explore** seu perfil musical e compatibilidades

## 🐛 Solução de Problemas

### Erro de Conexão com Banco
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps

# Reiniciar banco de dados
./dev.sh stop
./dev.sh start
```

### Erro de Dependências
```bash
# Backend - Certifique-se de estar no ambiente virtual
cd backend
source venv/bin/activate  # Ativar ambiente virtual
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Erro de Ambiente Virtual
```bash
# Se o ambiente virtual não existir
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verificar se está funcionando
which python  # Deve mostrar o caminho do venv
pip list      # Deve mostrar as dependências instaladas
```

### Erro de Spotify API
- Verifique se as credenciais no `.env` estão corretas
- Confirme se a URL de redirecionamento está configurada no Spotify Dashboard

## 📊 Funcionalidades

### ✅ Implementadas
- Autenticação com Spotify
- Análise de perfil musical
- Cálculo de compatibilidade
- Interface web responsiva
- Clustering de usuários

### 🔄 Em Desenvolvimento
- Visualizações avançadas
- Recomendações de música
- Chat entre usuários compatíveis

## 🔬 Como Funciona

### 1. **Autenticação e Coleta de Dados**
- Usuário conecta com Spotify via OAuth2
- Sistema coleta dados de escuta (músicas, artistas, histórico)
- Extrai características de áudio das músicas (danceability, energy, valence, etc.)

### 2. **Análise de Perfil Musical**
- Calcula médias das características de áudio
- Identifica artistas e gêneros mais ouvidos
- Analisa padrões de escuta (horários, contextos)

### 3. **Algoritmo de Compatibilidade**
- **Características de Áudio (40%)**: Similaridade de cosseno entre vetores de features
- **Artistas em Comum (40%)**: Análise de interseção de conjuntos de artistas
- **Músicas em Comum (20%)**: Número de músicas compartilhadas normalizado

### 4. **Clustering de Usuários**
- Agrupa usuários com perfis musicais similares usando K-Means
- Facilita descoberta de matches compatíveis
- Identifica padrões de comportamento musical

### 5. **Interface e Visualizações**
- Dashboard com estatísticas pessoais
- Página de compatibilidade com matches
- Análise detalhada do perfil musical
- Gráficos interativos de características de áudio

## 🛠️ Comandos Úteis

```bash
# Ver ajuda
./dev.sh help

# Configurar ambiente (cria venv automaticamente)
./dev.sh setup

# Executar tudo
./dev.sh run

# Apenas backend (usa o venv automaticamente)
./dev.sh backend

# Apenas frontend
./dev.sh frontend

# Parar banco de dados
./dev.sh stop
```

### Comandos Manuais com Ambiente Virtual
```bash
# Ativar ambiente virtual manualmente
cd backend
source venv/bin/activate

# Verificar ambiente virtual ativo
which python
echo $VIRTUAL_ENV

# Desativar ambiente virtual
deactivate

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

## 📦 Dependências e Estrutura

### Backend (Python)
```
fastapi==0.104.1          # Framework web
uvicorn[standard]==0.24.0  # Servidor ASGI
sqlalchemy==2.0.23        # ORM
psycopg2-binary==2.9.9    # Driver PostgreSQL
spotipy==2.23.0           # Cliente Spotify API
scikit-learn==1.3.2       # Machine Learning
pandas==2.1.3             # Análise de dados
numpy==1.25.2             # Computação numérica
python-jose[cryptography] # JWT
passlib[bcrypt]           # Hash de senhas
```

### Frontend (Node.js)
```
react==18.2.0             # Biblioteca UI
typescript==4.9.5         # Tipagem estática
react-router-dom==6.20.1  # Roteamento
axios==1.6.2              # Cliente HTTP
styled-components==6.1.1  # CSS-in-JS
lucide-react==0.294.0     # Ícones
react-hot-toast==2.4.1    # Notificações
```

### Estrutura de Arquivos
```
soulmatch.fm/
├── backend/              # API FastAPI
│   ├── app/             # Código da aplicação
│   ├── venv/            # Ambiente virtual Python
│   ├── requirements.txt # Dependências Python
│   └── docker-compose.yml
├── frontend/            # App React
│   ├── src/            # Código fonte
│   ├── public/         # Arquivos estáticos
│   └── package.json    # Dependências Node.js
├── docs/               # Documentação
└── dev.sh             # Script de desenvolvimento
```

## 📚 Próximos Passos

1. **Explore** a documentação da API em http://localhost:8000/docs
2. **Teste** as funcionalidades de compatibilidade
3. **Analise** seu perfil musical
4. **Contribua** com melhorias e novas funcionalidades

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs do console
2. Consulte a documentação da API
3. Abra uma issue no repositório
4. Entre em contato com a equipe

---

**Bem-vindo ao SoulMatch.fm! 🎧✨**
