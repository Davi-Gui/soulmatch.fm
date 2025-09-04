-- Script de inicialização do banco de dados PostgreSQL
-- Este script é executado automaticamente quando o container é criado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Criar usuário se não existir (já é criado pelo docker-compose)
-- CREATE USER soulmatch_user WITH PASSWORD 'soulmatch_password';

-- Criar banco se não existir (já é criado pelo docker-compose)
-- CREATE DATABASE soulmatch_db OWNER soulmatch_user;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE soulmatch_db TO soulmatch_user;

-- Configurações de performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Recarregar configurações
SELECT pg_reload_conf();
