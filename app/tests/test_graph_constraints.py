import sys
import os
import unittest
import pandas as pd
import networkx as nx

# Adiciona o diretório raiz do projeto ao caminho do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(project_root)

# Importa as funções necessárias
from app.utils.data_loader import load_data
from app.utils.graph_utils import build_graph, verify_graph_constraints

class TestGraphConstraints(unittest.TestCase):
    """
    Classe de teste para verificar se o grafo construído respeita 
    as restrições de raio (r) ou distância (d) especificadas.
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
        
        # Cria um subconjunto para testes mais rápidos
        self.sample_df = self.df.head(50) if len(self.df) > 50 else self.df
        
        # Verificar se o sample_df é um DataFrame válido
        if not isinstance(self.sample_df, pd.DataFrame):
            raise TypeError(f"self.sample_df não é um DataFrame. Tipo atual: {type(self.sample_df)}")
        
        # Adicionar alguns logs para debug
        print(f"Tipo do self.df: {type(self.df)}")
        print(f"Tipo do self.sample_df: {type(self.sample_df)}")
        print(f"Número de cidades no sample_df: {len(self.sample_df)}")
        if len(self.sample_df) > 0:
            print(f"Colunas disponíveis: {', '.join(self.sample_df.columns.tolist())}")
    
    def test_radius_constraint(self):
        """
        Testa se o grafo construído com restrição de raio (r) 
        mantém todas as arestas dentro do limite especificado.
        """
        # Valores de raio para teste
        test_radii = [0.5, 1.0, 2.0]
        
        for r in test_radii:
            # Constrói o grafo com restrição de raio
            G = build_graph(self.sample_df, r=r, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
            
            # Verifica as restrições
            result = verify_graph_constraints(G)
            
            # Testes
            self.assertTrue(result['is_valid'], 
                           f"O grafo com raio r={r} contém arestas que violam a restrição")
            
            # Verifica se todas as arestas estão dentro do limite de raio
            for _, _, edge_data in G.edges(data=True):
                self.assertLessEqual(edge_data.get('angular_dist'), r,
                                   f"Uma aresta tem distância angular {edge_data.get('angular_dist')} que excede o raio {r}")
            
            # Verifica estatísticas
            if G.number_of_edges() > 0:
                self.assertLessEqual(result['stats']['max_angular_dist'], r,
                                   f"A maior distância angular {result['stats']['max_angular_dist']} excede o raio {r}")
    
    def test_distance_constraint(self):
        """
        Testa se o grafo construído com restrição de distância (d) 
        mantém todas as arestas dentro do limite especificado.
        """
        # Valores de distância para teste (em km)
        test_distances = [50, 100, 200]
        
        for d in test_distances:
            # Constrói o grafo com restrição de distância
            G = build_graph(self.sample_df, d=d, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
            
            # Verifica as restrições
            result = verify_graph_constraints(G)
            
            # Testes
            self.assertTrue(result['is_valid'], 
                           f"O grafo com distância d={d}km contém arestas que violam a restrição")
            
            # Verifica se todas as arestas estão dentro do limite de distância
            for _, _, edge_data in G.edges(data=True):
                self.assertLessEqual(edge_data.get('km_dist'), d,
                                   f"Uma aresta tem distância {edge_data.get('km_dist')}km que excede o limite {d}km")
            
            # Verifica estatísticas
            if G.number_of_edges() > 0:
                self.assertLessEqual(result['stats']['max_km_dist'], d,
                                   f"A maior distância {result['stats']['max_km_dist']}km excede o limite {d}km")
    
    def test_both_constraints(self):
        """
        Testa se o grafo construído com ambas as restrições (r e d)
        mantém todas as arestas dentro dos limites especificados.
        """
        # Valores para teste
        r = 1.0  # raio em graus
        d = 100  # distância em km
        
        # Constrói o grafo com ambas as restrições
        G = build_graph(self.sample_df, r=r, d=d, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        
        # Verifica as restrições
        result = verify_graph_constraints(G)
        
        # Testes
        self.assertTrue(result['is_valid'], 
                       f"O grafo com r={r} e d={d}km contém arestas que violam as restrições")
        
        # Verifica se todas as arestas estão dentro dos limites
        for _, _, edge_data in G.edges(data=True):
            self.assertLessEqual(edge_data.get('angular_dist'), r,
                               f"Uma aresta tem distância angular {edge_data.get('angular_dist')} que excede o raio {r}")
            self.assertLessEqual(edge_data.get('km_dist'), d,
                               f"Uma aresta tem distância {edge_data.get('km_dist')}km que excede o limite {d}km")

    def test_graph_info(self):
        """
        Testa se as informações sobre as restrições são corretamente 
        armazenadas no grafo construído.
        """
        # Valores para teste
        r = 1.5
        d = 150
        
        # Constrói grafos com diferentes configurações
        G1 = build_graph(self.sample_df, r=r, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        G2 = build_graph(self.sample_df, d=d, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        G3 = build_graph(self.sample_df, r=r, d=d, name_to_id=self.name_to_id, id_to_name=self.id_to_name)
        
        # Verifica se as restrições estão armazenadas corretamente
        self.assertEqual(G1.graph['r'], r, "O valor de r não foi armazenado corretamente no grafo")
        self.assertIsNone(G1.graph['d'], "O valor de d deveria ser None")
        
        self.assertEqual(G2.graph['d'], d, "O valor de d não foi armazenado corretamente no grafo")
        self.assertIsNone(G2.graph['r'], "O valor de r deveria ser None")
        
        self.assertEqual(G3.graph['r'], r, "O valor de r não foi armazenado corretamente no grafo")
        self.assertEqual(G3.graph['d'], d, "O valor de d não foi armazenado corretamente no grafo")

if __name__ == "__main__":
    unittest.main()