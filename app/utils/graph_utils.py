import networkx as nx
import math
import pandas as pd

def build_graph(cities_df, r=None, d=None, name_to_id=None, id_to_name=None):
    """Constrói o grafo a partir dos dados das cidades,
    conectando cidades apenas se as distâncias entre elas respeitarem
    TODAS as restrições definidas (r e/ou d).
    
    Args:
        cities_df: DataFrame com dados das cidades
        r: Raio máximo (em graus) para conectar cidades
        d: Distância máxima (em km) para conectar cidades
        name_to_id: Dicionário de mapeamento de nome da cidade para ID
        id_to_name: Dicionário de mapeamento de ID para nome da cidade
        
    Returns:
        Um grafo NetworkX com as cidades como nós e conexões que respeitam os critérios
    """
    if r is None and d is None:
        raise ValueError("Pelo menos um dos parâmetros r ou d deve ser fornecido")
    
    G = nx.Graph()
    G.graph['r'] = r
    G.graph['d'] = d
    
    # Armazenar mapeamentos no grafo para conversão entre ID e nome
    G.graph['id_to_name'] = id_to_name or {}
    G.graph['name_to_id'] = name_to_id or {}
    
    # Primeiro passo: Adicionar nós ao grafo (apenas com latitude e longitude válidas)
    for _, row in cities_df.iterrows():
        if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
            # Usar city_id como identificador único em vez do nome da cidade
            node_id = int(row['city_id'])
            G.add_node(
                node_id,
                city=row['city'],
                state=row.get('state', ''),
                pos=(row['longitude'], row['latitude']),
                population=int(row['population']) if pd.notna(row['population']) else 0,
                latitude=row['latitude'],
                longitude=row['longitude']
            )
    
    # Para cada par de cidades distintas
    city_ids = list(G.nodes())
    for i in range(len(city_ids)):
        for j in range(i+1, len(city_ids)):
            city1_id = city_ids[i]
            city2_id = city_ids[j]
            
            # Obter atributos dos nós
            city1_attrs = G.nodes[city1_id]
            city2_attrs = G.nodes[city2_id]
            
            # Calcular distâncias
            angular_dist = calculate_angular_distance(city1_attrs, city2_attrs)
            km_dist = calculate_haversine_distance(city1_attrs, city2_attrs)
            
            # Verificar se as restrições são atendidas
            atende_raio = (r is None) or (angular_dist <= r)
            atende_dist_km = (d is None) or (km_dist <= d)
            
            # Se TODAS as restrições forem atendidas, as cidades devem estar conectadas
            if atende_raio and atende_dist_km:
                weight = km_dist if d is not None else angular_dist
                G.add_edge(
                    city1_id, city2_id,
                    weight=weight,
                    angular_dist=angular_dist,
                    km_dist=km_dist
                )
    
    return G

def build_graph_from_df(cities_df, r=None, d=None, name_to_id=None, id_to_name=None):
    """Wrapper para build_graph que facilita a construção do grafo a partir de um DataFrame.
    
    Args:
        cities_df: DataFrame com dados das cidades
        r: Raio máximo de conexão em graus (distância euclidiana)
        d: Distância máxima em quilômetros (usando Haversine)
        name_to_id: Dicionário de mapeamento de nome da cidade para ID
        id_to_name: Dicionário de mapeamento de ID para nome da cidade
        
    Returns:
        Um objeto networkx.Graph representando as cidades e suas conexões
    """
    return build_graph(cities_df, r=r, d=d, name_to_id=name_to_id, id_to_name=id_to_name)

def build_graph_from_df_km(cities_df, d_km, name_to_id=None, id_to_name=None):
    """Constrói o grafo a partir de um DataFrame usando distância em quilômetros.
    
    Esta função é um wrapper para build_graph que utiliza apenas o parâmetro de distância em km.
    
    Args:
        cities_df: DataFrame com dados das cidades
        d_km: Distância máxima em quilômetros para estabelecer conexões entre cidades
        name_to_id: Dicionário de mapeamento de nome da cidade para ID
        id_to_name: Dicionário de mapeamento de ID para nome da cidade
        
    Returns:
        Um objeto networkx.Graph representando as cidades e suas conexões
    """
    return build_graph(cities_df, r=None, d=d_km, name_to_id=name_to_id, id_to_name=id_to_name)

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

def calculate_angular_distance(city1, city2):
    """Calcula a distância angular (em graus) entre duas cidades."""
    lat1, lon1 = city1['latitude'], city1['longitude']
    lat2, lon2 = city2['latitude'], city2['longitude']
    
    # Distância angular usando a fórmula de Haversine, mas retornando em graus
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calcula a diferença de latitude e longitude
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula para calcular o ângulo central em radianos
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Converte de radianos para graus
    angle_in_degrees = math.degrees(c)
    
    return angle_in_degrees

def verify_graph_constraints(G):
    """
    Verifica se o grafo G respeita as restrições de raio (r) e distância (d) 
    que foram utilizadas na sua construção.
    
    Args:
        G: Grafo NetworkX a ser verificado
        
    Returns:
        Um dicionário contendo:
        - is_valid: Booleano indicando se todas as arestas respeitam as restrições
        - invalid_edges: Lista de tuplas (cidade1, cidade2) que violam as restrições
        - stats: Estatísticas sobre o grafo e suas arestas
    """
    r = G.graph.get('r')
    d = G.graph.get('d')
    
    if r is None and d is None:
        return {
            'is_valid': False,
            'error': "O grafo não possui restrições de raio (r) ou distância (d) definidas",
            'invalid_edges': [],
            'stats': {}
        }
    
    invalid_edges = []
    total_edges = G.number_of_edges()
    
    # Estatísticas
    stats = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': total_edges,
        'avg_degree': (2 * total_edges) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0,
        'min_angular_dist': float('inf'),
        'max_angular_dist': 0,
        'min_km_dist': float('inf'),
        'max_km_dist': 0,
        'r_constraint': r,
        'd_constraint': d
    }
    
    # Verificar cada aresta
    for u, v, edge_data in G.edges(data=True):
        # Obter as distâncias da aresta
        angular_dist = edge_data.get('angular_dist')
        km_dist = edge_data.get('km_dist')
        
        # Atualizar estatísticas
        if angular_dist is not None:
            stats['min_angular_dist'] = min(stats['min_angular_dist'], angular_dist)
            stats['max_angular_dist'] = max(stats['max_angular_dist'], angular_dist)
        
        if km_dist is not None:
            stats['min_km_dist'] = min(stats['min_km_dist'], km_dist)
            stats['max_km_dist'] = max(stats['max_km_dist'], km_dist)
        
        # Verificar se a aresta respeita as restrições
        violates_r = r is not None and angular_dist > r
        violates_d = d is not None and km_dist > d
        
        if violates_r or violates_d:
            city1_name = G.nodes[u].get('city', f'ID {u}')
            city2_name = G.nodes[v].get('city', f'ID {v}')
            invalid_edges.append({
                'city1': city1_name,
                'city2': city2_name,
                'angular_dist': angular_dist,
                'km_dist': km_dist,
                'r_violated': violates_r,
                'd_violated': violates_d
            })
    
    # Corrigir valores infinitos nas estatísticas se não houver arestas
    if stats['min_angular_dist'] == float('inf'):
        stats['min_angular_dist'] = None
    if stats['min_km_dist'] == float('inf'):
        stats['min_km_dist'] = None
    
    return {
        'is_valid': len(invalid_edges) == 0,
        'invalid_edges': invalid_edges,
        'stats': stats
    }