#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
Execute este script para criar as tabelas necessárias
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base
from app.config import settings

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        # Create engine
        engine = create_engine(settings.database_url)
        
        # Create all tables
        print("Criando tabelas do banco de dados...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Banco de dados inicializado com sucesso!")
        print(f"📊 Tabelas criadas:")
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
            
    except SQLAlchemyError as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

def check_database_connection():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as connection:
            # CORREÇÃO AQUI: Usando text() para envolver a query
            connection.execute(text("SELECT 1"))
        print("✅ Conexão com banco de dados estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com banco de dados: {e}")
        print("💡 Verifique se:")
        print("   - O PostgreSQL está rodando")
        print("   - As credenciais no arquivo .env estão corretas")
        print("   - O banco de dados existe")
        return False

if __name__ == "__main__":
    print("🚀 Inicializando banco de dados SoulMatch.fm...")
    print(f"📡 URL do banco: {settings.database_url}")
    
    # Check connection first
    if check_database_connection():
        init_database()
    else:
        sys.exit(1)