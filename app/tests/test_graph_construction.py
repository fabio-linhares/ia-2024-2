import sys
import os
import pandas as pd
import networkx as nx
import json
import math

# Adicionar o diretório pai ao path para poder importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Importando a função correta
from utils.graph_utils import build_graph, calculate_angular_distance, calculate_haversine_distance

def load_cities_data(json_file_path):
    """Carrega os dados das cidades de um arquivo JSON."""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Filtrar apenas entradas completas (que têm latitude e longitude)
    valid_data = [city for city in data if 'latitude' in city and 'longitude' in city]
    
    # Converter para DataFrame
    df = pd.DataFrame(valid_data)
    
    # Adicionar city_id sequencial (começando em 0)
    df['city_id'] = range(len(df))
    
    return df

def validate_graph_construction(cities_df, graph, r=None, d=None):
    """
    Verifica se o grafo foi construído corretamente de acordo com os parâmetros r e d.
    
    Args:
        cities_df: DataFrame com os dados das cidades
        graph: Grafo construído pela função build_graph
        r: Raio máximo de conexão em graus (distância angular)
        d: Distância máxima em quilômetros (usando Haversine)
        
    Returns:
        Tupla (is_valid, errors) onde:
        - is_valid: booleano indicando se o grafo está correto
        - errors: lista de erros encontrados
    """
    errors = []
    
    # Primeiro verifica se todas as cidades estão no grafo
    for _, city in cities_df.iterrows():
        city_id = int(city['city_id'])
        if city_id not in graph:
            errors.append(f"Cidade {city['city']} (ID: {city_id}) não está no grafo")
    
    # Depois verifica se as arestas respeitam as restrições
    for i, city1 in cities_df.iterrows():
        for j, city2 in cities_df.iterrows():
            if i < j:  # Evita verificar a mesma aresta duas vezes
                city1_id = int(city1['city_id'])
                city2_id = int(city2['city_id'])
                city1_name = city1['city']
                city2_name = city2['city']
                
                angular_dist = calculate_angular_distance(city1, city2)
                km_dist = calculate_haversine_distance(city1, city2)
                
                should_connect = True
                # Verificar condições de conexão
                if r is not None and angular_dist > r:
                    should_connect = False
                if d is not None and km_dist > d:
                    should_connect = False
                
                has_edge = graph.has_edge(city1_id, city2_id)
                
                # Verificar se há inconsistência
                if should_connect and not has_edge:
                    errors.append(f"Falta aresta entre {city1_name} (ID: {city1_id}) e {city2_name} (ID: {city2_id}): "
                                 f"angular={angular_dist:.4f}° km={km_dist:.2f}km")
                elif not should_connect and has_edge:
                    errors.append(f"Aresta inválida entre {city1_name} (ID: {city1_id}) e {city2_name} (ID: {city2_id}): "
                                 f"angular={angular_dist:.4f}° km={km_dist:.2f}km")
    
    # Verificar atributos das arestas
    for u, v, data in graph.edges(data=True):
        if 'angular_dist' not in data or 'km_dist' not in data:
            errors.append(f"Aresta ({u}, {v}) não tem atributos de distância")
        
        # Verificar se o peso está correto
        elif d is not None and abs(data['weight'] - data['km_dist']) > 0.001:
            errors.append(f"Peso incorreto na aresta ({u}, {v}): {data['weight']} != {data['km_dist']}")
        elif d is None and r is not None and abs(data['weight'] - data['angular_dist']) > 0.001:
            errors.append(f"Peso incorreto na aresta ({u}, {v}): {data['weight']} != {data['angular_dist']}")
    
    is_valid = len(errors) == 0
    return is_valid, errors

def analyze_graph_connections(graph, cities_df, r=None, d=None):
    """
    Analisa as conexões do grafo e fornece estatísticas.
    
    Args:
        graph: Grafo construído
        cities_df: DataFrame com dados das cidades
        r: Raio usado (opcional)
        d: Distância usada (opcional)
    """
    # Criar um mapeamento de ID para nome da cidade para exibição
    id_to_name = {int(row['city_id']): row['city'] for _, row in cities_df.iterrows()}
    
    # Obter grau médio (número médio de conexões por cidade)
    avg_degree = sum(dict(graph.degree()).values()) / graph.number_of_nodes()
    
    # Calcular densidade do grafo (fração de arestas possíveis que existem)
    density = nx.density(graph)
    
    # Verificar componentes conectados
    connected_components = list(nx.connected_components(graph))
    
    # Verificar se há cidades isoladas
    isolated_nodes = list(nx.isolates(graph))
    
    print(f"\nAnálise do grafo:")
    print(f"- Número de nós: {graph.number_of_nodes()}")
    print(f"- Número de arestas: {graph.number_of_edges()}")
    print(f"- Grau médio: {avg_degree:.2f}")
    print(f"- Densidade: {density:.4f}")
    print(f"- Componentes conectados: {len(connected_components)}")
    print(f"- Cidades isoladas: {len(isolated_nodes)}")
    
    if len(isolated_nodes) > 0:
        # Mostrar algumas cidades isoladas como exemplo
        sample_isolated = isolated_nodes[:3]
        sample_names = [f"{id_to_name[node]} (ID: {node})" for node in sample_isolated]
        print(f"  Exemplos de cidades isoladas: {', '.join(sample_names)}")
    
    if r is not None:
        print(f"- Raio (r): {r}°")
    if d is not None:
        print(f"- Distância (d): {d}km")
    
    # Verificar consistência das distâncias das arestas
    if graph.number_of_edges() > 0:
        edge_angular_dists = [data['angular_dist'] for _, _, data in graph.edges(data=True)]
        edge_km_dists = [data['km_dist'] for _, _, data in graph.edges(data=True)]
        
        print(f"\nEstatísticas das arestas:")
        print(f"- Distância angular média: {sum(edge_angular_dists)/len(edge_angular_dists):.4f}°")
        print(f"- Distância angular máxima: {max(edge_angular_dists):.4f}°")
        print(f"- Distância em km média: {sum(edge_km_dists)/len(edge_km_dists):.2f}km")
        print(f"- Distância em km máxima: {max(edge_km_dists):.2f}km")
        
        if r is not None:
            over_r = [d for d in edge_angular_dists if d > r]
            if over_r:
                print(f"ERRO: {len(over_r)} arestas têm distância angular > {r}°")
            
        if d is not None:
            over_d = [dist for dist in edge_km_dists if dist > d]
            if over_d:
                print(f"ERRO: {len(over_d)} arestas têm distância em km > {d}km")

def test_with_sample(cities_df, sample_size=10):
    """
    Testa a construção do grafo com uma amostra pequena para análise detalhada.
    """
    # Criar amostra
    sample_df = cities_df.sample(sample_size, random_state=42)
    
    # Garantir que a coluna city_id está presente e é um inteiro
    if 'city_id' not in sample_df.columns:
        sample_df['city_id'] = range(len(sample_df))
    else:
        sample_df['city_id'] = sample_df['city_id'].astype(int)
    
    print(f"\nTeste com amostra de {sample_size} cidades:")
    
    # Para cada par de cidades na amostra, calcular as distâncias
    for i, city1 in sample_df.iterrows():
        for j, city2 in sample_df.iterrows():
            if i < j:
                angular_dist = calculate_angular_distance(city1, city2)
                km_dist = calculate_haversine_distance(city1, city2)
                print(f"{city1['city']} (ID: {city1['city_id']}) <-> {city2['city']} (ID: {city2['city_id']}): angular={angular_dist:.4f}° km={km_dist:.2f}km")
            
    # Testar com diferentes raios/distâncias
    r_values = [0.5, 1.0, 2.0]
    d_values = [50, 100, 200]
    
    for r in r_values:
        G = build_graph(sample_df, r=r)
        valid, errors = validate_graph_construction(sample_df, G, r=r)
        print(f"\nGrafo com r={r}°: {'Válido' if valid else 'Inválido'}")
        print(f"- Arestas: {G.number_of_edges()}")
        if not valid:
            print(f"- Primeiros 3 erros de {len(errors)}:")
            for error in errors[:3]:
                print(f"  * {error}")
    
    for d in d_values:
        G = build_graph(sample_df, d=d)
        valid, errors = validate_graph_construction(sample_df, G, d=d)
        print(f"\nGrafo com d={d}km: {'Válido' if valid else 'Inválido'}")
        print(f"- Arestas: {G.number_of_edges()}")
        if not valid:
            print(f"- Primeiros 3 erros de {len(errors)}:")
            for error in errors[:3]:
                print(f"  * {error}")

def test_graph_construction(cities_df):
    """
    Testa a construção do grafo com diferentes parâmetros e imprime os resultados.
    
    Args:
        cities_df: DataFrame com os dados das cidades
    """
    # Teste 1: Construir grafo apenas com raio r
    r = 1.0  # Um valor pequeno para ter poucas conexões
    print(f"\nTeste 1: Grafo com raio r={r}°")
    G1 = build_graph(cities_df, r=r)
    valid1, errors1 = validate_graph_construction(cities_df, G1, r=r)
    print(f"Grafo válido: {valid1}")
    print(f"Número de nós: {G1.number_of_nodes()}")
    print(f"Número de arestas: {G1.number_of_edges()}")
    if not valid1:
        print(f"Erros encontrados: {len(errors1)}")
        for error in errors1[:5]:  # Mostrar apenas os 5 primeiros erros
            print(f"- {error}")
    
    # Teste 2: Construir grafo apenas com distância d
    d = 100  # 100 km
    print(f"\nTeste 2: Grafo com distância d={d}km")
    G2 = build_graph(cities_df, d=d)
    valid2, errors2 = validate_graph_construction(cities_df, G2, d=d)
    print(f"Grafo válido: {valid2}")
    print(f"Número de nós: {G2.number_of_nodes()}")
    print(f"Número de arestas: {G2.number_of_edges()}")
    if not valid2:
        print(f"Erros encontrados: {len(errors2)}")
        for error in errors2[:5]:
            print(f"- {error}")
    
    # Teste 3: Construir grafo com ambos os parâmetros
    r, d = 1.0, 100
    print(f"\nTeste 3: Grafo com raio r={r}° e distância d={d}km")
    G3 = build_graph(cities_df, r=r, d=d)
    valid3, errors3 = validate_graph_construction(cities_df, G3, r=r, d=d)
    print(f"Grafo válido: {valid3}")
    print(f"Número de nós: {G3.number_of_nodes()}")
    print(f"Número de arestas: {G3.number_of_edges()}")
    if not valid3:
        print(f"Erros encontrados: {len(errors3)}")
        for error in errors3[:5]:
            print(f"- {error}")
    
    # Análise das estatísticas dos grafos
    analyze_graph_connections(G1, cities_df, r=r)
    analyze_graph_connections(G2, cities_df, d=d)
    analyze_graph_connections(G3, cities_df, r=r, d=d)

def main():
    # Carregar dados das cidades
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cities.json'))
    cities_df = load_cities_data(file_path)
    print(f"Dados carregados: {len(cities_df)} cidades")
    
    # Executar os testes com uma amostra menor para análise detalhada
    test_with_sample(cities_df, sample_size=5)
    
    # Executar os testes completos
    test_graph_construction(cities_df)

if __name__ == "__main__":
    main()