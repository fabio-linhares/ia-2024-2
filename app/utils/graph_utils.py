import networkx as nx
import math
import pandas as pd

def build_graph(cities_df, r=None, d=None):
    """Constrói o grafo a partir dos dados das cidades.
    
    Args:
        cities_df: DataFrame com dados das cidades
        r: Raio máximo de conexão em graus (distância euclidiana)
        d: Distância máxima em quilômetros (usando Haversine)
        
    Pelo menos um dos parâmetros r ou d deve ser fornecido.
    Se ambos forem fornecidos, uma conexão é criada apenas se satisfizer ambas as condições.
    """
    if r is None and d is None:
        raise ValueError("Pelo menos um dos parâmetros r ou d deve ser fornecido")
        
    G = nx.Graph()

    # Adicionar nós
    for index, row in cities_df.iterrows():
        G.add_node(row['city'], pos=(row['longitude'], row['latitude']), 
                  state=row['state'], population=row['population'])

    # Adicionar arestas
    for i, city1 in cities_df.iterrows():
        for j, city2 in cities_df.iterrows():
            if i != j:
                # Calcular distâncias
                euclidian_dist = calculate_distance(city1, city2)
                km_dist = calculate_haversine_distance(city1, city2)
                
                # Verificar condições de conexão
                connect = True
                if r is not None and euclidian_dist > r:
                    connect = False
                if d is not None and km_dist > d:
                    connect = False
                
                if connect:
                    # Decidir qual peso usar para a aresta (priorizando km se disponível)
                    weight = km_dist if d is not None else euclidian_dist
                    G.add_edge(city1['city'], city2['city'], 
                               weight=weight, 
                               euclidian_dist=euclidian_dist,
                               km_dist=km_dist)

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