#!/bin/bash
# Script para criação da estrutura de diretórios e arquivos do projeto "city_router"

# Cria os diretórios necessários
mkdir -p city_router/app/components \
         city_router/app/pages \
         city_router/app/utils \
         city_router/app/styles \
         city_router/reports \
         city_router/data \
         city_router/.streamlit

# Cria os arquivos dentro dos diretórios
touch city_router/app/components/city_selector.py \
      city_router/app/components/map_display.py \
      city_router/app/components/progress_bar.py \
      city_router/app/components/report_viewer.py \
      city_router/app/pages/about.py \
      city_router/app/pages/main_app.py \
      city_router/app/utils/algorithms.py \
      city_router/app/utils/data_loader.py \
      city_router/app/utils/graph_utils.py \
      city_router/app/styles/custom.css \
      city_router/app/__init__.py \
      city_router/app/main.py \
      city_router/reports/bfs_report.md \
      city_router/reports/a_star_report.md \
      city_router/reports/fuzzy_report.md \
      city_router/data/cities.json \
      city_router/.streamlit/config.toml \
      city_router/requirements.txt \
      city_router/README.md \
      city_router/environment.yml

echo "Estrutura de diretórios e arquivos criada com sucesso!"
