#!/bin/bash

# Script de desenvolvimento para SoulMatch.fm
# Facilita a execução do projeto em ambiente de desenvolvimento

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[SoulMatch.fm]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Verificar se Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado. Instale o Docker primeiro."
        print_info "Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
        print_info "Arch Linux: sudo pacman -S docker docker-compose"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado. Instale o Docker Compose primeiro."
        exit 1
    fi
    
    # Verificar se usuário está no grupo docker
    if ! groups $USER | grep -q docker; then
        print_warning "Usuário não está no grupo docker. Adicionando..."
        sudo usermod -aG docker $USER
        print_warning "IMPORTANTE: Faça logout/login ou execute 'newgrp docker'"
        print_warning "Depois execute o script novamente."
        exit 1
    fi
}

# Verificar se Python está instalado
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não está instalado. Instale o Python 3 primeiro."
        print_info "Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        print_info "Arch Linux: sudo pacman -S python python-pip"
        exit 1
    fi
    
    # Verificar versão do Python
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$python_version < 3.9" | bc -l) -eq 1 ]]; then
        print_error "Python 3.9+ é necessário. Versão atual: $python_version"
        exit 1
    fi
    
    # Verificar se pip está instalado
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 não está instalado. Instale o pip primeiro."
        print_info "Ubuntu/Debian: sudo apt-get install python3-pip"
        print_info "Arch Linux: sudo pacman -S python-pip"
        exit 1
    fi
}

# Verificar se Node.js está instalado
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js não está instalado. Instale o Node.js primeiro."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm não está instalado. Instale o npm primeiro."
        exit 1
    fi
}

# Verificar portas em uso
check_ports() {
    print_info "Verificando portas em uso..."
    
    # Verificar porta 5432 (PostgreSQL)
    if ss -tulpn | grep -q ":5432"; then
        print_warning "Porta 5432 (PostgreSQL) está em uso."
        print_info "Parando PostgreSQL do sistema..."
        sudo systemctl stop postgresql 2>/dev/null || true
        sudo systemctl disable postgresql 2>/dev/null || true
    fi
    
    # Verificar porta 3000 (Frontend)
    if ss -tulpn | grep -q ":3000"; then
        print_warning "Porta 3000 (Frontend) está em uso."
        print_info "Você pode precisar parar outros serviços usando esta porta."
    fi
    
    # Verificar porta 8000 (Backend)
    if ss -tulpn | grep -q ":8000"; then
        print_warning "Porta 8000 (Backend) está em uso."
        print_info "Você pode precisar parar outros serviços usando esta porta."
    fi
}

# Iniciar banco de dados
start_database() {
    print_message "Iniciando banco de dados PostgreSQL..."
    cd backend
    
    # Verificar portas antes de iniciar
    check_ports
    
    docker-compose up -d postgres
    cd ..
    print_message "Banco de dados iniciado!"
}

# Parar banco de dados
stop_database() {
    print_message "Parando banco de dados..."
    cd backend
    docker-compose down
    cd ..
    print_message "Banco de dados parado!"
}

# Configurar backend
setup_backend() {
    print_message "Configurando backend..."
    cd backend
    
    # Verificar dependências do sistema
    print_info "Verificando dependências do sistema..."
    if ! dpkg -l | grep -q "build-essential\|libssl-dev\|libffi-dev\|python3-dev"; then
        print_warning "Dependências do sistema podem estar faltando."
        print_info "Execute: sudo apt-get install build-essential libssl-dev libffi-dev python3-dev"
        print_warning "Continuando mesmo assim..."
    fi
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        print_info "Criando ambiente virtual Python..."
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    print_info "Atualizando pip..."
    pip install --upgrade pip
    
    # Instalar dependências com verificação de erro
    print_info "Instalando dependências Python..."
    if ! pip install -r requirements.txt; then
        print_error "Erro ao instalar dependências Python."
        print_info "Tentando instalar dependências problemáticas separadamente..."
        
        # Instalar dependências problemáticas uma por uma
        pip install psycopg2-binary==2.9.9 || print_warning "psycopg2-binary falhou"
        pip install python-jose[cryptography]==3.3.0 || print_warning "python-jose falhou"
        pip install passlib[bcrypt]==1.7.4 || print_warning "passlib falhou"
        pip install scikit-learn==1.3.2 || print_warning "scikit-learn falhou"
        
        print_info "Tentando instalar o resto das dependências..."
        pip install -r requirements.txt --ignore-installed
    fi
    
    # Verificar se arquivo .env existe
    if [ ! -f ".env" ]; then
        print_warning "Arquivo .env não encontrado. Copiando do exemplo..."
        cp env.example .env
        print_warning "Configure o arquivo .env com suas credenciais do Spotify!"
    fi
    
    # Inicializar banco de dados
    print_info "Inicializando banco de dados..."
    python init_db.py
    
    cd ..
    print_message "Backend configurado!"
}

# Configurar frontend
setup_frontend() {
    print_message "Configurando frontend..."
    cd frontend
    
    # Instalar dependências
    print_info "Instalando dependências Node.js..."
    npm install
    
    cd ..
    print_message "Frontend configurado!"
}

# Executar backend
run_backend() {
    print_message "Executando backend..."
    cd backend
    source venv/bin/activate
    python run.py
}

# Executar frontend
run_frontend() {
    print_message "Executando frontend..."
    cd frontend
    npm start
}

# Executar tudo
run_all() {
    print_message "Executando SoulMatch.fm completo..."
    
    # Iniciar banco de dados
    start_database
    
    # Aguardar banco estar pronto
    print_info "Aguardando banco de dados estar pronto..."
    sleep 5
    
    # Executar backend em background
    print_info "Iniciando backend em background..."
    run_backend &
    BACKEND_PID=$!
    
    # Aguardar backend estar pronto
    print_info "Aguardando backend estar pronto..."
    sleep 10
    
    # Executar frontend
    print_info "Iniciando frontend..."
    run_frontend &
    FRONTEND_PID=$!
    
    # Aguardar interrupção
    print_message "SoulMatch.fm está rodando!"
    print_info "Backend: http://localhost:8000"
    print_info "Frontend: http://localhost:3000"
    print_info "Pressione Ctrl+C para parar"
    
    # Capturar interrupção
    trap "kill $BACKEND_PID $FRONTEND_PID; stop_database; exit" INT
    
    # Aguardar processos
    wait
}

# Mostrar ajuda
show_help() {
    echo "SoulMatch.fm - Script de Desenvolvimento"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos:"
    echo "  setup     - Configura todo o ambiente de desenvolvimento"
    echo "  start     - Inicia banco de dados"
    echo "  stop      - Para banco de dados"
    echo "  backend   - Executa apenas o backend"
    echo "  frontend  - Executa apenas o frontend"
    echo "  run       - Executa tudo (banco + backend + frontend)"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 setup    # Configura tudo pela primeira vez"
    echo "  $0 run      # Executa o projeto completo"
    echo "  $0 backend  # Executa apenas o backend"
}

# Função principal
main() {
    case "${1:-help}" in
        "setup")
            check_docker
            check_python
            check_node
            start_database
            setup_backend
            setup_frontend
            print_message "Setup completo! Execute '$0 run' para iniciar o projeto."
            ;;
        "start")
            check_docker
            start_database
            ;;
        "stop")
            stop_database
            ;;
        "backend")
            check_python
            run_backend
            ;;
        "frontend")
            check_node
            run_frontend
            ;;
        "run")
            check_docker
            check_python
            check_node
            run_all
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Executar função principal
main "$@"
