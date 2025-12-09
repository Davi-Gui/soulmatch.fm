#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

command_exists() { command -v "$1" >/dev/null 2>&1; }

echo "==> Inicializando SoulMatch.fm"

# Dependências básicas
for cmd in python node npm docker docker-compose; do
  if ! command_exists "$cmd"; then
    echo "Erro: '$cmd' não está instalado ou no PATH."
    exit 1
  fi
done

# Detecta se estamos usando pyenv (modo do colega) ou venv padrão (modo do README)
USING_PYENV=0
if command_exists pyenv; then
  # Se existir um .python-version com 'venv', consideramos pyenv local venv
  if [ -f "$BACKEND_DIR/.python-version" ] && grep -q "^venv$" "$BACKEND_DIR/.python-version"; then
    USING_PYENV=1
  fi
fi

# Função para verificar se o python NÃO é o do sistema e se há venv ativo
check_python_env() {
  local pybin
  pybin="$(command -v python || true)"
  if [ -z "${pybin}" ]; then
    echo "Erro: Python não encontrado no PATH."
    exit 1
  fi

  # Bloqueia uso de /usr/bin/python (python do sistema)
  if [ "$pybin" = "/usr/bin/python" ] || [ "$pybin" = "/usr/bin/python3" ]; then
    echo "Erro: Python atual é o do sistema ($pybin). Nenhum ambiente virtual está rodando."
    echo "Use pyenv local venv (modo pyenv) ou ative o venv (modo README) antes de executar."
    exit 1
  fi

  # Adicional: se não houver VIRTUAL_ENV e não for pyenv ativo, alerta
  if [ "$USING_PYENV" -eq 0 ] && [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "Erro: VIRTUAL_ENV não está definido e pyenv não está configurado com 'venv'."
    echo "Ative o venv com: source backend/venv/bin/activate"
    exit 1
  fi
}

# Backend setup
echo "==> Configurando Backend"
pushd "$BACKEND_DIR" >/dev/null

# Modo pyenv
if [ "$USING_PYENV" -eq 1 ]; then
  echo "Detectado pyenv com '.python-version' = venv"
  # Garante que a versão local está setada para 'venv'
  pyenv local venv
  # Checa se o python atual é o do pyenv e não o do sistema
  check_python_env

  # Instala deps
  if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
  else
    echo "Aviso: requirements.txt não encontrado."
  fi
else
  echo "Usando venv padrão (conforme README)"
  # Cria venv se não existir
  if [ ! -d "venv" ]; then
    python -m venv venv
  fi
  # Ativa venv
  # shellcheck disable=SC1091
  source venv/bin/activate
  # Checa se não é python do sistema
  check_python_env

  # Instala deps
  if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
  else
    echo "Aviso: requirements.txt não encontrado."
  fi
fi

# Docker services (DB)
echo "==> Subindo containers Docker..."
docker-compose up -d

# .env
if [ ! -f ".env" ]; then
  if [ -f "env.example" ]; then
    cp env.example .env
    echo "Criado .env a partir de env.example. Edite credenciais do Spotify e DB."
  else
    echo "Aviso: env.example não encontrado; crie um .env."
  fi
fi

# Inicializar DB se existir script
if [ -f "init_db.py" ]; then
  echo "==> Inicializando Banco de Dados..."
  python init_db.py || echo "Aviso: init_db.py falhou ou já inicializado."
fi

# Iniciar backend
echo "==> Iniciando Backend (FastAPI)"
python run.py &
BACKEND_PID=$!
popd >/dev/null

# Frontend setup
echo "==> Configurando Frontend"
pushd "$FRONTEND_DIR" >/dev/null
if [ -f "package.json" ]; then
  npm install
else
  echo "Erro: package.json não encontrado em $FRONTEND_DIR"
  exit 1
fi

echo "==> Iniciando Frontend (React)"
npm start &
FRONTEND_PID=$!
popd >/dev/null

echo "==> Backend PID: $BACKEND_PID | Frontend PID: $FRONTEND_PID"
echo "Logs backend: tail -f $BACKEND_DIR/app.log (se configurado) ou veja o terminal."
echo "Para parar: kill $BACKEND_PID $FRONTEND_PID"
