import networkx as nx
import heapq
from collections import deque
import math
import random
import time

# Wrapper functions for the algorithms
def bfs_search(graph, cities_df, start, end):
    """Wrapper for breadth_first_search."""
    return breadth_first_search(graph, start, end)

def dfs_search(graph, cities_df, start, end):
    """Wrapper for depth_first_search."""
    return depth_first_search(graph, start, end)

def a_star(graph, cities_df, start, end):
    """Wrapper for a_star_search."""
    return a_star_search(graph, cities_df, start, end)

def dijkstra(graph, cities_df, start, end):
    """Wrapper for dijkstra_search."""
    return dijkstra_search(graph, cities_df, start, end)

def fuzzy(graph, cities_df, start, end):
    """Wrapper for fuzzy_search."""
    return fuzzy_search(graph, cities_df, start, end)

class IterativeBFS:
    def __init__(self, graph, start, end):
        """
        Inicializa a busca BFS iterativa.
        
        Args:
            graph: Grafo NetworkX com as cidades e conexões
            start: Cidade de origem
            end: Cidade de destino
        """
        self.graph = graph
        self.start = start
        self.end = end
        self.queue = deque([(start, [start], 0)])  # (nó atual, caminho, distância)
        self.visited = {start}
        self.found = False
        self.current_path = []
        self.current_dist = 0
        self.start_time = time.perf_counter()
        self.elapsed_time = 0
        # Dados para visualização
        self.frontier_nodes = [start]
        self.visited_nodes = {start}
    
    def step(self):
        """
        Executa uma iteração do algoritmo BFS.
        
        Returns:
            bool: True se o algoritmo terminou (caminho encontrado ou impossível),
                  False se ainda há iterações a serem executadas
        """
        if not self.queue:
            # Não há mais nós para explorar, caminho não encontrado
            self.elapsed_time = (time.perf_counter() - self.start_time) * 1000  # em ms
            return True
        
        current, path, total_dist = self.queue.popleft()
        
        # Atualizar o caminho e distância atual para visualização
        self.current_path = path
        self.current_dist = total_dist
        
        # Remover o nó atual da fronteira
        if current in self.frontier_nodes:
            self.frontier_nodes.remove(current)
        
        # Se chegamos ao destino
        if current == self.end:
            self.found = True
            self.elapsed_time = (time.perf_counter() - self.start_time) * 1000  # em ms
            return True
        
        # Explorar vizinhos
        for neighbor in self.graph.neighbors(current):
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                self.visited_nodes.add(neighbor)
                
                # Adicionar à fronteira para visualização
                self.frontier_nodes.append(neighbor)
                
                # Calcular a nova distância
                edge_data = self.graph.get_edge_data(current, neighbor)
                new_dist = total_dist + edge_data['weight']
                new_path = path + [neighbor]
                
                # Adicionar à fila para exploração
                self.queue.append((neighbor, new_path, new_dist))
        
        return False  # Ainda não terminamos
    
    def get_iteration_data(self):
        """
        Retorna os dados da iteração atual para visualização.
        
        Returns:
            dict: Dicionário com os dados da iteração
        """
        return {
            'current_path': self.current_path,
            'current_dist': self.current_dist,
            'visited_nodes': list(self.visited_nodes),
            'frontier_nodes': self.frontier_nodes
        }
    
    def get_current_path(self):
        """
        Retorna o caminho atual.
        
        Returns:
            list: Lista de cidades no caminho atual
        """
        return self.current_path
    
    def get_current_dist(self):
        """
        Retorna a distância atual.
        
        Returns:
            float: Distância acumulada do caminho atual
        """
        return self.current_dist

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

def breadth_first_search(graph, start, end):
    """
    Implementação do algoritmo de busca em largura (BFS).
    
    Args:
        graph: Grafo NetworkX com as cidades e conexões
        start: Cidade de origem
        end: Cidade de destino
        
    Returns:
        path: Lista de cidades no caminho encontrado
        total_dist: Distância total do caminho
        elapsed_time: Tempo de execução em ms
    """
    start_time = time.perf_counter()
    
    if start not in graph or end not in graph:
        return None, float('inf'), 0
    
    # Fila FIFO para BFS - armazena (nó atual, caminho até ele, distância acumulada)
    queue = deque([(start, [start], 0)])
    
    # Conjunto para rastreamento de nós visitados
    visited = {start}
    
    while queue:
        current, path, total_dist = queue.popleft()
        
        # Se chegamos ao destino, retornamos o caminho e a distância
        if current == end:
            elapsed_time = (time.perf_counter() - start_time) * 1000  # em ms
            return path, total_dist, elapsed_time
        
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
            queue.append((neighbor, new_path, new_dist))
    
    # Se não encontramos um caminho
    return None, float('inf'), 0

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

def a_star_search(graph, cities_df, start, end):
    """
    Implementação do algoritmo A* para encontrar o caminho mais curto.
    
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
    
    # Heurística: distância Haversine direta entre dois pontos
    def heuristic(node):
        node_lat = graph.nodes[node]['latitude']
        node_lon = graph.nodes[node]['longitude']
        end_lat = graph.nodes[end]['latitude']
        end_lon = graph.nodes[end]['longitude']
        return haversine(node_lat, node_lon, end_lat, end_lon)
    
    # Inicializar valores
    g_score = {node: float('inf') for node in graph.nodes()}
    g_score[start] = 0
    
    f_score = {node: float('inf') for node in graph.nodes()}
    f_score[start] = heuristic(start)
    
    # Predecessores para reconstrução do caminho
    predecessors = {node: None for node in graph.nodes()}
    
    # Conjunto de nós visitados
    closed_set = set()
    
    # Contador para desempate em f_score igual
    counter = 0
    
    # Fila de prioridade: (f_score, g_score, população, contador, nó)
    open_set = [(f_score[start], 0, int(graph.nodes[start]['population']), counter, start)]
    
    while open_set:
        # Extrair nó com menor f_score
        _, current_g, _, _, current = heapq.heappop(open_set)
        
        # Ignorar nós já processados
        if current in closed_set:
            continue
        
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
            
            return path, g_score[end], elapsed_time
        
        # Marcar como visitado
        closed_set.add(current)
        
        # Verificar vizinhos não visitados
        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue
            
            # Calcular tentativa de g_score
            edge_data = graph.get_edge_data(current, neighbor)
            tentative_g = g_score[current] + edge_data['weight']
            
            # Se encontramos um caminho melhor
            if tentative_g < g_score[neighbor]:
                # Atualizar g_score e predecessor
                predecessors[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                
                # Adicionar à fila de prioridade
                counter += 1
                population = int(graph.nodes[neighbor]['population'])
                heapq.heappush(open_set, (f_score[neighbor], tentative_g, population, counter, neighbor))
            
            # Se g_score igual, verificar população para desempate
            elif tentative_g == g_score[neighbor]:
                current_pred = predecessors[neighbor]
                if current_pred and int(graph.nodes[current]['population']) < int(graph.nodes[current_pred]['population']):
                    predecessors[neighbor] = current
                    # Não precisamos atualizar g_score pois é o mesmo
                    
                    # Adicionar à fila de prioridade para garantir exploração
                    counter += 1
                    population = int(graph.nodes[neighbor]['population'])
                    heapq.heappush(open_set, (f_score[neighbor], tentative_g, population, counter, neighbor))
    
    # Se não encontramos um caminho
    return None, float('inf'), 0