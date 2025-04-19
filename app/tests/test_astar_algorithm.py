import sys
import os
import unittest
import pandas as pd
import networkx as nx
import time

# Adiciona o diretório raiz do projeto ao caminho do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(project_root)

# Importa as funções necessárias
from app.utils.data_loader import load_data
from app.utils.graph_utils import build_graph, verify_graph_constraints
from app.utils.algorithms import a_star_search

class TestAStarAlgorithm(unittest.TestCase):
    """
    Classe de teste para verificar o funcionamento do algoritmo A* (A-Star)
    utilizando um grafo construído a partir de dados de cidades.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        Carrega o conjunto de dados de teste e prepara o ambiente.
        """
        # Caminho para o arquivo de teste
        test_cities_path = os.path.join(project_root, 'data', 'test_cities.json')
        
        # Carrega os dados - load_data retorna (df, name_to_id, id_to_name)
        result = load_data(test_cities_path)
        
        # Desempacotar a tupla retornada pela função load_data
        if isinstance(result, tuple) and len(result) == 3:
            self.df, self.name_to_id, self.id_to_name = result
        else:
            # Se por algum motivo não for uma tupla de 3 elementos, usar o resultado diretamente
            self.df = result
            self.name_to_id = {}
            self.id_to_name = {}
        
        # Garantir que temos um DataFrame válido
        if not isinstance(self.df, pd.DataFrame):
            raise TypeError(f"self.df não é um DataFrame. Tipo atual: {type(self.df)}")
        
        # Imprime informações básicas sobre o dataset carregado
        print(f"Dataset carregado: {len(self.df)} cidades")
        print(f"Colunas disponíveis: {', '.join(self.df.columns.tolist())}")
        
        # Construir grafos com diferentes parâmetros para os testes
        # Usar valores grandes para garantir que as cidades estejam conectadas
        self.graph_r = build_graph(self.df, r=20.0, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        self.graph_d = build_graph(self.df, d=3000, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        
        # Verificar se o grafo tem conexões suficientes
        print(f"Grafo r=20.0 tem {self.graph_r.number_of_edges()} arestas")
        print(f"Grafo d=3000km tem {self.graph_d.number_of_edges()} arestas")
        
        # Extrair cidades para usar nos testes (primeiro verificamos se estão conectadas)
        found_connected_cities = False
        
        if len(self.df) >= 2:
            # Tentar várias combinações de cidades até encontrar um par conectado
            for i in range(len(self.df)):
                for j in range(i+1, len(self.df)):
                    city1_id = int(self.df.iloc[i]['city_id'])
                    city2_id = int(self.df.iloc[j]['city_id'])
                    
                    # Verificar se existe caminho entre as cidades no grafo
                    if nx.has_path(self.graph_r, city1_id, city2_id):
                        self.city1_id = city1_id
                        self.city2_id = city2_id
                        self.city1_name = self.df.iloc[i]['city']
                        self.city2_name = self.df.iloc[j]['city']
                        found_connected_cities = True
                        print(f"Usando cidades conectadas: {self.city1_name} -> {self.city2_name}")
                        break
                
                if found_connected_cities:
                    break
                    
            # Se não encontramos cidades conectadas, usamos as primeiras duas de qualquer forma
            if not found_connected_cities:
                self.city1_id = int(self.df.iloc[0]['city_id'])
                self.city2_id = int(self.df.iloc[1]['city_id'])
                self.city1_name = self.df.iloc[0]['city']
                self.city2_name = self.df.iloc[1]['city']
                print(f"AVISO: Não foi possível encontrar cidades conectadas. Usando {self.city1_name} e {self.city2_name}")
        else:
            raise ValueError("O dataset precisa ter pelo menos 2 cidades para os testes")
    
    def test_a_star_basic_functionality(self):
        """
        Testa a funcionalidade básica do algoritmo A*.
        Verifica se ele encontra um caminho entre duas cidades.
        """
        # Primeiro, verifica se as cidades escolhidas estão no grafo
        self.assertIn(self.city1_id, self.graph_r, f"Cidade origem (ID: {self.city1_id}) não está no grafo")
        self.assertIn(self.city2_id, self.graph_r, f"Cidade destino (ID: {self.city2_id}) não está no grafo")
        
        # Verifica se há um caminho entre as cidades no grafo
        has_path = nx.has_path(self.graph_r, self.city1_id, self.city2_id)
        
        if has_path:
            # Executa o algoritmo A*
            path, total_dist, elapsed_time = a_star_search(
                self.graph_r, 
                self.df, 
                self.city1_id, 
                self.city2_id,
                verbose=True
            )
            
            # Verifica se o caminho foi encontrado
            self.assertIsNotNone(path, "A* não encontrou um caminho válido entre as cidades")
            self.assertGreater(len(path), 0, "O caminho retornado está vazio")
            
            # Verifica se o caminho começa na origem e termina no destino
            self.assertEqual(path[0], self.city1_id, "O caminho não começa na cidade de origem")
            self.assertEqual(path[-1], self.city2_id, "O caminho não termina na cidade de destino")
            
            # Verifica se a distância total é válida
            self.assertIsInstance(total_dist, (int, float), "A distância total não é um número")
            self.assertGreater(total_dist, 0, "A distância total deve ser maior que zero")
            
            # Verifica se o tempo de execução é razoável
            self.assertIsInstance(elapsed_time, (int, float), "O tempo de execução não é um número")
            self.assertGreater(elapsed_time, 0, "O tempo de execução deve ser maior que zero")
            
            # Exibe informações sobre o caminho encontrado
            city_names = [self.id_to_name.get(city_id, f"ID {city_id}") for city_id in path]
            print(f"\nCaminho A* encontrado: {' -> '.join(city_names)}")
            print(f"Distância total: {total_dist:.2f}")
            print(f"Tempo de execução: {elapsed_time:.4f} ms")
        else:
            # Se não houver caminho, o teste é ignorado
            print(f"Não existe caminho entre {self.city1_name} e {self.city2_name} no grafo. Teste ignorado.")
            self.skipTest("Não existe caminho entre as cidades selecionadas no grafo")
    
    def test_a_star_optimality(self):
        """
        Testa a otimalidade do algoritmo A*.
        Compara o caminho encontrado pelo A* com o caminho mais curto do NetworkX.
        """
        # Verifica se há um caminho entre as cidades no grafo
        has_path = nx.has_path(self.graph_d, self.city1_id, self.city2_id)
        
        if has_path:
            # Executa o algoritmo A*
            path_astar, total_dist_astar, _ = a_star_search(
                self.graph_d, 
                self.df, 
                self.city1_id, 
                self.city2_id
            )
            
            # Encontra o caminho mais curto usando o algoritmo do NetworkX
            path_nx = nx.shortest_path(self.graph_d, self.city1_id, self.city2_id, weight='weight')
            total_dist_nx = nx.shortest_path_length(self.graph_d, self.city1_id, self.city2_id, weight='weight')
            
            # Verifica se as distâncias totais são iguais (ou quase iguais, considerando precisão numérica)
            self.assertAlmostEqual(
                total_dist_astar, 
                total_dist_nx, 
                delta=0.001, 
                msg="A distância do caminho A* não é igual à distância do caminho mais curto"
            )
            
            # Exibe informações para comparação
            print(f"\nComparação de caminhos:")
            print(f"Caminho A*: {path_astar} (Distância: {total_dist_astar:.4f})")
            print(f"Caminho NetworkX: {path_nx} (Distância: {total_dist_nx:.4f})")
        else:
            # Se não houver caminho, o teste é ignorado
            print(f"Não existe caminho entre {self.city1_name} e {self.city2_name} no grafo. Teste ignorado.")
            self.skipTest("Não existe caminho entre as cidades selecionadas no grafo")
    
    def test_a_star_performance(self):
        """
        Testa o desempenho do algoritmo A* em comparação com o algoritmo de caminho mais curto do NetworkX.
        """
        # Verifica se há um caminho entre as cidades no grafo
        has_path = nx.has_path(self.graph_r, self.city1_id, self.city2_id)
        
        if has_path:
            # Mede o tempo do algoritmo A*
            start_time = time.perf_counter()
            path_astar, total_dist_astar, elapsed_time_astar = a_star_search(
                self.graph_r, 
                self.df, 
                self.city1_id, 
                self.city2_id
            )
            
            # Mede o tempo do algoritmo do NetworkX
            start_time_nx = time.perf_counter()
            path_nx = nx.shortest_path(self.graph_r, self.city1_id, self.city2_id, weight='weight')
            elapsed_time_nx = (time.perf_counter() - start_time_nx) * 1000  # converte para ms
            
            # Exibe informações sobre o desempenho
            print(f"\nDesempenho:")
            print(f"Tempo A*: {elapsed_time_astar:.4f} ms")
            print(f"Tempo NetworkX: {elapsed_time_nx:.4f} ms")
            print(f"Razão A*/NetworkX: {elapsed_time_astar/elapsed_time_nx:.2f}x")
            
            # Não verificamos se A* é mais rápido, apenas medimos e relatamos
            # Em grafos pequenos, a sobrecarga da implementação pode tornar A* mais lento
        else:
            # Se não houver caminho, o teste é ignorado
            print(f"Não existe caminho entre {self.city1_name} e {self.city2_name} no grafo. Teste ignorado.")
            self.skipTest("Não existe caminho entre as cidades selecionadas no grafo")
    
    def test_a_star_no_path(self):
        """
        Testa o comportamento do algoritmo A* quando não existe caminho entre as cidades.
        """
        # Constrói um grafo com restrições muito pequenas, onde provavelmente não há conexão
        graph_isolated = build_graph(self.df, r=0.1, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        
        # Verifica se existe caminho no grafo com restrições rigorosas
        has_path = nx.has_path(graph_isolated, self.city1_id, self.city2_id)
        
        if not has_path:
            # Executa o algoritmo A* em um grafo sem caminho
            path, total_dist, elapsed_time = a_star_search(
                graph_isolated, 
                self.df, 
                self.city1_id, 
                self.city2_id
            )
            
            # Verifica se o algoritmo retorna None para o caminho
            self.assertIsNone(path, "A* deveria retornar None quando não existe caminho")
            
            # Verifica se a distância total é infinita
            self.assertEqual(total_dist, float('inf'), "A distância total deveria ser infinita quando não existe caminho")
            
            # Verifica se o tempo de execução é válido
            self.assertIsInstance(elapsed_time, (int, float), "O tempo de execução não é um número")
            self.assertGreater(elapsed_time, 0, "O tempo de execução deve ser maior que zero")
            
            print(f"\nTeste sem caminho concluído com sucesso. A* retornou corretamente None.")
        else:
            # Se existir um caminho mesmo com restrições rigorosas, tentamos com restrições ainda mais rigorosas
            # ou pulamos o teste se não for possível criar um grafo sem caminho
            print(f"Ainda existe caminho mesmo com restrições rigorosas. Tentando restrições mais rigorosas.")
            
            # Tenta criar um grafo ainda mais restrito
            graph_very_isolated = build_graph(self.df, r=0.01, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
            has_path_very = nx.has_path(graph_very_isolated, self.city1_id, self.city2_id)
            
            if not has_path_very:
                # Executa o algoritmo A* no grafo muito restrito
                path, total_dist, elapsed_time = a_star_search(
                    graph_very_isolated, 
                    self.df, 
                    self.city1_id, 
                    self.city2_id
                )
                
                # Verifica os resultados
                self.assertIsNone(path, "A* deveria retornar None quando não existe caminho")
                self.assertEqual(total_dist, float('inf'), "A distância total deveria ser infinita quando não existe caminho")
            else:
                # Se mesmo com restrições ainda mais rigorosas houver caminho, pulamos o teste
                print(f"Não foi possível criar um grafo sem caminho entre as cidades. Teste ignorado.")
                self.skipTest("Não foi possível criar um grafo sem caminho entre as cidades para testar")

if __name__ == "__main__":
    unittest.main()