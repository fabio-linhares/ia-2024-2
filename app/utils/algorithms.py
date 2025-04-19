import heapq
import math
import random
import time
from collections import deque
from functools import lru_cache

import networkx as nx
from app.utils.graph_utils import calculate_haversine_distance  # Corrigido o caminho de importação

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

# DIJKSTRA
####################################
def dijkstra_search(graph, cities_df, start, end):
    """
    Dijkstra bidirecional: inicia buscas simultâneas do início e do fim.
    Ultra-eficiente para caminhos ponto-a-ponto.
    Usa critérios plugáveis (população nos desempates) e aproveita cities_df se possível.

    Args:
        graph: NetworkX graph
        cities_df: DataFrame OU dict (nome->dados) com informações relevantes da cidade
        start: origem
        end: destino

    Return:
        path: lista de cidades no caminho ótimo, ou None
        total_dist: soma dos pesos das arestas do caminho
        elapsed_time_ms: duração (ms)
    """

    def get_population(n):
        # Usar DataFrame, dict (caso cities_df seja dict) ou fallback ao grafo
        if hasattr(cities_df, "loc"):
            try:
                if 'city' in cities_df.columns and 'population' in cities_df.columns:
                    sel = cities_df.loc[cities_df['city'] == n, 'population']
                    if not sel.empty:
                        return int(sel.values[0])
            except Exception:
                pass
        elif isinstance(cities_df, dict):
            p = cities_df.get(n, {}).get('population')
            if p is not None:
                return int(p)
        return int(graph.nodes[n].get('population', 0))

    start_time = time.perf_counter()
    if start not in graph or end not in graph:
        return None, float('inf'), 0

    # Inicialização para ambas as buscas
    distances_start = {node: float('inf') for node in graph.nodes()}
    distances_end = {node: float('inf') for node in graph.nodes()}
    parents_start = {node: None for node in graph.nodes()}
    parents_end = {node: None for node in graph.nodes()}

    distances_start[start] = 0
    distances_end[end] = 0

    heap_start = [(0, get_population(start), 0, start)]
    heap_end = [(0, get_population(end), 0, end)]

    visited_start = dict()
    visited_end = dict()
    counter = 0
    best_meeting = None
    best_path_len = float('inf')

    while heap_start and heap_end:
        # Expanda pelo lado que tem menor distância somada até agora (melhor balanceamento)
        if heap_start[0][0] + heap_end[0][0] > best_path_len:
            break

        # Expandir da origem
        if heap_start[0][0] <= heap_end[0][0]:
            dist, _, _, u = heapq.heappop(heap_start)
            if u in visited_start:
                continue
            visited_start[u] = dist

            # Checagem de encontro
            if u in visited_end:
                total_length = dist + visited_end[u]
                if total_length < best_path_len:
                    best_path_len = total_length
                    best_meeting = u

            for v in graph.neighbors(u):
                edge_data = graph.get_edge_data(u, v)
                weight = edge_data.get('weight', 1)
                alt = dist + weight
                if alt < distances_start[v]:
                    distances_start[v] = alt
                    parents_start[v] = u
                    counter += 1
                    heapq.heappush(heap_start, (alt, get_population(v), counter, v))

        # Expandir do destino
        else:
            dist, _, _, u = heapq.heappop(heap_end)
            if u in visited_end:
                continue
            visited_end[u] = dist

            if u in visited_start:
                total_length = dist + visited_start[u]
                if total_length < best_path_len:
                    best_path_len = total_length
                    best_meeting = u

            for v in graph.neighbors(u):
                # Como é busca reversa, devemos considerar arestas (v, u)
                edge_data = graph.get_edge_data(u, v)
                weight = edge_data.get('weight', 1)
                alt = dist + weight
                if alt < distances_end[v]:
                    distances_end[v] = alt
                    parents_end[v] = u
                    counter += 1
                    heapq.heappush(heap_end, (alt, get_population(v), counter, v))

    elapsed_time = (time.perf_counter() - start_time) * 1000

    if best_meeting is None:
        return None, float('inf'), elapsed_time

    # Use suas funções auxiliares plug-and-play para reconstruir e medir caminho!
    path = reconstruct_path(best_meeting, parents_start, parents_end)
    total_dist = path_distance(graph, path)
    return path, total_dist, elapsed_time

# FUZZY
####################################
def fuzzy_search(graph, cities_df, start, end, r=None, d=None):
    """
    Implementa busca fuzzy bidirecional aprimorada que balanceia distância e confiabilidade das conexões.
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
    from utils.graph_utils import calculate_haversine_distance
    start_time = time.perf_counter()
    
    if start not in graph or end not in graph:
        return None, float('inf'), 0, 0.0
    
    # Parâmetros configuráveis para a função de pertinência fuzzy
    fuzzy_params = {
        'alpha': 3.0,        # Limiar para certeza máxima (max_distance/alpha)
        'min_certainty': 0.1, # Valor mínimo de certeza
        'decay_factor': 0.9  # Fator de decaimento na interpolação
    }
    
    # Função de pertinência fuzzy parametrizada
    def membership_function(distance, max_distance, params=fuzzy_params):
        if distance <= max_distance / params['alpha']:
            return 1.0
        elif distance >= max_distance:
            return params['min_certainty']
        else:
            return 1.0 - (distance / max_distance) * params['decay_factor']
    
    # Função heurística para guiar a busca (distância Haversine até o destino)
    def heuristic(node, target):
        node_attrs = {'latitude': graph.nodes[node]['latitude'], 'longitude': graph.nodes[node]['longitude']}
        target_attrs = {'latitude': graph.nodes[target]['latitude'], 'longitude': graph.nodes[target]['longitude']}
        return calculate_haversine_distance(node_attrs, target_attrs)
    
    # Determinar a distância máxima permitida e tipo de distância
    if r is not None:
        max_distance = r
        distance_type = 'angular'
    elif d is not None:
        max_distance = d
        distance_type = 'km'
    else:
        max_distance = max([data['weight'] for _, _, data in graph.edges(data=True)], default=10.0)
        distance_type = 'weight'
    
    # Normalizar para distância em graus, se necessário
    norm_max_distance = max_distance
    if distance_type == 'km':
        norm_max_distance = max_distance / 111  # Aproximação km para graus
    
    # ----- ESTRUTURAS DE DADOS PARA BUSCA BIDIRECIONAL -----
    
    # Busca da origem
    certeza_start = {node: 0.0 for node in graph.nodes()}
    distances_start = {node: float('inf') for node in graph.nodes()}
    predecessors_start = {node: None for node in graph.nodes()}
    visited_start = set()
    certeza_start[start] = 1.0
    distances_start[start] = 0
    
    # Busca do destino
    certeza_end = {node: 0.0 for node in graph.nodes()}
    distances_end = {node: float('inf') for node in graph.nodes()}
    predecessors_end = {node: None for node in graph.nodes()}
    visited_end = set()
    certeza_end[end] = 1.0
    distances_end[end] = 0
    
    # Filas de prioridade para ambas as buscas
    # (-(certeza), distância + heurística, -população, contador, nó)
    # Usando -população para priorizar cidades MENORES
    counter = 0
    
    # Calcular heurísticas iniciais
    h_start = heuristic(start, end)
    h_end = heuristic(end, start)
    
    pq_start = [(-(certeza_start[start]), distances_start[start] + h_start, 
                 -(graph.nodes[start].get('population', 0)), counter, start)]
    counter += 1
    pq_end = [(-(certeza_end[end]), distances_end[end] + h_end, 
               -(graph.nodes[end].get('population', 0)), counter, end)]
    
    # Melhor ponto de encontro e suas métricas
    best_meeting_point = None
    best_path_certainty = 0.0
    best_path_length = float('inf')
    
    # ----- BUSCA BIDIRECIONAL -----
    while pq_start and pq_end:
        # Critério de parada antecipada
        if best_meeting_point and (-pq_start[0][0]) + (-pq_end[0][0]) < best_path_certainty:
            break
        
        # Decidir qual lado expandir (alternando ou balanceando fronteiras)
        expand_forward = len(visited_end) > len(visited_start)
        
        # --- Expandir da origem ---
        if expand_forward:
            _, f_score, _, _, current = heapq.heappop(pq_start)
            
            if current in visited_start:
                continue
                
            visited_start.add(current)
            
            # Verificar interseção com a busca reversa
            if current in visited_end:
                path_certainty = min(certeza_start[current], certeza_end[current])
                total_distance = distances_start[current] + distances_end[current]
                
                if (path_certainty > best_path_certainty or 
                    (path_certainty == best_path_certainty and total_distance < best_path_length)):
                    best_meeting_point = current
                    best_path_certainty = path_certainty
                    best_path_length = total_distance
            
            # Explorar vizinhos
            for neighbor in graph.neighbors(current):
                if neighbor in visited_start:
                    continue
                    
                edge_data = graph.get_edge_data(current, neighbor)
                edge_dist = edge_data['weight']
                
                # Ajustar distância conforme o tipo
                if distance_type == 'km' and 'km_dist' in edge_data:
                    edge_dist = edge_data['km_dist']
                elif distance_type == 'angular' and 'angular_dist' in edge_data:
                    edge_dist = edge_data['angular_dist']
                
                distance = distances_start[current] + edge_dist
                
                # Calcular certeza desta conexão
                edge_certainty = membership_function(edge_dist, norm_max_distance)
                new_certainty = min(certeza_start[current], edge_certainty)
                
                # Verificar se é melhor caminho
                if (new_certainty > certeza_start[neighbor] or 
                    (new_certainty == certeza_start[neighbor] and distance < distances_start[neighbor])):
                    certeza_start[neighbor] = new_certainty
                    distances_start[neighbor] = distance
                    predecessors_start[neighbor] = current
                    
                    # Calcular f_score (g + h) para priorização A*
                    h = heuristic(neighbor, end)
                    f_score = distance + h
                    counter += 1
                    
                    # Priorizar cidades com menor população
                    population = graph.nodes[neighbor].get('population', 0)
                    heapq.heappush(pq_start, (
                        -(new_certainty),   # Certeza (negativa para max heap)
                        f_score,            # Distância + heurística
                        -population,        # Prioriza cidades menores
                        counter,            # Desempate final
                        neighbor
                    ))
        
        # --- Expandir do destino ---
        else:
            _, f_score, _, _, current = heapq.heappop(pq_end)
            
            if current in visited_end:
                continue
                
            visited_end.add(current)
            
            # Verificar interseção
            if current in visited_start:
                path_certainty = min(certeza_start[current], certeza_end[current])
                total_distance = distances_start[current] + distances_end[current]
                
                if (path_certainty > best_path_certainty or 
                    (path_certainty == best_path_certainty and total_distance < best_path_length)):
                    best_meeting_point = current
                    best_path_certainty = path_certainty
                    best_path_length = total_distance
            
            # Busca reversa - explorar vizinhos
            for neighbor in graph.neighbors(current):
                if neighbor in visited_end:
                    continue
                    
                edge_data = graph.get_edge_data(current, neighbor)
                edge_dist = edge_data['weight']
                
                # Ajustar distância conforme o tipo
                if distance_type == 'km' and 'km_dist' in edge_data:
                    edge_dist = edge_data['km_dist']
                elif distance_type == 'angular' and 'angular_dist' in edge_data:
                    edge_dist = edge_data['angular_dist']
                
                distance = distances_end[current] + edge_dist
                
                # Calcular certeza
                edge_certainty = membership_function(edge_dist, norm_max_distance)
                new_certainty = min(certeza_end[current], edge_certainty)
                
                # Verificar se é melhor caminho
                if (new_certainty > certeza_end[neighbor] or 
                    (new_certainty == certeza_end[neighbor] and distance < distances_end[neighbor])):
                    certeza_end[neighbor] = new_certainty
                    distances_end[neighbor] = distance
                    predecessors_end[neighbor] = current
                    
                    # Calcular f_score para priorização A*
                    h = heuristic(neighbor, start)
                    f_score = distance + h
                    counter += 1
                    
                    # Priorizar cidades com menor população
                    population = graph.nodes[neighbor].get('population', 0)
                    heapq.heappush(pq_end, (
                        -(new_certainty),
                        f_score,
                        -population,
                        counter,
                        neighbor
                    ))
    
    elapsed_time = (time.perf_counter() - start_time) * 1000
    
    # Se não encontramos um ponto de encontro
    if best_meeting_point is None:
        return None, float('inf'), elapsed_time, 0.0
    
    # Reconstruir o caminho completo a partir do ponto de encontro
    path_start = []
    node = best_meeting_point
    while node is not None:
        path_start.append(node)
        node = predecessors_start.get(node)
    path_start.reverse()
    
    path_end = []
    node = predecessors_end.get(best_meeting_point)  # Não incluir o ponto de encontro duas vezes
    while node is not None:
        path_end.append(node)
        node = predecessors_end.get(node)
    
    # Caminho completo: início → ponto de encontro → fim
    path = path_start + path_end
    
    # Calcular distância total do caminho
    total_dist = 0
    for i in range(len(path) - 1):
        edge_data = graph.get_edge_data(path[i], path[i+1])
        if edge_data:
            if distance_type == 'km' and 'km_dist' in edge_data:
                total_dist += edge_data['km_dist']
            else:
                total_dist += edge_data['weight']
    
    return path, total_dist, elapsed_time, best_path_certainty

# DFS
####################################
def depth_first_search(graph, start, end, verbose=False, max_cost=None):
    """
    DFS aprimorado: heap de prioridade heurística, pruning por custo e max_cost, 
    logging detalhado, contagem de nós expandidos e desempate avançado.
    Args:
        graph: Grafo NetworkX
        start: nó de origem
        end: nó de destino
        verbose: ativa logs detalhados
        max_cost: (opcional) corta busca se custo parcial exceder
    Returns:
        path: lista com caminho ótimo do start ao end encontrado
        total_dist: custo total do caminho
        elapsed_time: tempo de execução (ms)
    """
    start_time = time.perf_counter()
    nodes_expanded = 0

    def heuristic(node):
        # Heurística básica: população (quanto menor, melhor); 
        pop = int(graph.nodes[node].get('population', 0))
        return pop

    # Early exit (restrição de custo máximo total, assim como no A*)
    if start not in graph or end not in graph:
        return None, float('inf'), 0

    stack = [(-0, 0, start, [start])]  # (prioridade, custo parcial, nó atual, caminho)
    best_costs = {start: 0}
    counter = 0  # Para desempate mais sofisticado como no A*
    log = []

    while stack:
        priority, total_dist, current, path = heapq.heappop(stack)
        nodes_expanded += 1

        if verbose:
            print(f"[DEBUG] Expande: {current} | custo: {total_dist} | prioridade: {-priority} | caminho: {path}")

        # Early exit (max_cost)
        if max_cost is not None and total_dist > max_cost:
            if verbose:
                print(f"[INFO] Early exit: custo {total_dist:.3f} excedeu limite {max_cost}.")
            continue

        if current == end:
            elapsed_time = (time.perf_counter() - start_time) * 1000
            if verbose:
                print(f"[INFO] Caminho encontrado em {elapsed_time:.2f} ms, nós expandidos: {nodes_expanded}")
            return path, total_dist, elapsed_time

        # Pruning por custo (melhor caminho já atingido)
        for neighbor in graph.neighbors(current):
            if neighbor in path:  # Evita ciclos
                continue
            edge_data = graph.get_edge_data(current, neighbor)
            new_dist = total_dist + edge_data.get('weight', 1)
            if neighbor not in best_costs or new_dist < best_costs[neighbor]:
                best_costs[neighbor] = new_dist
                new_path = path + [neighbor]

                # Critério de desempate mais sofisticado (tupla composta)
                tiebreaker = heuristic(neighbor)
                heapq.heappush(
                    stack, 
                    (-(new_dist + tiebreaker), new_dist, neighbor, new_path)
                )

    # Caminho não encontrado
    elapsed_time = (time.perf_counter() - start_time) * 1000
    if verbose:
        print(f"[WARN] Caminho não encontrado. Nós expandidos: {nodes_expanded}, tempo: {elapsed_time:.2f} ms")
    return None, float('inf'), elapsed_time

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

# BFS
####################################
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
    # Extrair as coordenadas das cidades como dicionários
    start_row = cities_df[cities_df['city'] == start_city].iloc[0]
    end_row = cities_df[cities_df['city'] == end_city].iloc[0]
    
    # Usar a função importada do graph_utils
    return calculate_haversine_distance(start_row, end_row)

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
        # Criar objetos com a latitude e longitude dos nós para usar com calculate_haversine_distance
        n_attrs = {'latitude': graph.nodes[n]['latitude'], 'longitude': graph.nodes[n]['longitude']}
        e_attrs = {'latitude': graph.nodes[end]['latitude'], 'longitude': graph.nodes[end]['longitude']}
        return calculate_haversine_distance(n_attrs, e_attrs)
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

    # Tiebreaker avançado — heurística, população, grau, hash
    def default_tiebreak(n):
        pop = graph.nodes[n].get('population', 0)
        grau = graph.degree[n]
        return (heuristic(n), -pop, -grau, hash(n)) 
    tiebreak = tiebreak_fn if tiebreak_fn else default_tiebreak

    # Alternativa usando rank e grau
    # def default_tiebreak(n):
    # rank = graph.nodes[n].get('rank', float('inf'))
    # grau = graph.degree[n]
    # return (heuristic(n), rank, -grau, hash(n))

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
    log = []  #  logging detalhado em memória

    while open_set:
        _, _, _, current = heapq.heappop(open_set)

        # Lazy update
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

        # Early exit — interrompe se já acima do custo máximo
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
