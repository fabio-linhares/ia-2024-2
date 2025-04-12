import networkx as nx
import heapq
from collections import deque
import math
import random

def breadth_first_search(graph, start, end):
    """Implementa a busca em largura."""
    if start not in graph or end not in graph:
        return None, float('inf')

    queue = deque([(start, [start], 0)])  # (node, path, distance)
    visited = set([start])

    while queue:
        node, path, distance = queue.popleft()
        
        if node == end:
            return path, distance
            
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                edge_dist = graph[node][neighbor]['weight']
                new_path = path + [neighbor]
                new_distance = distance + edge_dist
                queue.append((neighbor, new_path, new_distance))
                
    return None, float('inf')

def a_star_search(graph, cities_df, start, end):
    """Implementa o algoritmo A*."""
    if start not in graph or end not in graph:
        return None, float('inf')
    
    # Função heurística - distância em linha reta até o destino
    def heuristic(node1, node2):
        city1 = cities_df[cities_df['city'] == node1].iloc[0]
        city2 = cities_df[cities_df['city'] == node2].iloc[0]
        return math.sqrt((city1['latitude'] - city2['latitude'])**2 + 
                         (city1['longitude'] - city2['longitude'])**2)
    
    # Lista de nós a serem explorados
    open_list = [(0, start, [start], 0)]  # (f_score, node, path, g_score)
    # Nós já explorados
    closed_set = set()
    
    while open_list:
        f, current, path, g = heapq.heappop(open_list)
        
        if current == end:
            return path, g
        
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue
                
            tentative_g = g + graph[current][neighbor]['weight']
            
            # Desempate por população se houver empate na distância
            city_data = cities_df[cities_df['city'] == neighbor].iloc[0]
            population_factor = math.log(city_data['population']) / 100
            
            h = heuristic(neighbor, end) - population_factor
            f = tentative_g + h
            
            heapq.heappush(open_list, (f, neighbor, path + [neighbor], tentative_g))
    
    return None, float('inf')

def fuzzy_search(graph, cities_df, start, end, r):
    """Implementa a busca fuzzy com base na distância."""
    if start not in graph or end not in graph:
        return None, float('inf'), 0
    
    # Função de pertinência fuzzy - quanto menor a distância, maior a certeza
    def membership_function(distance, max_distance):
        if distance <= max_distance / 3:
            return 1.0
        elif distance >= max_distance:
            return 0.1
        else:
            return 1 - (distance / max_distance) * 0.9
    
    # Busca A* com componente fuzzy
    open_list = [(0, start, [start], 0, 1.0)]  # (f_score, node, path, g_score, certainty)
    closed_set = set()
    
    while open_list:
        f, current, path, g, certainty = heapq.heappop(open_list)
        
        if current == end:
            return path, g, certainty
        
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue
                
            edge_dist = graph[current][neighbor]['weight']
            tentative_g = g + edge_dist
            
            # Calcular certeza da conexão baseada na distância relativa ao raio
            edge_certainty = membership_function(edge_dist, r)
            new_certainty = min(certainty, edge_certainty)
            
            h = calculate_distance_from_df(cities_df, neighbor, end)
            f = tentative_g + h * (1 - new_certainty * 0.5)  # Quanto menor a certeza, maior o foco na heurística
            
            heapq.heappush(open_list, (f, neighbor, path + [neighbor], tentative_g, new_certainty))
    
    return None, float('inf'), 0

def calculate_distance_from_df(cities_df, city1_name, city2_name):
    """Calcula a distância entre duas cidades usando o DataFrame e a fórmula de Haversine."""
    city1 = cities_df[cities_df['city'] == city1_name].iloc[0]
    city2 = cities_df[cities_df['city'] == city2_name].iloc[0]
    
    # Usar a fórmula de Haversine para calcular a distância geodésica em km
    R = 6371.0  # Raio da Terra em km
    
    lat1_rad = math.radians(city1['latitude'])
    lon1_rad = math.radians(city1['longitude'])
    lat2_rad = math.radians(city2['latitude'])
    lon2_rad = math.radians(city2['longitude'])
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance_km = R * c
    
    # Para manter compatibilidade com o resto do código, retornamos também a distância em graus
    # que é usada internamente pelo algoritmo
    distance_degrees = math.sqrt((city1['latitude'] - city2['latitude'])**2 + 
                              (city1['longitude'] - city2['longitude'])**2)
    
    return distance_degrees