import sys
import os
import unittest
import pandas as pd
import networkx as nx
import folium
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz do projeto ao caminho do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(project_root)

# Importa as funções necessárias
from app.utils.data_loader import load_data
from app.utils.graph_utils import build_graph
from app.components.map_display import (
    display_route_map, 
    display_all_routes_map, 
    display_path_on_map, 
    display_graph_visualization
)

class TestMapDisplay(unittest.TestCase):
    """
    Classe de teste para verificar o funcionamento das funções de exibição de mapas.
    Estas funções são responsáveis por renderizar as rotas entre cidades e visualizações do grafo.
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
        
        # Garantir que temos um DataFrame válido
        if not isinstance(cls.df, pd.DataFrame):
            raise TypeError(f"cls.df não é um DataFrame. Tipo atual: {type(cls.df)}")
        
        # Criar um subconjunto para testes mais rápidos se necessário
        cls.sample_df = cls.df.head(10) if len(cls.df) > 10 else cls.df
        
        # Construir um grafo para testes
        cls.graph = build_graph(cls.sample_df, r=20.0, name_to_id=cls.name_to_id, id_to_name=cls.id_to_name)
        
        # Criar alguns caminhos de teste (usando nomes de cidades)
        # Garantir que os nomes das cidades existem no DataFrame
        available_cities = cls.sample_df['city'].tolist()
        
        if len(available_cities) >= 3:
            cls.path1 = [available_cities[0], available_cities[1], available_cities[2]]
            cls.path2 = [available_cities[0], available_cities[2]]
        else:
            # Fallback para caso não haja cidades suficientes
            cls.path1 = ["New York", "Chicago", "Los Angeles"]
            cls.path2 = ["New York", "Los Angeles"]
        
        # Dicionário simulando resultados de algoritmos
        cls.results = {
            'BFS': ([cls.path1[0], cls.path1[1], cls.path1[2]], 300, 10),
            'A*': ([cls.path2[0], cls.path2[1]], 250, 5),
            'Dijkstra': ([cls.path1[0], cls.path1[2]], 280, 7)
        }
        
        # Mostrar informações sobre o ambiente de teste
        print(f"Ambiente de teste configurado com {len(cls.sample_df)} cidades")
        print(f"Grafo criado com {cls.graph.number_of_nodes()} nós e {cls.graph.number_of_edges()} arestas")
        
    # Patch para simular o comportamento do Streamlit
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit_folium.folium_static')
    def test_display_route_map(self, mock_folium_static, mock_warning, mock_error):
        """
        Testa a função display_route_map que exibe um mapa com múltiplas rotas.
        Verifica se a função retorna um objeto de mapa válido e não gera erros.
        """
        # Caso 1: Teste com um único caminho válido
        paths = [self.path1]
        map_obj = display_route_map(self.sample_df, paths)
        
        # Verificar se a função retornou um objeto de mapa válido
        self.assertIsInstance(map_obj, folium.Map, "A função deve retornar um objeto de mapa Folium")
        
        # Verificar se folium_static NÃO foi chamado no ambiente de teste
        mock_folium_static.assert_not_called()
        
        # Verificar elementos básicos do mapa
        self.assertGreaterEqual(len(map_obj._children), 4, "O mapa deve conter elementos básicos")
        
        # Caso 2: Teste com múltiplos caminhos
        mock_folium_static.reset_mock()
        paths = [self.path1, self.path2]
        map_obj = display_route_map(self.sample_df, paths)
        
        self.assertIsInstance(map_obj, folium.Map, "A função deve retornar um objeto de mapa Folium mesmo com múltiplos caminhos")
        mock_folium_static.assert_not_called()
        
        # Caso 3: Teste com caminho vazio
        mock_folium_static.reset_mock()
        paths = []
        map_obj = display_route_map(self.sample_df, paths)
        
        self.assertIsInstance(map_obj, folium.Map, "A função deve retornar um objeto de mapa Folium mesmo com caminho vazio")
        mock_folium_static.assert_not_called()
        self.assertFalse(mock_error.called, "Não deve ocorrer erro com caminho vazio")
        
        # Caso 4: Teste com DataFrame sem coordenadas
        mock_folium_static.reset_mock()
        mock_error.reset_mock()
        
        df_sem_coords = self.sample_df.drop(['latitude', 'longitude'], axis=1)
        map_obj = display_route_map(df_sem_coords, [self.path1])
        
        self.assertIsNone(map_obj, "Deve retornar None quando não há coordenadas")
        mock_error.assert_called()  # Deve chamar st.error()
        self.assertFalse(mock_folium_static.called, "Não deve renderizar mapa sem coordenadas")

    @patch('streamlit.error')
    @patch('streamlit_folium.folium_static')
    def test_display_all_routes_map(self, mock_folium_static, mock_error):
        """
        Testa a função display_all_routes_map que exibe um mapa comparativo 
        com rotas de diferentes algoritmos.
        """
        # Caso 1: Teste com resultados de múltiplos algoritmos
        map_obj = display_all_routes_map(self.sample_df, self.results)
        
        self.assertIsInstance(map_obj, folium.Map, "A função deve retornar um objeto de mapa Folium")
        mock_folium_static.assert_not_called()  # Não deve ser chamado em modo de teste
        
        # Verificar elementos básicos do mapa
        self.assertGreaterEqual(len(map_obj._children), 4, "O mapa deve conter elementos básicos")
        
        # Caso 2: Teste com resultados vazios
        mock_folium_static.reset_mock()
        map_obj = display_all_routes_map(self.sample_df, {})
        
        self.assertIsInstance(map_obj, folium.Map, "A função deve retornar um objeto de mapa Folium mesmo com resultados vazios")
        mock_folium_static.assert_not_called()  # Não deve ser chamado em modo de teste
        
        # Caso 3: Teste com DataFrame sem coordenadas
        mock_folium_static.reset_mock()
        mock_error.reset_mock()
        
        df_sem_coords = self.sample_df.drop(['latitude', 'longitude'], axis=1)
        map_obj = display_all_routes_map(df_sem_coords, self.results)
        
        self.assertIsNone(map_obj, "Deve retornar None quando não há coordenadas")
        mock_error.assert_called()  # Deve chamar st.error()
        mock_folium_static.assert_not_called()  # Não deve renderizar mapa sem coordenadas

    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit_folium.folium_static')
    def test_display_path_on_map(self, mock_folium_static, mock_warning, mock_error):
        """
        Testa a função display_path_on_map que exibe um mapa com um único caminho.
        """
        # Caso 1: Teste com um caminho válido
        custom_title = "Teste de Caminho"
        map_obj = display_path_on_map(self.sample_df, self.path1, title=custom_title)
        
        # Verificações básicas
        self.assertIsInstance(map_obj, folium.Map, "A função deve retornar um objeto de mapa Folium")
        mock_folium_static.assert_not_called()  # Não deve ser chamado em modo de teste
        
        # Verificar se existem elementos HTML no mapa (não verificamos o conteúdo específico)
        html_elements = [child for child in map_obj._children.values() 
                        if isinstance(child, folium.Element)]
        self.assertGreater(len(html_elements), 0, "O mapa deve conter elementos HTML")
        
        # Verificar se existem marcadores para cada cidade no caminho
        markers_count = 0
        for child in map_obj._children.values():
            if isinstance(child, folium.map.Marker):
                markers_count += 1
        
        # Deve haver pelo menos um marcador para cada cidade no caminho
        self.assertGreaterEqual(markers_count, len(self.path1), 
                               f"O mapa deve conter pelo menos {len(self.path1)} marcadores (um para cada cidade)")
        
        # Caso 2: Teste com caminho vazio
        mock_folium_static.reset_mock()
        map_obj = display_path_on_map(self.sample_df, [], "Caminho Vazio")
        
        self.assertIsInstance(map_obj, folium.Map, "A função deve retornar um objeto de mapa Folium mesmo com caminho vazio")
        mock_folium_static.assert_not_called()
        
        # Caso 3: Teste com DataFrame sem coordenadas
        mock_folium_static.reset_mock()
        mock_error.reset_mock()
        
        df_sem_coords = self.sample_df.drop(['latitude', 'longitude'], axis=1)
        map_obj = display_path_on_map(df_sem_coords, self.path1)
        
        self.assertIsNone(map_obj, "Deve retornar None quando não há coordenadas")
        mock_error.assert_called()  # Deve chamar st.error()
        mock_folium_static.assert_not_called()  # Não deve renderizar mapa sem coordenadas

    @patch('matplotlib.pyplot.show')
    def test_display_graph_visualization(self, mock_show):
        """
        Testa a função display_graph_visualization que cria uma visualização 
        do grafo usando matplotlib.
        """
        # Caso 1: Teste com grafo válido e parâmetros r e d
        fig = display_graph_visualization(self.graph, self.sample_df, r=5.0, d=500)
        
        self.assertIsInstance(fig, plt.Figure, "A função deve retornar um objeto Figure do matplotlib")
        
        # Verificar propriedades básicas da figura
        self.assertEqual(len(fig.axes), 1, "A figura deve ter um único eixo")
        ax = fig.axes[0]
        self.assertIn("Grafo de Conexões entre Cidades", ax.get_title(), "O título deve conter 'Grafo de Conexões entre Cidades'")
        
        # Caso 2: Teste apenas com parâmetro r
        fig = display_graph_visualization(self.graph, self.sample_df, r=5.0)
        
        self.assertIsInstance(fig, plt.Figure, "A função deve retornar um objeto Figure do matplotlib")
        ax = fig.axes[0]
        self.assertIn("raio r = 5.0", ax.get_title(), "O título deve mencionar o raio")
        
        # Caso 3: Teste apenas com parâmetro d
        fig = display_graph_visualization(self.graph, self.sample_df, d=500)
        
        self.assertIsInstance(fig, plt.Figure, "A função deve retornar um objeto Figure do matplotlib")
        ax = fig.axes[0]
        self.assertIn("distância máxima = 500", ax.get_title(), "O título deve mencionar a distância máxima")
        
        # Caso 4: Teste sem parâmetros r e d
        fig = display_graph_visualization(self.graph, self.sample_df)
        
        self.assertIsInstance(fig, plt.Figure, "A função deve retornar um objeto Figure do matplotlib")
        ax = fig.axes[0]
        self.assertEqual("Grafo de Conexões entre Cidades", ax.get_title(), "O título deve ser genérico sem r e d")
    
    def test_edge_cases(self):
        """
        Testa casos extremos e situações excepcionais que podem ocorrer.
        """
        # Caso 1: Cidades no caminho que não existem no DataFrame
        with patch('streamlit.warning') as mock_warning:
            with patch('streamlit_folium.folium_static'):
                caminho_invalido = ["Cidade Inexistente 1", "Cidade Inexistente 2"]
                map_obj = display_route_map(self.sample_df, [caminho_invalido])
                
                # Deve avisar sobre cidades não encontradas
                self.assertTrue(mock_warning.called, "Deve emitir aviso para cidades não encontradas")
                
        # Caso 2: Exceção durante renderização 
        with patch('app.components.map_display.folium.Map', side_effect=Exception("Erro simulado")):
            with patch('streamlit.error') as mock_error:
                result = display_route_map(self.sample_df, [self.path1])
                
                # Deve tratar a exceção e retornar None
                self.assertIsNone(result, "Deve retornar None quando ocorre erro")
                self.assertTrue(mock_error.called, "Deve emitir erro quando ocorre exceção")

if __name__ == "__main__":
    unittest.main()