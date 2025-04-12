import pandas as pd
import json
import os

def load_data(file_path):
    """
    Carrega os dados das cidades a partir do arquivo JSON.
    
    Esta função lê o arquivo JSON das cidades americanas, converte os tipos de dados para 
    formatos adequados (números flutuantes para coordenadas e inteiros para população) e
    retorna um DataFrame organizado.
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
        
        # Adiciona informações de depuração para o desenvolvedor
        print(f"Dados carregados com sucesso: {len(df)} cidades encontradas")
        print(f"Colunas disponíveis: {', '.join(df.columns.tolist())}")
        
        # Ordenar cidades por população (decrescente)
        df = df.sort_values(by='population', ascending=False).reset_index(drop=True)
        
        return df
    
    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")
        # Retorna um DataFrame vazio com as colunas esperadas em caso de erro
        return pd.DataFrame(columns=["city", "state", "latitude", "longitude", "population"])