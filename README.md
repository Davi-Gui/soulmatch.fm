# SoulMatch.fm - Compatibilidade Musical

**Projeto Interdisciplinar (PID) – CEFET-MG**  
Equipe: Davi Guimarães, João Paulo Lacerda e João Victor de Carvalho / Ano: 2025

---

## 📌 Descrição

SoulMatch.fm é uma aplicação web que analisa a **compatibilidade musical entre usuários da plataforma Spotify**, com base em seus hábitos de escuta. A aplicação utiliza técnicas de análise de dados, machine learning e clustering para identificar padrões musicais e calcular compatibilidade entre usuários.

---

## Objetivo

Responder à seguinte pergunta de pesquisa:

> *"De que maneira é possível representar, por meio de uma aplicação web, a compatibilidade musical entre usuários da plataforma Spotify, a partir da análise automatizada de seus dados de escuta, com o objetivo de promover interações baseadas em afinidade musical?"*

---

## Tecnologias

### Backend
- **Python 3.11**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados principal
- **Spotipy** - Cliente Python para Spotify Web API
- **scikit-learn** - Machine learning e clustering
- **Pandas & NumPy** - Análise de dados
- **JWT** - Autenticação e autorização

### Frontend
- **React 18** - Biblioteca para interface de usuário
- **TypeScript** - Tipagem estática
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **Styled Components** - Estilização
- **Lucide React** - Ícones
- **React Hot Toast** - Notificações

### Análise de Dados
- **Clustering (K-Means)** - Agrupamento de usuários por perfil musical
- **Similaridade de Cosseno** - Cálculo de compatibilidade
- **Análise de Características de Áudio** - Danceability, Energy, Valence, etc.
- **Análise de Padrões de Escuta** - Horários, contextos, frequência

---

## Estrutura do Projeto

```
soulmatch.fm/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── routers/         # Endpoints da API
│   │   ├── services/        # Lógica de negócio
│   │   ├── models.py        # Modelos do banco de dados
│   │   ├── schemas.py       # Schemas Pydantic
│   │   ├── database.py      # Configuração do banco
│   │   └── main.py          # Aplicação principal
│   ├── requirements.txt     # Dependências Python
│   └── run.py              # Script de execução
├── frontend/               # Aplicação React
│   ├── src/
│   │   ├── components/     # Componentes reutilizáveis
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── contexts/       # Contextos React
│   │   ├── services/       # Serviços de API
│   │   └── App.tsx         # Componente principal
│   ├── package.json        # Dependências Node.js
│   └── public/             # Arquivos estáticos
├── data/                   # Dados de exemplo e testes
├── docs/                   # Documentação e relatórios
└── README.md              # Este arquivo
```

---

## ⚙️ Como Executar

### Pré-requisitos
- Python 3.9 - 3.11
- Node.js 16+
- PostgreSQL 12+
- Conta no Spotify Developer

### 1. Configuração do Backend

```bash
# Navegar para o diretório backend
cd backend

#Iniciar containers 
docker-compose up -d

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas credenciais do Spotify e banco de dados

# Executar migrações do banco (quando implementadas)
# alembic upgrade head

#Inicializar Banco de Dados
python init_db.py

# Executar o servidor
python run.py
```

### 2. Configuração do Frontend

```bash
# Navegar para o diretório frontend
cd frontend

# Instalar dependências
npm install

# Executar o servidor de desenvolvimento
npm start
```

### 3. Configuração do Spotify

1. Acesse [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Crie uma nova aplicação
3. Configure as URLs de redirecionamento:
   - `http://127.0.0.1:8000/callback`
4. Copie o Client ID e Client Secret para o arquivo `.env`

---

## Funcionalidades Implementadas

### Backend
- [x] Estrutura base do FastAPI
- [x] Modelos de banco de dados
- [x] Autenticação OAuth2 com Spotify
- [x] Endpoints para usuários
- [x] Endpoints para compatibilidade
- [x] Endpoints para análise
- [x] Serviços de coleta de dados
- [x] Serviços de análise e clustering
- [x] Configuração do banco de dados PostgreSQL
- [x] Documentação da API



### Frontend
- [x] Estrutura base do React
- [x] Sistema de autenticação
- [x] Páginas principais (Home, Login, Dashboard, Profile, Compatibility, Analysis)
- [x] Componentes reutilizáveis
- [x] Integração com API
- [x] Interface responsiva

### Em Desenvolvimento
- [ ] Testes automatizados
- [ ] Deploy em produção
- [ ] Otimizações de performance

---

## Algoritmo de Compatibilidade

O algoritmo de compatibilidade considera:

1. **Características de Áudio (40%)**
   - Danceability, Energy, Valence, Acousticness, etc.
   - Similaridade de cosseno entre vetores de características

2. **Artistas em Comum (40%)**
   - Análise de artistas mais ouvidos
   - Cálculo de similaridade baseado em interseção de conjuntos

3. **Músicas em Comum (20%)**
   - Número de músicas compartilhadas
   - Normalização baseada no total de músicas

4. **Clustering de Usuários**
   - Agrupamento por perfil musical similar
   - Identificação de padrões de escuta

---

## Privacidade e Segurança

- **Dados Acessados**: Apenas dados públicos e histórico de escuta do Spotify
- **Armazenamento**: Dados agregados e anonimizados
- **Autenticação**: OAuth2 com Spotify + JWT
- **Criptografia**: Tokens seguros e comunicação HTTPS

---

## Documentação

A documentação técnica detalhada está sendo desenvolvida na pasta `/docs` e incluirá:

- Especificação da API
- Diagramas de arquitetura
- Relatório acadêmico
- Guias de contribuição

---

## Deploy

### Opções de Hospedagem
- **Backend**: Railway, Render, Heroku
- **Frontend**: Vercel, Netlify
- **Banco de Dados**: PostgreSQL (Railway, Supabase)

### Variáveis de Ambiente para Produção
```env
# Spotify
SPOTIFY_CLIENT_ID=your_production_client_id
SPOTIFY_CLIENT_SECRET=your_production_client_secret
SPOTIFY_REDIRECT_URI=https://yourdomain.com/auth/callback

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=your_production_secret_key
```

---

## Contribuição

Este é um projeto acadêmico, mas contribuições são bem-vindas:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## Licença

Este projeto é de uso acadêmico e todos os direitos são reservados à equipe responsável.

---

## Futuro

Este projeto foi pensado com potencial de uso prático fora do ambiente acadêmico e poderá ser explorado comercialmente no futuro, dependendo da viabilidade técnica e do interesse da equipe.

---

## Contato

**Equipe SoulMatch.fm**
- Davi Guimarães
- João Paulo Lacerda  
- João Victor de Carvalho

**Instituição**: CEFET-MG - Curso Técnico em Informática
