# 🛡️ Guia de Segurança para Linux - SoulMatch.fm

Este guia identifica possíveis problemas que podem afetar seu sistema Linux durante a instalação e como evitá-los.

## ⚠️ **RISCOS IDENTIFICADOS**

### 1. **Bibliotecas Python com Dependências do Sistema**

#### 🔴 **psycopg2-binary** (Driver PostgreSQL)
```bash
# PROBLEMA: Pode tentar compilar código C
# SOLUÇÃO: Usar versão binary (já está no requirements.txt)
psycopg2-binary==2.9.9  # ✅ Seguro
# psycopg2==2.9.9       # ❌ Pode quebrar (requer libpq-dev)
```

#### 🔴 **python-jose[cryptography]** (Criptografia)
```bash
# PROBLEMA: cryptography pode precisar de dependências do sistema
# SOLUÇÃO: Instalar dependências do sistema primeiro
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev
```

#### 🔴 **passlib[bcrypt]** (Hash de senhas)
```bash
# PROBLEMA: bcrypt precisa compilar código C
# SOLUÇÃO: Instalar dependências de compilação
sudo apt-get install -y build-essential python3-dev
```

### 2. **Bibliotecas de Machine Learning**

#### 🟡 **scikit-learn, pandas, numpy**
```bash
# PROBLEMA: Podem precisar de BLAS/LAPACK
# SOLUÇÃO: Instalar bibliotecas matemáticas
sudo apt-get install -y libblas-dev liblapack-dev gfortran
```

### 3. **Docker e Portas**

#### 🔴 **Conflito de Portas**
```bash
# PROBLEMA: Portas já em uso
# VERIFICAR:
sudo netstat -tulpn | grep :5432  # PostgreSQL
sudo netstat -tulpn | grep :3000  # Frontend
sudo netstat -tulpn | grep :8000  # Backend

# SOLUÇÃO: Parar serviços conflitantes
sudo systemctl stop postgresql  # Se PostgreSQL estiver rodando
```

## 🛡️ **INSTALAÇÃO SEGURA**

### 1. **Preparar Sistema (Ubuntu/Debian)**
```bash
# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar dependências essenciais
sudo apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libblas-dev \
    liblapack-dev \
    gfortran \
    curl \
    git \
    docker.io \
    docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
# IMPORTANTE: Fazer logout/login após este comando
```

### 2. **Preparar Sistema (Arch Linux)**
```bash
# Atualizar sistema
sudo pacman -Syu

# Instalar dependências essenciais
sudo pacman -S \
    base-devel \
    openssl \
    libffi \
    python \
    blas \
    lapack \
    gcc-fortran \
    curl \
    git \
    docker \
    docker-compose

# Habilitar Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### 3. **Verificar Conflitos**
```bash
# Verificar se Python está funcionando
python3 --version
python3 -c "import sys; print(sys.executable)"

# Verificar se pip está funcionando
pip3 --version

# Verificar portas em uso
sudo ss -tulpn | grep -E ':(3000|8000|5432)'
```

## 🔧 **INSTALAÇÃO COM AMBIENTE VIRTUAL (RECOMENDADO)**

### 1. **Criar Ambiente Virtual Isolado**
```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências uma por uma (mais seguro)
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart==0.0.6
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install sqlalchemy==2.0.23
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install httpx==0.25.2
pip install spotipy==2.23.0
pip install plotly==5.17.0

# Dependências que podem dar problema (instalar por último)
pip install psycopg2-binary==2.9.9
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install pandas==2.1.3
pip install numpy==1.25.2
pip install scikit-learn==1.3.2
```

### 2. **Verificar Instalação**
```bash
# Verificar se todas as dependências foram instaladas
pip list

# Testar imports críticos
python -c "import psycopg2; print('PostgreSQL driver OK')"
python -c "import cryptography; print('Cryptography OK')"
python -c "import sklearn; print('Scikit-learn OK')"
python -c "import pandas; print('Pandas OK')"
```

## 🚨 **PROBLEMAS COMUNS E SOLUÇÕES**

### 1. **Erro de Compilação**
```bash
# ERRO: Microsoft Visual C++ 14.0 is required
# SOLUÇÃO: Instalar build-essential
sudo apt-get install build-essential

# ERRO: Failed building wheel for psycopg2
# SOLUÇÃO: Usar versão binary
pip uninstall psycopg2
pip install psycopg2-binary
```

### 2. **Erro de Permissão Docker**
```bash
# ERRO: permission denied while trying to connect to Docker daemon
# SOLUÇÃO: Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
# Fazer logout/login
newgrp docker
```

### 3. **Erro de Porta em Uso**
```bash
# ERRO: Port 5432 is already in use
# SOLUÇÃO: Parar PostgreSQL do sistema
sudo systemctl stop postgresql
sudo systemctl disable postgresql

# Ou usar porta diferente no docker-compose.yml
ports:
  - "5433:5432"  # Usar porta 5433 no host
```

### 4. **Erro de Memória**
```bash
# ERRO: Out of memory during compilation
# SOLUÇÃO: Aumentar swap ou usar menos processos
export MAKEFLAGS="-j1"  # Usar apenas 1 processo
pip install --no-cache-dir package_name
```

## 🔒 **CONFIGURAÇÕES DE SEGURANÇA**

### 1. **Firewall (Opcional)**
```bash
# Permitir apenas portas necessárias
sudo ufw allow 3000  # Frontend
sudo ufw allow 8000  # Backend
sudo ufw deny 5432   # PostgreSQL (apenas local)
```

### 2. **Usuário Não-Root**
```bash
# NUNCA executar como root
# Sempre usar usuário normal
whoami  # Deve mostrar seu usuário, não 'root'
```

### 3. **Backup do Sistema**
```bash
# Fazer backup antes de instalar
sudo tar -czf backup_before_soulmatch.tar.gz /home/$USER
```

## 📋 **CHECKLIST DE SEGURANÇA**

Antes de instalar, verifique:

- [ ] Sistema atualizado (`sudo apt update && sudo apt upgrade`)
- [ ] Dependências do sistema instaladas
- [ ] Usuário não é root
- [ ] Portas 3000, 8000, 5432 livres
- [ ] Docker instalado e funcionando
- [ ] Python 3.9+ instalado
- [ ] Node.js 16+ instalado
- [ ] Backup do sistema feito
- [ ] Ambiente virtual será usado

## 🆘 **EM CASO DE PROBLEMAS**

### 1. **Desinstalar Tudo**
```bash
# Parar containers
docker-compose down

# Remover volumes
docker volume prune

# Remover ambiente virtual
rm -rf backend/venv

# Remover node_modules
rm -rf frontend/node_modules
```

### 2. **Logs de Erro**
```bash
# Ver logs do Docker
docker-compose logs

# Ver logs do sistema
journalctl -u docker

# Ver logs de instalação Python
pip install --verbose package_name
```

### 3. **Restaurar Sistema**
```bash
# Restaurar backup
sudo tar -xzf backup_before_soulmatch.tar.gz -C /
```

## ✅ **INSTALAÇÃO SEGURA CONFIRMADA**

Após seguir este guia, você terá:
- ✅ Sistema protegido contra quebras
- ✅ Dependências instaladas corretamente
- ✅ Ambiente isolado e seguro
- ✅ Backup de segurança
- ✅ Conhecimento para resolver problemas

**Lembre-se**: Sempre use ambiente virtual para Python e nunca execute como root!
