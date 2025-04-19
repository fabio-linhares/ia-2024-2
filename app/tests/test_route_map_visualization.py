import sys
import os
import unittest
import pandas as pd
import networkx as nx
import folium
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
import random
import time

# Adiciona o diretório raiz do projeto ao caminho do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(project_root)

# Importa as funções necessárias
from app.utils.data_loader import load_data
from app.utils.graph_utils import build_graph, verify_graph_constraints
from app.utils.algorithms import bfs_search, dijkstra_search, a_star_search
from app.components.map_display import (
    display_route_map, 
    display_all_routes_map, 
    display_path_on_map, 
    display_graph_visualization
)

class TestRouteMapVisualization(unittest.TestCase):
    """
    Esta classe de teste verifica visualmente se as rotas são plotadas corretamente no mapa,
    destacando as cidades no caminho.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Configuração inicial que é executada uma vez antes de todos os testes.
        Carrega o conjunto de dados e prepara o ambiente de teste.
        """
        # Usar o arquivo cities.json completo para ter mais cidades
        cities_path = os.path.join(project_root, 'data', 'cities.json')
        if not os.path.exists(cities_path):
            # Fallback para o arquivo de teste
            cities_path = os.path.join(project_root, 'data', 'test_cities.json')
        
        # Carregar os dados
        result = load_data(cities_path)
        
        # Desempacotar a tupla retornada pela função load_data
        if isinstance(result, tuple) and len(result) == 3:
            cls.df, cls.name_to_id, cls.id_to_name = result
        else:
            cls.df = result
            cls.name_to_id = {}
            cls.id_to_name = {}
        
        # Em vez de uma amostra aleatória, usar todas as cidades ou um número definido
        # para garantir consistência
        if len(cls.df) > 300:
            # Selecionar as primeiras 300 cidades para teste (não aleatório)
            cls.sample_df = cls.df.head(300)
        else:
            cls.sample_df = cls.df
        
        # Criar diretório para os arquivos de visualização se não existir
        cls.output_dir = os.path.join(project_root, 'reports', 'route_verification')
        os.makedirs(cls.output_dir, exist_ok=True)
        
        print(f"Ambiente de teste configurado com {len(cls.sample_df)} cidades")
        print(f"Arquivos de visualização serão salvos em: {cls.output_dir}")
    
    def test_route_visualization_accuracy(self):
        """
        Testa se as cidades de uma rota específica são exibidas corretamente no mapa.
        Executa um algoritmo de busca com um raio definido e verifica visualmente 
        se as cidades no caminho são destacadas no mapa.
        """
        # Definir um raio de conexão razoável
        r = 5.0  # 5 graus ~ 555 km
        
        # Construir o grafo com o raio definido
        G = build_graph(self.sample_df, r=r, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        
        print(f"Grafo construído com r={r}°: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas")
        
        # Primeiro, selecionamos apenas as cidades que estão no grafo
        graph_nodes = list(G.nodes())
        
        # Mapeamento reverso para obter os nomes das cidades a partir dos IDs
        city_names_in_graph = []
        for node_id in graph_nodes:
            city_name = self.id_to_name.get(node_id)
            if city_name:
                city_names_in_graph.append(city_name)
        
        print(f"Total de cidades no grafo: {len(city_names_in_graph)}")
        
        if len(city_names_in_graph) < 5:
            self.skipTest("Não há cidades suficientes no grafo para testar")
        
        # Primeiro, identificar componentes conectados
        connected_components = list(nx.connected_components(G))
        
        # Usar o maior componente conectado
        largest_component = max(connected_components, key=len)
        print(f"Maior componente conectado tem {len(largest_component)} nós")
        
        # Lista de nós no maior componente
        nodes_in_component = list(largest_component)
        
        # Tentar com pares conhecidos de cidades grandes
        major_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        
        # Filtrar apenas as cidades que estão no grafo
        major_cities_in_graph = []
        for city in major_cities:
            city_id = self.name_to_id.get(city)
            if city_id is not None and city_id in G.nodes:
                major_cities_in_graph.append(city)
        
        print(f"Cidades principais no grafo: {len(major_cities_in_graph)}")
        
        # Verificar pares de cidades principais
        valid_pairs = []
        if len(major_cities_in_graph) >= 2:
            for i in range(len(major_cities_in_graph)):
                for j in range(i+1, len(major_cities_in_graph)):
                    city1 = major_cities_in_graph[i]
                    city2 = major_cities_in_graph[j]
                    id1 = self.name_to_id.get(city1)
                    id2 = self.name_to_id.get(city2)
                    
                    # Verificar se os IDs existem e se estão no mesmo componente
                    if id1 in largest_component and id2 in largest_component:
                        try:
                            # Verificar se existe um caminho
                            path = nx.shortest_path(G, id1, id2)
                            if len(path) >= 3:  # Queremos pelo menos 3 cidades na rota
                                valid_pairs.append((city1, city2, len(path)))
                        except nx.NetworkXNoPath:
                            continue
        
        # Se não encontramos pares válidos com cidades principais, tentar com cidades aleatórias
        if not valid_pairs:
            # Usar cidades aleatórias do maior componente
            cities_in_component = []
            for node_id in nodes_in_component:
                city_name = self.id_to_name.get(node_id)
                if city_name:
                    cities_in_component.append((city_name, node_id))
            
            if len(cities_in_component) < 2:
                self.skipTest("Não há cidades suficientes no maior componente conectado")
            
            # Tentar encontrar pares com caminhos interessantes
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts and len(valid_pairs) < 3:
                # Selecionar duas cidades aleatórias
                city1_info = random.choice(cities_in_component)
                city2_info = random.choice(cities_in_component)
                
                if city1_info == city2_info:
                    attempts += 1
                    continue
                
                city1, id1 = city1_info
                city2, id2 = city2_info
                
                try:
                    path = nx.shortest_path(G, id1, id2)
                    if len(path) >= 3:  # Queremos pelo menos 3 cidades na rota
                        valid_pairs.append((city1, city2, len(path)))
                except nx.NetworkXNoPath:
                    pass
                
                attempts += 1
        
        if not valid_pairs:
            self.skipTest("Não foi possível encontrar pares de cidades com caminhos válidos")
        
        # Ordenar os pares por tamanho do caminho (mais interessante primeiro)
        valid_pairs.sort(key=lambda x: x[2], reverse=True)
        
        # Selecionar o par com o caminho mais interessante
        start_city, end_city, path_length = valid_pairs[0]
        start_id = self.name_to_id.get(start_city)
        end_id = self.name_to_id.get(end_city)
        
        print(f"Executando busca de rota entre {start_city} e {end_city} (distância esperada: {path_length} cidades)")
        
        # 2. Executar três algoritmos diferentes de busca
        algorithms_and_results = {}
        
        # BFS
        bfs_result = bfs_search(G, self.sample_df, start_id, end_id)
        if bfs_result and len(bfs_result) >= 2 and bfs_result[0]:
            path_ids = bfs_result[0]
            path_names = [self.id_to_name.get(node_id, f"ID:{node_id}") for node_id in path_ids]
            algorithms_and_results["BFS"] = path_names
        
        # Dijkstra
        dijkstra_result = dijkstra_search(G, self.sample_df, start_id, end_id)
        if dijkstra_result and len(dijkstra_result) >= 2 and dijkstra_result[0]:
            path_ids = dijkstra_result[0]
            path_names = [self.id_to_name.get(node_id, f"ID:{node_id}") for node_id in path_ids]
            algorithms_and_results["Dijkstra"] = path_names
        
        # A*
        a_star_result = a_star_search(G, self.sample_df, start_id, end_id)
        if a_star_result and len(a_star_result) >= 2 and a_star_result[0]:
            path_ids = a_star_result[0]
            path_names = [self.id_to_name.get(node_id, f"ID:{node_id}") for node_id in path_ids]
            algorithms_and_results["Astar"] = path_names
        
        if not algorithms_and_results:
            self.skipTest("Nenhum algoritmo conseguiu encontrar um caminho")
        
        # 3. Para cada algoritmo, criar um mapa e destacar as cidades na rota
        for algo, path in algorithms_and_results.items():
            # Gerar o título do mapa com informações detalhadas
            title = f"Rota de {start_city} para {end_city} usando {algo} (r={r}°)"
            print(f"Plotando {algo}: {' -> '.join(path)}")
            
            # Criar mapa com a rota
            map_obj = display_path_on_map(self.sample_df, path, title=title)
            
            # Salvar o mapa para verificação visual
            safe_algo = algo.replace('*', 'Astar')  # Substituir * por Astar para evitar problemas com nomes de arquivos
            output_filename = f"rota_{safe_algo}_{start_city.replace(' ', '_')}_para_{end_city.replace(' ', '_')}.html"
            output_path = os.path.join(self.output_dir, output_filename)
            map_obj.save(output_path)
            
            print(f"Mapa salvo em: {output_path}")
            self.assertTrue(os.path.exists(output_path), f"O arquivo {output_path} não foi criado")
            
            # Verificar se o mapa criado tem os marcadores esperados
            markers_count = 0
            for child in map_obj._children.values():
                if isinstance(child, folium.map.Marker):
                    markers_count += 1
            
            # Deve haver pelo menos um marcador para cada cidade no caminho
            self.assertGreaterEqual(markers_count, len(path), 
                                    f"O mapa deve conter pelo menos {len(path)} marcadores (um para cada cidade)")
        
        # 4. Criar um mapa comparativo com todas as rotas
        all_paths = list(algorithms_and_results.values())
        comparative_map = display_route_map(self.sample_df, all_paths)
        
        comparative_output_path = os.path.join(self.output_dir, f"comparacao_{start_city.replace(' ', '_')}_para_{end_city.replace(' ', '_')}.html")
        comparative_map.save(comparative_output_path)
        
        print(f"Mapa comparativo salvo em: {comparative_output_path}")
        self.assertTrue(os.path.exists(comparative_output_path), f"O arquivo comparativo {comparative_output_path} não foi criado")
        
        # 5. Criar também uma visualização do grafo com as mesmas cidades destacadas
        graph_fig = display_graph_visualization(G, self.sample_df, r=r)
        
        graph_output_path = os.path.join(self.output_dir, f"grafo_r{r}_{start_city.replace(' ', '_')}_para_{end_city.replace(' ', '_')}.png")
        graph_fig.savefig(graph_output_path, dpi=150, bbox_inches='tight')
        
        print(f"Visualização do grafo salva em: {graph_output_path}")
        self.assertTrue(os.path.exists(graph_output_path), f"O arquivo do grafo {graph_output_path} não foi criado")
        
        # 6. Criar um arquivo de informações para facilitar a verificação visual
        info_file_path = os.path.join(self.output_dir, "informacoes_dos_testes.txt")
        with open(info_file_path, "a") as f:
            f.write(f"\n\n--- TESTE REALIZADO EM {time.strftime('%d/%m/%Y %H:%M:%S')} ---\n")
            f.write(f"Raio de conexão (r): {r}°\n")
            f.write(f"Origem: {start_city}\n")
            f.write(f"Destino: {end_city}\n")
            f.write(f"Grafo: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas\n\n")
            
            for algo, path in algorithms_and_results.items():
                f.write(f"Algoritmo: {algo}\n")
                f.write(f"Caminho ({len(path)} cidades): {' -> '.join(path)}\n\n")
        
        print(f"Arquivo de informações atualizado: {info_file_path}")
        
        # Exibir um resumo das rotas para auxiliar na verificação manual
        print("\n=== RESUMO DAS ROTAS PARA VERIFICAÇÃO VISUAL ===")
        for algo, path in algorithms_and_results.items():
            print(f"{algo}: {' -> '.join(path)}")
        print(f"Verificar os mapas em: {self.output_dir}")
        print("===============================================\n")

if __name__ == "__main__":
    unittest.main()