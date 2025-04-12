import networkx as nx
import math
import pandas as pd

def build_graph(cities_df, r):
    """Constrói o grafo a partir dos dados das cidades."""
    G = nx.Graph()

    # Adicionar nós
    for index, row in cities_df.iterrows():
        G.add_node(row['city'], pos=(row['longitude'], row['latitude']), 
                  state=row['state'], population=row['population'])

    # Adicionar arestas
    for i, city1 in cities_df.iterrows():
        for j, city2 in cities_df.iterrows():
            if i != j:
                dist = calculate_distance(city1, city2)
                if dist <= r:
                    # Adicionar aresta se a distância é menor ou igual ao raio
                    G.add_edge(city1['city'], city2['city'], weight=dist)

    return G

def calculate_distance(city1, city2):
    """Calcula a distância euclidiana entre duas cidades."""
    lat1, lon1 = city1['latitude'], city1['longitude']
    lat2, lon2 = city2['latitude'], city2['longitude']
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def calculate_haversine_distance(city1, city2):
    """
    Calcula a distância geodésica entre duas cidades usando a fórmula de Haversine.
    Retorna a distância em quilômetros.
    
    Args:
        city1: Dicionário ou Series com campos 'latitude' e 'longitude'
        city2: Dicionário ou Series com campos 'latitude' e 'longitude'
    Returns:
        Distância em quilômetros
    """
    # Raio da Terra em quilômetros
    R = 6371.0
    
    # Converter graus para radianos
    lat1_rad = math.radians(city1['latitude'])
    lon1_rad = math.radians(city1['longitude'])
    lat2_rad = math.radians(city2['latitude'])
    lon2_rad = math.radians(city2['longitude'])
    
    # Diferença de coordenadas
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance