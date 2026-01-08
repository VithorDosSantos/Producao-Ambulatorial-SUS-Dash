#!/usr/bin/env bash
# Script de build para o Render

set -o errexit

# Instalar dependências Python
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "Build concluído com sucesso!"
