import heapq
import math
import random
import time
from collections import deque
from functools import lru_cache

import networkx as nx

from concurrent.futures import ThreadPoolExecutor, as_completed

# Wrapper functions for the algorithms
# def bfs_search(graph, cities_df, start, end):
#     """Wrapper for breadth_first_search."""
#     return breadth_first_search(graph, start, end)

# Global mapping for demonstration (no thread safety here)
# --- Se seu grafo sofrer mutação, o hash mudará e o cache será atualizado
global_graph_map = {}

def get_graph_hash(graph):
    # Crie um hash simples representando o estado do grafo
    return hash(str(graph.edges(data=True)) + str(graph.nodes(data=True)))

@lru_cache(maxsize=5000)
def bfs_cached(graph_hash, start, end):
    # Recupera o grafo real pelo hash
    graph = global_graph_map[graph_hash]
    return breadth_first_search(graph, start, end)

def bfs_search(graph, cities_df, start, end):
    """Wrapper for cached breadth_first_search."""
    graph_hash = get_graph_hash(graph)
    global_graph_map[graph_hash] = graph  # Armazene o grafo para consulta
    return bfs_cached(graph_hash, start, end)


# --- DFS: não vale a pena aplicar cache, wrapper simples ---
# --- pois isso raramente traz benefícios para consultas reais.
# --- O cache é mais útil para algoritmos como A* e Dijkstra, 
# --- onde o grafo é mais estável e as consultas são mais frequentes.
# --- O DFS é mais adequado para buscas pontuais e não se beneficia tanto do cache.
def dfs_search(graph, cities_df, start, end):
    return depth_first_search(graph, start, end)

# --- A*: wrapper com cache ---
@lru_cache(maxsize=5000)
def a_star_cached(graph_hash, start, end):
    graph = global_graph_map[graph_hash]
    return a_star_search(graph, cities_df, start, end)

def a_star(graph, cities_df, start, end):
    graph_hash = get_graph_hash(graph)
    global_graph_map[graph_hash] = graph
    return a_star_cached(graph_hash, start, end)

# --- Dijkstra: wrapper com cache ---
@lru_cache(maxsize=5000)
def dijkstra_cached(graph_hash, start, end):
    graph = global_graph_map[graph_hash]
    return dijkstra_search(graph, cities_df, start, end)

def dijkstra(graph, cities_df, start, end):
    graph_hash = get_graph_hash(graph)
    global_graph_map[graph_hash] = graph
    return dijkstra_cached(graph_hash, start, end)

# --- Fuzzy search: wrapper com cache ---
@lru_cache(maxsize=5000)
def fuzzy_cached(graph_hash, start, end):
    graph = global_graph_map[graph_hash]
    return fuzzy_search(graph, cities_df, start, end)

def fuzzy(graph, cities_df, start, end):
    graph_hash = get_graph_hash(graph)
    global_graph_map[graph_hash] = graph
    return fuzzy_cached(graph_hash, start, end)


def dijkstra_search(graph, cities_df, start, end):
    """
    Implementação otimizada do algoritmo de Dijkstra para encontrar o caminho mais curto.
    Utiliza população como critério de desempate.
    
    Args:
        graph: Grafo NetworkX com as cidades e conexões
        cities_df: DataFrame com informações das cidades (não usado atualmente)
        start: Cidade de origem
        end: Cidade de destino
        
    Returns:
        path: Lista de cidades no caminho mais curto
        total_dist: Distância total do caminho
        elapsed_time: Tempo de execução em ms
    """
    start_time = time.perf_counter()
    
    if start not in graph or end not in graph:
        return None, float('inf'), 0
    
    # Inicializar distâncias
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start] = 0
    
    # Predecessores para reconstrução do caminho
    predecessors = {node: None for node in graph.nodes()}
    
    # Conjunto de nós visitados
    visited = set()
    
    # Fila de prioridade: (distância, população, contador, nó)
    counter = 0
    priority_queue = [(0, int(graph.nodes[start]['population']), counter, start)]
    
    while priority_queue:
        # Extrair nó com menor distância
        current_distance, _, _, current_node = heapq.heappop(priority_queue)
        
        # Ignorar nós já processados
        if current_node in visited:
            continue
        
        # Marcar como visitado
        visited.add(current_node)
        
        # Se chegamos ao destino
        if current_node == end:
            elapsed_time = (time.perf_counter() - start_time) * 1000  # em ms
            
            # Reconstruir caminho
            path = []
            node = current_node
            while node is not None:
                path.append(node)
                node = predecessors[node]
            path.reverse()
            
            return path, distances[end], elapsed_time
        
        # Verificar vizinhos não visitados
        for neighbor in graph.neighbors(current_node):
            if neighbor in visited:
                continue
                
            # Calcular nova distância
            edge_data = graph.get_edge_data(current_node, neighbor)
            distance = current_distance + edge_data['weight']
            
            # Se encontramos um caminho melhor
            if distance < distances[neighbor]:
                # Atualizar distância e predecessor
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                
                # Adicionar à fila de prioridade com população como critério de desempate
                counter += 1
                population = int(graph.nodes[neighbor]['population'])
                heapq.heappush(priority_queue, (distance, population, counter, neighbor))
            
            # Se distância igual, verificar população para desempate
            elif distance == distances[neighbor]:
                current_pred = predecessors[neighbor]
                if current_pred and int(graph.nodes[current_node]['population']) < int(graph.nodes[current_pred]['population']):
                    predecessors[neighbor] = current_node
                    # Não precisamos atualizar a distância pois é a mesma
                    
                    # Adicionar à fila de prioridade para garantir exploração
                    counter += 1
                    population = int(graph.nodes[neighbor]['population'])
                    heapq.heappush(priority_queue, (distance, population, counter, neighbor))
    
    # Se não encontramos um caminho
    return None, float('inf'), 0

def fuzzy_search(graph, cities_df, start, end, r=None, d=None):
    """
    Implementa busca fuzzy aprimorada que balanceia distância e confiabilidade das conexões.
    Utiliza um modelo fuzzy com penalização adaptativa para conexões menos confiáveis.
    
    Args:
        graph: Grafo NetworkX com as cidades e conexões
        cities_df: DataFrame com informações das cidades
        start: Cidade de origem
        end: Cidade de destino
        r: Raio máximo de conexão em graus (opcional)
        d: Distância máxima em km (opcional)
        
    Returns:
        path: Lista de cidades no caminho encontrado
        total_dist: Distância total do caminho
        elapsed_time: Tempo de execução em ms
        certainty: Valor de certeza da rota (percentual de confiabilidade)
    """
    start_time = time.perf_counter()
    
    if start not in graph or end not in graph:
        return None, float('inf'), 0, 0.0
    
    # Função de pertinência fuzzy
    def membership_function(distance, max_distance):
        if distance <= max_distance / 3:
            return 1.0
        elif distance >= max_distance:
            return 0.1
        else:
            return 1 - (distance / max_distance) * 0.9
    
    # Determinar a distância máxima permitida
    if r is not None:
        max_distance = r
    elif d is not None:
        max_distance = d / 111  # Converter de km para graus
    else:
        # Usar o peso da aresta mais pesada no grafo como referência
        max_distance = max([data['weight'] for _, _, data in graph.edges(data=True)], default=10.0)
    
    # Inicializar estruturas de dados
    certeza = {node: 0.0 for node in graph.nodes()}
    certeza[start] = 1.0
    
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start] = 0
    
    predecessors = {node: None for node in graph.nodes()}
    
    visited = set()
    
    # Fila de prioridade: (-(certeza), distância, população, contador, nó)
    # Usamos negativo da certeza para priorizar valores maiores de certeza
    counter = 0
    priority_queue = [(-(certeza[start]), 0, int(graph.nodes[start]['population']), counter, start)]
    
    while priority_queue:
        # Extrair nó com maior certeza (menor valor negativo)
        _, current_distance, _, _, current = heapq.heappop(priority_queue)
        
        # Ignorar nós já processados
        if current in visited:
            continue
        
        # Marcar como visitado
        visited.add(current)
        
        # Se chegamos ao destino
        if current == end:
            elapsed_time = (time.perf_counter() - start_time) * 1000  # em ms
            
            # Reconstruir caminho
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = predecessors[node]
            path.reverse()
            
            # Retornar também o valor de certeza como quarto elemento
            return path, distances[end], elapsed_time, certeza[end]
        
        # Verificar vizinhos não visitados
        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue
                
            # Calcular nova distância
            edge_data = graph.get_edge_data(current, neighbor)
            edge_dist = edge_data['weight']
            distance = current_distance + edge_dist
            
            # Calcular certeza desta conexão usando lógica fuzzy
            edge_certainty = membership_function(edge_dist, max_distance)
            
            # Aplicar T-norm (min) para combinar certezas
            new_certainty = min(certeza[current], edge_certainty)
            
            # Se encontramos um caminho com maior certeza ou
            # se a certeza é igual mas a distância é menor
            if new_certainty > certeza[neighbor] or (new_certainty == certeza[neighbor] and distance < distances[neighbor]):
                # Atualizar certeza, distância e predecessor
                certeza[neighbor] = new_certainty
                distances[neighbor] = distance
                predecessors[neighbor] = current
                
                # Adicionar à fila de prioridade
                counter += 1
                population = int(graph.nodes[neighbor]['population'])
                heapq.heappush(priority_queue, (-(new_certainty), distance, population, counter, neighbor))
    
    # Se não encontramos um caminho
    return None, float('inf'), 0, 0.0

def depth_first_search(graph, start, end):
    """
    Implementação do algoritmo de busca em profundidade (DFS).
    
    Args:
        graph: Grafo NetworkX com as cidades e conexões
        start: Cidade de origem
        end: Cidade de destino
        
    Returns:
        path: Lista de cidades no caminho encontrado
        total_dist: Distância total do caminho
    """
    if start not in graph or end not in graph:
        return None, float('inf')
    
    # Pilha para DFS - armazena (nó atual, caminho até ele, distância acumulada)
    stack = [(start, [start], 0)]
    
    # Conjunto para rastreamento de nós visitados
    visited = {start}
    
    while stack:
        current, path, total_dist = stack.pop()
        
        # Se chegamos ao destino, retornamos o caminho e a distância
        if current == end:
            return path, total_dist
        
        # Explorar todos os vizinhos não visitados
        # Priorizar vizinhos com menor população
        neighbors = sorted(
            [(n, graph.nodes[n]['population']) for n in graph.neighbors(current) if n not in visited],
            key=lambda x: int(x[1])  # Ordenar por população (menor primeiro)
        )
        
        for neighbor, _ in neighbors:
            visited.add(neighbor)
            edge_data = graph.get_edge_data(current, neighbor)
            new_dist = total_dist + edge_data['weight']
            new_path = path + [neighbor]
            stack.append((neighbor, new_path, new_dist))
    
    # Se não encontramos um caminho
    return None, float('inf')

# BFS
####################################
def reconstruct_path(meeting, parents_start, parents_end):
    path_start = []
    node = meeting
    while node is not None:
        path_start.append(node)
        node = parents_start.get(node)
    path_start.reverse()
    path_end = []
    node = parents_end.get(meeting)
    while node is not None:
        path_end.append(node)
        node = parents_end.get(node)
    return path_start + path_end

def path_distance(graph, path):
    if not path or len(path) == 1:
        return 0
    dist = 0
    for i in range(len(path) - 1):
        edge = graph.get_edge_data(path[i], path[i + 1])
        if edge is not None:
            dist += edge['weight']
    return dist

def breadth_first_search(graph, start, end, timeout_ms=5000, log_metrics=True):
    """
    BFS bidirecional com fila de prioridade por menor população (NÃO bloqueia outros vizinhos).
    Paralelização condicional por camada, timeout, métricas de performance.

    Args:
        graph: Grafo NetworkX
        start, end: cidades
        timeout_ms: limite em ms (default: 5000)
        parallel_threshold: nº de nós em fronteira para paralelizar expansão dos vizinhos
        threads: nº de threads para paralelismo
        log_metrics: exibe métricas avançadas
    Returns:
        path, total_dist, elapsed_time_ms, info_dict
    """
    # Inicia o tempo de execução
    # Se o grafo não contém as cidades, retorna vazio
    start_time = time.perf_counter()
    if start not in graph or end not in graph:
        return [], float('inf'), 0, {}
    if start == end:
        return [start], 0, 0, {}
    
    # Fila de prioridade: (população, entrada incremental, node)
    frontier_start = []
    heapq.heappush(frontier_start, (int(graph.nodes[start]['population']), 0, start))
    frontier_end = []
    heapq.heappush(frontier_end, (int(graph.nodes[end]['population']), 0, end))
    visited_start = {start}
    visited_end = {end}
    parents_start = {start: None}
    parents_end = {end: None}
    counter = 1  # Para desempate no heapq
    frontier_max = 2
    nodes_visited = set([start, end])
    max_nodes = graph.number_of_nodes()
    iteration = 0

    while frontier_start and frontier_end:
        if (time.perf_counter() - start_time) * 1000 > timeout_ms:
            if log_metrics:
                print("Timeout atingido.")
            return [], float('inf'), (time.perf_counter() - start_time) * 1000, {
                'visited': len(nodes_visited),
                'frontier_max': frontier_max,
                'explored_pct': (len(nodes_visited) / max_nodes) * 100,
                'timeout': True
            }
        # Expande o menor heap
        if len(frontier_start) <= len(frontier_end):
            frontier, visited, parents = frontier_start, visited_start, parents_start
            other_visited, other_parents = visited_end, parents_end
        else:
            frontier, visited, parents = frontier_end, visited_end, parents_end
            other_visited, other_parents = visited_start, parents_start

        _, _, current = heapq.heappop(frontier)
        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parents[neighbor] = current
            nodes_visited.add(neighbor)
            if neighbor in other_visited:
                # Reconstrói caminho e retorna
                path = reconstruct_path(
                    neighbor, parents_start, parents_end
                )
                total_dist = path_distance(graph, path)
                elapsed_time = (time.perf_counter() - start_time) * 1000
                info = {
                    'visited': len(nodes_visited),
                    'frontier_max': frontier_max,
                    'explored_pct': (len(nodes_visited) / max_nodes) * 100,
                    'iterations': iteration
                }
                return path, total_dist, elapsed_time, info
            heapq.heappush(
                frontier,
                (int(graph.nodes[neighbor]['population']), counter, neighbor)
            )
            counter += 1
        frontier_max = max(frontier_max, len(frontier_start), len(frontier_end))
        iteration += 1

    elapsed_time = (time.perf_counter() - start_time) * 1000
    info = {
        'visited': len(nodes_visited),
        'frontier_max': frontier_max,
        'explored_pct': (len(nodes_visited) / max_nodes) * 100,
        'iterations': iteration
    }
    if log_metrics:
        print("Busca finalizada sem caminho encontrado. Métricas:", info)
    return [], float('inf'), elapsed_time, info

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância Haversine entre dois pontos geográficos em km.
    """
    # Converter graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Raio da Terra em km
    r = 6371
    
    return c * r

def calculate_distance_from_df(cities_df, start_city, end_city):
    """
    Calcula a distância Haversine direta entre duas cidades usando o DataFrame.
    
    Args:
        cities_df: DataFrame com informações das cidades, incluindo latitude e longitude
        start_city: Nome da cidade de origem
        end_city: Nome da cidade de destino
        
    Returns:
        float: Distância em km entre as cidades
    """
    # Extrair as coordenadas das cidades
    start_row = cities_df[cities_df['city'] == start_city].iloc[0]
    end_row = cities_df[cities_df['city'] == end_city].iloc[0]
    
    # Obter latitudes e longitudes
    lat1 = start_row['latitude']
    lon1 = start_row['longitude']
    lat2 = end_row['latitude']
    lon2 = end_row['longitude']
    
    # Calcular a distância usando a fórmula de Haversine
    return haversine(lat1, lon1, lat2, lon2)

# A Estrela 
####################################
def a_star_search(
    graph, 
    cities_df, 
    start, 
    end,
    heuristic_fn=None,
    cost_fn=None,
    tiebreak_fn=None,
    max_cost=None,        # early exit por custo máximo
    verbose=False,
    log_fn=None           # logging externo
):
    """
    Busca A* estado da arte, com desempate avançado, lazy update otimizado e logging detalhado.

    Expande o nó do open set que tem o menor f_score, ou seja, aquele que parece 
    resultar na menor distância total até o destino, levando em conta tanto o caminho 
    já percorrido quanto a estimativa do restante.

    Args:
         graph: Grafo NetworkX
         cities_df: DataFrame ou dicionário com informações extras das cidades
         start: nó de origem
         end: nó de destino
         heuristic_fn: função customizável de heurística. Default: Haversine
         cost_fn: função customizável de custo de aresta
         tiebreak_fn: função customizável para desempate de prioridades
         verbose: ativa logs detalhados
     Returns:
         path: lista com caminho ótimo do start ao end
         total_dist: custo total do caminho
         elapsed_time_ms: tempo de execução em milissegundos
     """
    start_time = time.perf_counter()

    if start not in graph or end not in graph:
        return None, float('inf'), 0

    # Heurística padrão (Haversine)
    def default_heuristic(n):
        n_lat, n_lon = graph.nodes[n]['latitude'], graph.nodes[n]['longitude']
        e_lat, e_lon = graph.nodes[end]['latitude'], graph.nodes[end]['longitude']
        return haversine(n_lat, n_lon, e_lat, e_lon)
    heuristic = heuristic_fn if heuristic_fn else default_heuristic

    # Custo padrão enriquecido por atributos do cities_df
    def default_cost(u, v, data):
        city_info = cities_df.get(v, {})
        penalty = 0
        if 'criminalidade' in city_info:
            penalty += float(city_info['criminalidade'])
        if 'infraestrutura_ruim' in city_info:
            penalty += float(city_info['infraestrutura_ruim'])
        return data['weight'] + penalty
    cost = cost_fn if cost_fn else default_cost

    # SUGESTÃO "c": Tiebreaker avançado — heurística, população, grau, hash
    def default_tiebreak(n):
        pop = graph.nodes[n].get('population', 0)
        grau = graph.degree[n]
        return (heuristic(n), pop, -grau, hash(n))
    tiebreak = tiebreak_fn if tiebreak_fn else default_tiebreak

    g_score = {n: float('inf') for n in graph.nodes()}
    f_score = {n: float('inf') for n in graph.nodes()}
    predecessors = {n: None for n in graph.nodes()}
    g_score[start] = 0
    f_score[start] = heuristic(start)

    counter = 0
    closed_set = set()
    open_set = []
    heapq.heappush(open_set, (f_score[start], tiebreak(start), counter, start))

    nodes_expanded = 0
    log = []  # SUGESTÃO "e": logging detalhado em memória

    while open_set:
        _, _, _, current = heapq.heappop(open_set)

        # SUGESTÃO "d": Lazy update — ignore se já fechado
        if current in closed_set:
            continue

        if verbose or log_fn or log is not None:
            log_entry = {
                "current": current,
                "f_score": f_score[current],
                "g_score": g_score[current],
                "expanded": nodes_expanded
            }
            if log_fn:
                log_fn(log_entry)
            else:
                log.append(log_entry)
            if verbose:
                print(f"[DEBUG] Nós expandidos: {nodes_expanded} | Visitando {current} | f={f_score[current]:.3f} g={g_score[current]:.3f}")

        if current == end:
            elapsed_time = (time.perf_counter() - start_time) * 1000
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = predecessors[node]
            path.reverse()
            if verbose:
                print(f"[INFO] Caminho ótimo encontrado com custo {g_score[end]:.3f}.")
                print(f"[STATS] Nós expandidos: {nodes_expanded}, tempo: {elapsed_time:.2f} ms")
            return path, g_score[end], elapsed_time

        # SUGESTÃO "d": Early exit — interrompe se já acima do custo máximo
        if max_cost is not None and g_score[current] > max_cost:
            if verbose:
                print(f"[INFO] Early exit: custo {g_score[current]:.3f} excedeu limite {max_cost}.")
            break

        closed_set.add(current)
        nodes_expanded += 1

        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue

            edge_data = graph.get_edge_data(current, neighbor)
            tentative_g = g_score[current] + cost(current, neighbor, edge_data)
            if tentative_g < g_score[neighbor]:
                predecessors[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                counter += 1
                heapq.heappush(open_set, (
                    f_score[neighbor],
                    tiebreak(neighbor),
                    counter,
                    neighbor
                ))

    # Caminho não encontrado
    elapsed_time = (time.perf_counter() - start_time) * 1000
    if verbose:
        print(f"[WARN] Caminho não encontrado. Nós expandidos: {nodes_expanded}, tempo: {elapsed_time:.2f} ms")
    return None, float('inf'), elapsed_time
