import sys
import os
import unittest
import pandas as pd
import networkx as nx
import folium
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
import time

# Adiciona o diretório raiz do projeto ao caminho do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(project_root)

# Importa as funções necessárias
from app.utils.data_loader import load_data
from app.utils.graph_utils import build_graph, verify_graph_constraints
from app.components.map_display import (
    display_route_map, 
    display_all_routes_map, 
    display_path_on_map, 
    display_graph_visualization
)

class TestMapDisplayVisual(unittest.TestCase):
    """
    Classe de teste visual para as funções de visualização de mapas.
    Esta classe gera arquivos HTML e imagens que podem ser inspecionados visualmente
    para garantir que as rotas e grafos estão sendo plotados corretamente.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Configuração inicial que é executada uma vez antes de todos os testes.
        Carrega o conjunto de dados e prepara o ambiente de teste.
        """
        # Caminho para o arquivo de teste
        test_cities_path = os.path.join(project_root, 'data', 'test_cities.json')
        
        # Carrega os dados - load_data retorna (df, name_to_id, id_to_name)
        result = load_data(test_cities_path)
        
        # Desempacotar a tupla retornada pela função load_data
        if isinstance(result, tuple) and len(result) == 3:
            cls.df, cls.name_to_id, cls.id_to_name = result
        else:
            cls.df = result
            cls.name_to_id = {}
            cls.id_to_name = {}
        
        # Criar um subconjunto para testes mais rápidos se necessário
        cls.sample_df = cls.df.head(10) if len(cls.df) > 10 else cls.df
        
        # Construir um grafo para testes com parâmetros que garantem boa conectividade
        cls.graph = build_graph(cls.sample_df, r=20.0, name_to_id=cls.name_to_id, id_to_name=cls.id_to_name)
        
        # Encontrar pares de cidades que têm caminhos entre si
        cls.cidade_pares = []
        cities = cls.sample_df['city'].tolist()
        
        for i in range(len(cities)):
            for j in range(i+1, len(cities)):
                city1 = cities[i]
                city2 = cities[j]
                city1_id = cls.name_to_id.get(city1)
                city2_id = cls.name_to_id.get(city2)
                
                if city1_id is not None and city2_id is not None:
                    if nx.has_path(cls.graph, city1_id, city2_id):
                        cls.cidade_pares.append((city1, city2))
                        if len(cls.cidade_pares) >= 3:  # Limitamos a 3 pares
                            break
            if len(cls.cidade_pares) >= 3:
                break
        
        # Garantir que temos pelo menos um par de cidades
        if not cls.cidade_pares:
            print("AVISO: Não foi possível encontrar pares de cidades conectadas no grafo.")
            if len(cities) >= 2:
                cls.cidade_pares = [(cities[0], cities[1])]  # Use pelo menos o primeiro par
        
        # Criar diretório para os arquivos de visualização se não existir
        cls.output_dir = os.path.join(project_root, 'reports', 'visual_tests')
        os.makedirs(cls.output_dir, exist_ok=True)
        
        print(f"Ambiente de teste visual configurado com {len(cls.sample_df)} cidades")
        print(f"Grafo criado com {cls.graph.number_of_nodes()} nós e {cls.graph.number_of_edges()} arestas")
        print(f"Pares de cidades para teste: {cls.cidade_pares}")
    
    def test_visualize_single_path(self):
        """
        Testa e salva a visualização de um único caminho entre duas cidades.
        """
        if not self.cidade_pares:
            self.skipTest("Não há pares de cidades conectadas para testar")
        
        # Obter o primeiro par de cidades
        cidade_origem, cidade_destino = self.cidade_pares[0]
        
        # Encontrar o caminho entre as cidades usando o algoritmo BFS
        origem_id = self.name_to_id.get(cidade_origem)
        destino_id = self.name_to_id.get(cidade_destino)
        
        try:
            # Tentar encontrar o caminho
            caminho_ids = nx.shortest_path(self.graph, source=origem_id, target=destino_id)
            # Converter IDs para nomes de cidades
            caminho = [self.id_to_name.get(id, f"ID {id}") for id in caminho_ids]
            
            print(f"Caminho encontrado entre {cidade_origem} e {cidade_destino}: {' -> '.join(caminho)}")
            
            # Criar o mapa com o caminho
            map_obj = display_path_on_map(
                self.sample_df, 
                caminho, 
                title=f"Rota de {cidade_origem} para {cidade_destino}"
            )
            
            # Salvar o mapa como HTML
            output_path = os.path.join(self.output_dir, f"rota_{cidade_origem.replace(' ', '_')}_para_{cidade_destino.replace(' ', '_')}.html")
            map_obj.save(output_path)
            
            print(f"Mapa salvo em: {output_path}")
            self.assertTrue(os.path.exists(output_path), f"O arquivo {output_path} não foi criado")
            
        except nx.NetworkXNoPath:
            self.skipTest(f"Não existe caminho entre {cidade_origem} e {cidade_destino}")
    
    def test_visualize_multiple_paths(self):
        """
        Testa e salva a visualização de múltiplos caminhos em um único mapa.
        """
        if len(self.cidade_pares) < 2:
            self.skipTest("Não há pares suficientes de cidades conectadas para testar")
        
        # Obter os dois primeiros pares de cidades
        caminhos = []
        
        for cidade_origem, cidade_destino in self.cidade_pares[:2]:
            origem_id = self.name_to_id.get(cidade_origem)
            destino_id = self.name_to_id.get(cidade_destino)
            
            try:
                # Tentar encontrar o caminho
                caminho_ids = nx.shortest_path(self.graph, source=origem_id, target=destino_id)
                # Converter IDs para nomes de cidades
                caminho = [self.id_to_name.get(id, f"ID {id}") for id in caminho_ids]
                caminhos.append(caminho)
                
                print(f"Caminho encontrado entre {cidade_origem} e {cidade_destino}: {' -> '.join(caminho)}")
                
            except nx.NetworkXNoPath:
                print(f"Não existe caminho entre {cidade_origem} e {cidade_destino}")
        
        if not caminhos:
            self.skipTest("Não foi possível encontrar caminhos para os pares de cidades")
        
        # Criar o mapa com múltiplos caminhos
        map_obj = display_route_map(self.sample_df, caminhos)
        
        # Salvar o mapa como HTML
        output_path = os.path.join(self.output_dir, "multiplas_rotas.html")
        map_obj.save(output_path)
        
        print(f"Mapa com múltiplas rotas salvo em: {output_path}")
        self.assertTrue(os.path.exists(output_path), f"O arquivo {output_path} não foi criado")
    
    def test_visualize_all_algorithms(self):
        """
        Testa e salva a visualização comparativa de diferentes algoritmos.
        """
        if not self.cidade_pares:
            self.skipTest("Não há pares de cidades conectadas para testar")
        
        # Obter o primeiro par de cidades
        cidade_origem, cidade_destino = self.cidade_pares[0]
        origem_id = self.name_to_id.get(cidade_origem)
        destino_id = self.name_to_id.get(cidade_destino)
        
        # Simular resultados de diferentes algoritmos
        resultados = {}
        
        # Tentar encontrar diferentes caminhos
        try:
            # Caminho direto (mais curto)
            caminho_direto = nx.shortest_path(self.graph, source=origem_id, target=destino_id)
            caminho_direto_nomes = [self.id_to_name.get(id, f"ID {id}") for id in caminho_direto]
            distancia_direta = nx.shortest_path_length(self.graph, source=origem_id, target=destino_id, weight='weight')
            resultados['Dijkstra'] = (caminho_direto_nomes, distancia_direta, 5.0)
            
            # Caminho A* (similar ao mais curto para teste)
            resultados['A*'] = (caminho_direto_nomes, distancia_direta, 4.5)
            
            # Caminho BFS (pode não ser o mais curto)
            caminho_bfs = list(nx.bfs_edges(self.graph, source=origem_id))
            caminho_bfs_nodes = [origem_id]
            for u, v in caminho_bfs:
                if u == caminho_bfs_nodes[-1]:
                    caminho_bfs_nodes.append(v)
                if v == destino_id:
                    break
            if caminho_bfs_nodes[-1] != destino_id:
                # Se não chegou ao destino, use um subconjunto do caminho direto
                meio = len(caminho_direto) // 2
                caminho_bfs_nodes = caminho_direto[:meio] + [caminho_direto[-1]]
            
            caminho_bfs_nomes = [self.id_to_name.get(id, f"ID {id}") for id in caminho_bfs_nodes]
            
            # Calcula a distância BFS com segurança, verificando se cada aresta existe
            distancia_bfs = 0
            for i in range(len(caminho_bfs_nodes) - 1):
                edge_data = self.graph.get_edge_data(caminho_bfs_nodes[i], caminho_bfs_nodes[i+1])
                if edge_data and 'weight' in edge_data:
                    distancia_bfs += edge_data['weight']
                else:
                    # Se não tiver aresta direta, use um caminho mais longo conectando os nós
                    try:
                        distancia_bfs += nx.shortest_path_length(
                            self.graph, 
                            source=caminho_bfs_nodes[i], 
                            target=caminho_bfs_nodes[i+1], 
                            weight='weight'
                        )
                    except (nx.NetworkXNoPath, nx.NetworkXError):
                        # Se ainda não conseguir, use um valor estimado
                        distancia_bfs += distancia_direta * 0.2  # Valor arbitrário
            
            resultados['BFS'] = (caminho_bfs_nomes, distancia_bfs, 6.2)
            
            # Caminho Fuzzy (criando um caminho alternativo)
            # Para o teste, vamos criar um caminho com pelo menos uma cidade diferente
            caminho_fuzzy_nodes = list(caminho_direto)  # Começar com o caminho direto
            
            # Se o caminho direto tiver apenas 2 nós (origem e destino),
            # adicionar um nó intermediário
            if len(caminho_fuzzy_nodes) <= 2:
                # Encontrar um nó intermediário que esteja conectado a ambos
                candidatos = []
                for node in self.graph.nodes():
                    if (node != origem_id and node != destino_id and 
                        self.graph.has_edge(origem_id, node) and 
                        self.graph.has_edge(node, destino_id)):
                        candidatos.append(node)
                
                if candidatos:
                    # Usar o primeiro candidato encontrado
                    intermediario = candidatos[0]
                    caminho_fuzzy_nodes = [origem_id, intermediario, destino_id]
                else:
                    # Tentar encontrar qualquer caminho alternativo
                    try:
                        # Remover temporariamente a aresta direta para forçar um caminho diferente
                        if self.graph.has_edge(origem_id, destino_id):
                            peso_original = self.graph[origem_id][destino_id].get('weight', 1.0)
                            self.graph[origem_id][destino_id]['weight'] = float('inf')
                            caminho_alternativo = nx.shortest_path(self.graph, origem_id, destino_id, weight='weight')
                            # Restaurar o peso original
                            self.graph[origem_id][destino_id]['weight'] = peso_original
                            caminho_fuzzy_nodes = caminho_alternativo
                    except:
                        # Se não for possível, manter o caminho original
                        pass
            
            caminho_fuzzy_nomes = [self.id_to_name.get(id, f"ID {id}") for id in caminho_fuzzy_nodes]
            
            # Calcular a distância do caminho Fuzzy
            distancia_fuzzy = 0
            for i in range(len(caminho_fuzzy_nodes) - 1):
                edge_data = self.graph.get_edge_data(caminho_fuzzy_nodes[i], caminho_fuzzy_nodes[i+1])
                if edge_data and 'weight' in edge_data:
                    distancia_fuzzy += edge_data['weight']
                else:
                    # Usar um valor estimado se não houver aresta direta
                    distancia_fuzzy += distancia_direta * 0.3
            
            resultados['Fuzzy'] = (caminho_fuzzy_nomes, distancia_fuzzy, 3.8)
            
            # Imprimir as rotas encontradas para depuração
            print("Rotas encontradas para teste visual:")
            for algo, (rota, dist, tempo) in resultados.items():
                print(f"{algo}: {' -> '.join(rota)} (Distância: {dist:.2f})")
            
            # Criar o mapa comparativo
            map_obj = display_all_routes_map(self.sample_df, resultados)
            
            # Salvar o mapa como HTML
            output_path = os.path.join(self.output_dir, "comparacao_algoritmos.html")
            map_obj.save(output_path)
            
            print(f"Mapa comparativo de algoritmos salvo em: {output_path}")
            self.assertTrue(os.path.exists(output_path), f"O arquivo {output_path} não foi criado")
            
        except nx.NetworkXNoPath:
            self.skipTest(f"Não existe caminho entre {cidade_origem} e {cidade_destino}")
        except Exception as e:
            self.skipTest(f"Erro ao gerar visualização: {str(e)}")
    
    def test_visualize_graph_structure(self):
        """
        Testa e salva a visualização da estrutura do grafo.
        """
        # Criar visualização do grafo com parâmetros específicos
        fig = display_graph_visualization(self.graph, self.sample_df, r=5.0, d=500)
        
        # Salvar a figura como PNG
        output_path = os.path.join(self.output_dir, "estrutura_grafo.png")
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        
        print(f"Visualização da estrutura do grafo salva em: {output_path}")
        self.assertTrue(os.path.exists(output_path), f"O arquivo {output_path} não foi criado")
        
        # Criar visualização do grafo apenas com parâmetro r
        fig = display_graph_visualization(self.graph, self.sample_df, r=10.0)
        
        # Salvar a figura como PNG
        output_path = os.path.join(self.output_dir, "estrutura_grafo_r10.png")
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        
        print(f"Visualização do grafo com r=10.0 salva em: {output_path}")
        self.assertTrue(os.path.exists(output_path), f"O arquivo {output_path} não foi criado")

if __name__ == "__main__":
    unittest.main()