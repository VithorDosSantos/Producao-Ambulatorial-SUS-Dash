#!/usr/bin/env bash
# Script de inicialização para criar os bancos de dados no PostgreSQL do Render

set -o errexit

echo "🚀 Iniciando configuração do banco de dados..."

# Criar banco Espelho_siasus se não existir
psql -v ON_ERROR_STOP=1 --username "$PGUSER" --dbname "$PGDATABASE" <<-EOSQL
    SELECT 'CREATE DATABASE "Espelho_siasus"'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'Espelho_siasus')\gexec
EOSQL

echo "✅ Bancos de dados configurados!"
echo "ℹ️  Agora execute manualmente os scripts SQL para criar as tabelas"
