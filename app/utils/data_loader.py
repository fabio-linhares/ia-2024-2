import pandas as pd
import json
import os

def load_data(file_path):
    """
    Carrega os dados das cidades a partir do arquivo JSON e cria identificadores únicos.
    
    Esta função lê o arquivo JSON das cidades americanas, converte os tipos de dados para 
    formatos adequados (números flutuantes para coordenadas e inteiros para população),
    cria IDs únicos para cada cidade como inteiros sequenciais começando em 0, 
    e retorna um DataFrame organizado.
    
    Returns:
        tuple: (DataFrame com dados das cidades, dicionário name_to_id, dicionário id_to_name)
    """
    try:
        with open(file_path, 'r') as f:
            dados = json.load(f)
        
        # Converte o JSON para um DataFrame pandas para facilitar a manipulação
        df = pd.DataFrame(dados)
        
        # Garante que os campos numéricos estejam no formato correto
        if 'population' in df.columns:
            # Remove possíveis caracteres não numéricos e converte para inteiro
            df['population'] = df['population'].astype(str).str.replace(',', '').astype(int)
        
        # Garante que as coordenadas sejam números flutuantes para cálculos precisos
        for col in ['latitude', 'longitude']:
            if col in df.columns:
                df[col] = df[col].astype(float)
        
        # Ordenar cidades por população (decrescente)
        df = df.sort_values(by='population', ascending=False).reset_index(drop=True)
        
        # Cria um ID único para cada cidade como inteiro sequencial iniciando em 0
        df['city_id'] = range(len(df))
        
        # Adiciona informações de depuração para o desenvolvedor
        print(f"Dados carregados com sucesso: {len(df)} cidades encontradas")
        print(f"Colunas disponíveis: {', '.join(df.columns.tolist())}")
        
        # Verifica se há cidades com o mesmo nome
        cities_with_dupes = df['city'].value_counts()
        duplicated_cities = cities_with_dupes[cities_with_dupes > 1].index.tolist()
        if duplicated_cities:
            print(f"Atenção: Encontradas {len(duplicated_cities)} cidades com nomes duplicados.")
            print(f"Exemplos: {', '.join(duplicated_cities[:5])}")
            print("Um ID único (inteiro) foi atribuído a cada cidade, iniciando em 0.")
        
        # Criar dicionários de mapeamento entre city_id e city_name
        name_to_id = dict(zip(df['city'], df['city_id']))
        id_to_name = dict(zip(df['city_id'], df['city']))
        
        return df, name_to_id, id_to_name
    
    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")
        # Retorna um DataFrame vazio com as colunas esperadas em caso de erro
        empty_df = pd.DataFrame(columns=["city", "state", "latitude", "longitude", "population", "city_id"])
        return empty_df, {}, {}