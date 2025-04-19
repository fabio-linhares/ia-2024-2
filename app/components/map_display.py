import folium
from streamlit_folium import folium_static
import streamlit as st
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import math
import networkx as nx

def display_route_map(cities_df, paths):
    """
    Exibe um mapa interativo com as rotas encontradas.
    
    Esta função cria um mapa Folium marcando todas as cidades e desenhando
    as rotas encontradas pelos algoritmos.
    
    Args:
        cities_df: DataFrame com as informações das cidades
        paths: Lista de caminhos a serem exibidos no mapa
        
    Returns:
        Objeto mapa do folium
    """
    # Verificação de dados
    if 'latitude' not in cities_df.columns or 'longitude' not in cities_df.columns:
        st.error("Dados de latitude e longitude não encontrados. Verifique o arquivo cities.json.")
        st.write("Colunas disponíveis:", cities_df.columns.tolist())
        st.write("Primeiras linhas dos dados:", cities_df.head().to_dict())
        return None
    
    try:
        # Centralizar o mapa nos Estados Unidos para melhor visualização
        center_lat = 39.8
        center_lon = -98.5
        
        # Criar mapa base
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4, control_scale=True)
        
        # Adicionar título ao mapa
        title_html = '''
             <h4 align="center" style="font-size:16px"><b>Mapa de Rotas entre Cidades</b></h4>
             <p align="center" style="font-size:12px">
                Cores das Rotas: Azul (BFS), Verde (A*), Vermelho (Fuzzy), Amarelo (Dijkstra)
             </p>
             <p align="center" style="font-size:10px; font-style: italic;">
                Nota: Linhas conectam apenas cidades consecutivas em cada rota
             </p>
             '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Usar clusters para cidades sem rotas para melhorar performance
        marker_cluster = MarkerCluster(
            name="Cidades intermediárias",
            tooltip="Clique para expandir"
        ).add_to(m)
        
        # Conjunto para acompanhar cidades que fazem parte de qualquer rota
        cities_in_routes = set()
        for path in paths:
            if path:
                cities_in_routes.update(path)
        
        # Adicionar marcadores para todas as cidades
        for index, row in cities_df.iterrows():
            city_name = row['city']
            
            # Preparar informações para exibição no popup
            popup_text = f"""
            <b>{row['city']}, {row['state']}</b><br>
            População: {int(row['population']):,}<br>
            Coordenadas: {row['latitude']:.4f}, {row['longitude']:.4f}
            """
            
            # Se a cidade faz parte de uma rota, adiciona diretamente ao mapa
            # Caso contrário, adiciona ao cluster
            if city_name in cities_in_routes:
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    tooltip=row['city'],
                    icon=folium.Icon(color='blue', icon="info-sign")
                ).add_to(m)
            else:
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    tooltip=row['city']
                ).add_to(marker_cluster)
        
        # Adicionar linhas para as rotas
        colors = ['blue', 'green', 'red', 'yellow', 'orange']
        route_names = ["Rota BFS", "Rota A*", "Rota Fuzzy", "Rota Dijkstra"]
        
        for i, path in enumerate(paths):
            if not path or len(path) < 2:  # Pular rotas vazias ou com apenas um ponto
                continue
                
            # Converter nomes das cidades em coordenadas
            route_points = []
            for city_name in path:
                city_data = cities_df[cities_df['city'] == city_name]
                if not city_data.empty:
                    route_points.append([city_data.iloc[0]['latitude'], city_data.iloc[0]['longitude']])
                else:
                    st.warning(f"Cidade não encontrada no mapa: {city_name}")
            
            if len(route_points) > 1:  # Precisamos de pelo menos 2 pontos para uma linha
                route_name = route_names[i] if i < len(route_names) else f"Rota {i+1}"
                color = colors[i % len(colors)]
                
                # Desenhar cada segmento da rota separadamente (cidade a cidade)
                for j in range(len(route_points) - 1):
                    segment = [route_points[j], route_points[j+1]]
                    segment_tooltip = f"{route_name}: {path[j]} → {path[j+1]}"
                    
                    folium.PolyLine(
                        segment,
                        weight=4,
                        color=color,
                        opacity=0.8,
                        tooltip=segment_tooltip,
                        popup=f"Segmento {j+1} da {route_name}: {path[j]} → {path[j+1]}"
                    ).add_to(m)
            else:
                st.warning(f"Pontos insuficientes para desenhar a rota {i+1}: apenas {len(route_points)} pontos encontrados")
        
        # Adicionar uma nota explicativa sobre as linhas do mapa
        map_note = folium.Element('''
            <div style="position: fixed; bottom: 20px; left: 20px; background-color: white; 
            padding: 10px; border-radius: 5px; z-index: 1000; max-width: 300px; 
            box-shadow: 0 0 5px rgba(0,0,0,0.3);">
                <p style="margin: 0; font-size: 12px;">
                    <strong>Rotas sequenciais:</strong> As linhas coloridas representam a sequência exata 
                    das rotas encontradas pelos algoritmos, conectando apenas cidades consecutivas na ordem 
                    em que são visitadas.
                </p>
            </div>
        ''')
        m.get_root().html.add_child(map_note)
        
        # Adicionar escala e controle de camadas ao mapa
        folium.LayerControl(position='topright', collapsed=False).add_to(m)
        
        # Importante: Renderizamos o mapa somente se não estivermos em modo de teste
        # Para testes, queremos apenas retornar o objeto mapa
        try:
            # Verifica se estamos em um ambiente de teste
            import inspect
            caller_module = inspect.currentframe().f_back.f_globals.get('__name__', '')
            is_test = 'test' in caller_module
            
            if not is_test:
                folium_static(m, width=800, height=600)
        except Exception:
            # Se algo der errado, apenas renderiza o mapa
            folium_static(m, width=800, height=600)
        
        return m
    except Exception as e:
        st.error(f"Erro ao criar o mapa: {str(e)}")
        return None

def display_all_routes_map(cities_df, results):
    """
    Exibe um mapa interativo com todas as rotas encontradas pelos diferentes algoritmos.
    
    Args:
        cities_df: DataFrame com as informações das cidades
        results: Dicionário com os resultados dos algoritmos
    
    Returns:
        Objeto mapa do folium
    """
    # Verificação de dados
    if 'latitude' not in cities_df.columns or 'longitude' not in cities_df.columns:
        st.error("Dados de latitude e longitude não encontrados. Verifique o arquivo cities.json.")
        return None
    
    try:
        # Centralizar o mapa nos Estados Unidos para melhor visualização
        center_lat = 39.8
        center_lon = -98.5
        
        # Criar mapa base
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4, control_scale=True)
        
        # Definir cores para cada algoritmo
        colors = {
            'BFS': 'blue',
            'DFS': 'purple',
            'A*': 'green',
            'Fuzzy': 'red',
            'Dijkstra': 'orange'
        }
        
        # Adicionar título e legenda ao mapa
        title_html = '''
             <div style="position: fixed; top: 10px; left: 50px; width: 280px; 
                 background-color: white; padding: 10px; border-radius: 5px; z-index: 1000;
                 box-shadow: 0 0 5px rgba(0,0,0,0.3);">
                 <h4 style="margin: 0; text-align: center;">Legenda - Algoritmos</h4>
                 <ul style="list-style: none; padding: 5px;">
                     <li><span style="display: inline-block; width: 14px; height: 14px; background-color: blue; margin-right: 5px;"></span>BFS (Busca em Largura)</li>
                     <li><span style="display: inline-block; width: 14px; height: 14px; background-color: purple; margin-right: 5px;"></span>DFS (Busca em Profundidade)</li>
                     <li><span style="display: inline-block; width: 14px; height: 14px; background-color: green; margin-right: 5px;"></span>A* (A-Estrela)</li>
                     <li><span style="display: inline-block; width: 14px; height: 14px; background-color: red; margin-right: 5px;"></span>Fuzzy (Busca Difusa)</li>
                     <li><span style="display: inline-block; width: 14px; height: 14px; background-color: orange; margin-right: 5px;"></span>Dijkstra (Menor Distância)</li>
                 </ul>
             </div>
             '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Conjunto para acompanhar todas as cidades que fazem parte de alguma rota
        cities_in_routes = set()
        
        # Extrair cidades das rotas
        for algo, resultado in results.items():
            path = resultado[0]  # O caminho é sempre o primeiro elemento
            if path:
                cities_in_routes.update(path)
        
        # Adicionar marcadores para cidades de origem e destino
        if results and len(next(iter(results.values()))[0]) >= 2:
            first_algo = next(iter(results.keys()))
            start_city = results[first_algo][0][0]
            end_city = results[first_algo][0][-1]
            
            # Adicionar marcador para cidade de origem
            start_data = cities_df[cities_df['city'] == start_city].iloc[0]
            folium.Marker(
                location=[start_data['latitude'], start_data['longitude']],
                popup=f"<b>Origem: {start_city}</b>",
                tooltip=f"Origem: {start_city}",
                icon=folium.Icon(color='green', icon="play", prefix='fa')
            ).add_to(m)
            
            # Adicionar marcador para cidade de destino
            end_data = cities_df[cities_df['city'] == end_city].iloc[0]
            folium.Marker(
                location=[end_data['latitude'], end_data['longitude']],
                popup=f"<b>Destino: {end_city}</b>",
                tooltip=f"Destino: {end_city}",
                icon=folium.Icon(color='red', icon="flag-checkered", prefix='fa')
            ).add_to(m)
            
            # Usar clusters para cidades intermediárias
            intermediate_cluster = MarkerCluster(
                name="Cidades intermediárias",
                tooltip="Clique para expandir"
            ).add_to(m)
            
            # Adicionar marcadores para todas as cidades intermediárias
            for city_name in cities_in_routes:
                if city_name != start_city and city_name != end_city:
                    city_data = cities_df[cities_df['city'] == city_name]
                    if not city_data.empty:
                        row = city_data.iloc[0]
                        popup_text = f"""
                        <b>{row['city']}, {row['state']}</b><br>
                        População: {int(row['population']):,}<br>
                        """
                        folium.Marker(
                            location=[row['latitude'], row['longitude']],
                            popup=popup_text,
                            tooltip=f"{row['city']}"
                        ).add_to(intermediate_cluster)
        
        # Adicionar linhas para cada rota - modificado para conectar apenas cidades consecutivas
        for algo, resultado in results.items():
            path = resultado[0]  # O caminho é sempre o primeiro elemento
            distance = resultado[1]  # A distância é sempre o segundo elemento
            
            if not path or len(path) < 2:
                continue
            
            # Coletar coordenadas de todas as cidades no caminho
            coordinates = []
            for city_name in path:
                city_data = cities_df[cities_df['city'] == city_name]
                if not city_data.empty:
                    coordinates.append([city_data.iloc[0]['latitude'], city_data.iloc[0]['longitude']])
            
            # Obter a cor para o algoritmo
            color = colors.get(algo, 'gray')  # Obter cor do algoritmo ou usar cinza como padrão
            
            # Desenhar segmentos individuais entre cidades consecutivas
            for i in range(len(coordinates) - 1):
                segment = [coordinates[i], coordinates[i+1]]
                # Adicionar informação sobre o segmento específico
                segment_tooltip = f"{algo}: {path[i]} → {path[i+1]}"
                
                folium.PolyLine(
                    segment,
                    color=color,
                    weight=4,
                    opacity=0.7,
                    tooltip=segment_tooltip,
                    popup=f"<b>Algoritmo:</b> {algo}<br><b>Segmento:</b> {path[i]} → {path[i+1]}"
                ).add_to(m)
        
        # Adicionar uma nota explicativa sobre as linhas do mapa
        map_note = folium.Element('''
            <div style="position: fixed; bottom: 20px; left: 20px; background-color: white; 
            padding: 10px; border-radius: 5px; z-index: 1000; max-width: 300px; 
            box-shadow: 0 0 5px rgba(0,0,0,0.3);">
                <p style="margin: 0; font-size: 12px;">
                    <strong>Rotas sequenciais:</strong> As linhas coloridas representam a sequência exata 
                    das rotas encontradas pelos algoritmos, conectando apenas cidades consecutivas na ordem 
                    em que são visitadas pelo algoritmo. Cada algoritmo usa uma cor diferente para sua rota.
                </p>
            </div>
        ''')
        m.get_root().html.add_child(map_note)
        
        # Adicionar controle de camadas
        folium.LayerControl(position='topright', collapsed=False).add_to(m)
        
        # Importante: Renderizamos o mapa somente se não estivermos em modo de teste
        try:
            # Verifica se estamos em um ambiente de teste
            import inspect
            caller_module = inspect.currentframe().f_back.f_globals.get('__name__', '')
            is_test = 'test' in caller_module
            
            if not is_test:
                folium_static(m, width=600, height=600)
        except Exception:
            # Se algo der errado, apenas renderiza o mapa
            folium_static(m, width=600, height=600)
        
        return m
        
    except Exception as e:
        st.error(f"Erro ao criar mapa comparativo: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def display_path_on_map(cities_df, path, title="Caminho encontrado"):
    """
    Exibe um mapa interativo com um único caminho.
    
    Esta função é uma versão simplificada da display_route_map, exibindo
    apenas um caminho específico no mapa.
    
    Args:
        cities_df: DataFrame com as informações das cidades
        path: Lista com os nomes das cidades que formam o caminho
        title: Título a ser exibido no mapa
        
    Returns:
        Objeto mapa do folium
    """
    # Verificação de dados
    if 'latitude' not in cities_df.columns or 'longitude' not in cities_df.columns:
        st.error("Dados de latitude e longitude não encontrados. Verifique o arquivo cities.json.")
        return None
    
    try:
        # Centralizar o mapa nos Estados Unidos para melhor visualização
        center_lat = 39.8
        center_lon = -98.5
        
        # Criar mapa base
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4, control_scale=True)
        
        # Adicionar título ao mapa
        title_html = f'''
             <h4 align="center" style="font-size:16px"><b>{title}</b></h4>
             <p align="center" style="font-size:12px">Cada cidade na rota é marcada com uma cor diferente</p>
             <p align="center" style="font-size:10px; font-style: italic;">Nota: As linhas conectam cidades consecutivas
             da rota encontrada pelo algoritmo.</p>
             '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Definir uma lista de cores para usar nos marcadores
        marker_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                         'lightred', 'darkblue', 'darkgreen', 'cadetblue', 
                         'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black']
        
        # Adicionar marcadores para as cidades no caminho
        for i, city_name in enumerate(path):
            city_data = cities_df[cities_df['city'] == city_name]
            if not city_data.empty:
                row = city_data.iloc[0]
                
                # Preparar informações para exibição no popup
                popup_text = f"""
                <b>{row['city']}, {row['state']}</b><br>
                População: {int(row['population']):,}<br>
                Coordenadas: {row['latitude']:.4f}, {row['longitude']:.4f}
                """
                
                # Selecionar uma cor da lista para este marcador
                color_index = i % len(marker_colors)
                icon_color = marker_colors[color_index]
                
                # Usar ícones especiais para o início e fim do percurso
                if i == 0:
                    icon_type = 'play'
                elif i == len(path) - 1:
                    icon_type = 'flag-checkered'
                else:
                    icon_type = 'map-marker'
                
                # Adicionar o número da parada ao tooltip
                tooltip_text = f"{i+1}. {row['city']}"
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    tooltip=tooltip_text,
                    icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
                ).add_to(m)
            else:
                # Se a cidade não for encontrada no DataFrame, emitir um aviso
                st.warning(f"Cidade não encontrada no DataFrame: {city_name}")
        
        # Adicionar segmentos de linha entre cidades consecutivas do caminho
        if len(path) > 1:
            coordinates = []
            valid_cities = []
            for city_name in path:
                city_data = cities_df[cities_df['city'] == city_name]
                if not city_data.empty:
                    coordinates.append([city_data.iloc[0]['latitude'], city_data.iloc[0]['longitude']])
                    valid_cities.append(city_name)
            
            # Desenhar cada segmento da rota separadamente (cidade a cidade)
            for i in range(len(coordinates) - 1):
                segment = [coordinates[i], coordinates[i+1]]
                # Adicionar informação sobre o segmento específico
                segment_tooltip = f"De {valid_cities[i]} para {valid_cities[i+1]}"
                
                folium.PolyLine(
                    segment,
                    weight=3,
                    color='blue',
                    opacity=0.7,
                    tooltip=segment_tooltip,
                    popup=f"Segmento {i+1}: {valid_cities[i]} → {valid_cities[i+1]}"
                ).add_to(m)
        
        # Adicionar uma nota explicativa sobre as linhas do mapa
        map_note = folium.Element('''
            <div style="position: fixed; bottom: 20px; left: 20px; background-color: white; 
            padding: 10px; border-radius: 5px; z-index: 1000; max-width: 300px; 
            box-shadow: 0 0 5px rgba(0,0,0,0.3);">
                <p style="margin: 0; font-size: 12px;">
                    <strong>Rota sequencial:</strong> As linhas azuis representam a sequência exata 
                    da rota encontrada pelo algoritmo, conectando cidades consecutivas na ordem em que 
                    são visitadas pelo algoritmo.
                </p>
            </div>
        ''')
        m.get_root().html.add_child(map_note)
        
        # Importante: Renderizamos o mapa somente se não estivermos em modo de teste
        try:
            # Verifica se estamos em um ambiente de teste
            import inspect
            caller_module = inspect.currentframe().f_back.f_globals.get('__name__', '')
            is_test = 'test' in caller_module
            
            if not is_test:
                folium_static(m, width=800, height=600)
        except Exception:
            # Se algo der errado, apenas renderiza o mapa
            folium_static(m, width=800, height=600)
        
        return m
        
    except Exception as e:
        st.error(f"Erro ao criar o mapa: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def display_graph_visualization(G, cities_df, r=None, d=None):
    """
    Visualiza o grafo de conexões entre cidades.
    
    Args:
        G: Grafo NetworkX das conexões entre cidades
        cities_df: DataFrame com as informações das cidades
        r: Raio de conexão em graus (opcional)
        d: Distância máxima em km (opcional)
        
    Returns:
        Objeto figura do matplotlib com a visualização do grafo
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Determinar o título baseado nos parâmetros fornecidos
    if r is not None and d is not None:
        title = f"Grafo de Conexões entre Cidades (r = {r} graus, d = {d} km)"
    elif r is not None:
        title = f"Grafo de Conexões entre Cidades (raio r = {r} graus)"
    elif d is not None:
        title = f"Grafo de Conexões entre Cidades (distância máxima = {d} km)"
    else:
        title = "Grafo de Conexões entre Cidades"
        
    plt.title(title)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    
    # Posições dos nós baseadas em coordenadas geográficas
    pos = {}
    labels = {}
    
    # Mapear IDs para nomes para visualização
    id_to_name = getattr(G.graph, 'id_to_name', {})
    
    for node_id in G.nodes():
        # Obter dados do nó direto do grafo
        node_attrs = G.nodes[node_id]
        pos[node_id] = (node_attrs['longitude'], node_attrs['latitude'])
        
        # Usar o nome da cidade como rótulo para visualização
        labels[node_id] = node_attrs['city']
    
    # Desenhar os nós - tamanho baseado no log da população
    node_sizes = []
    node_colors = []
    for node_id in G.nodes():
        # Obter dados diretamente do grafo
        node_attrs = G.nodes[node_id]
        population = node_attrs.get('population', 10000)
        
        # Usar log para evitar nós muito grandes
        size = max(50, min(300, math.log(int(population)) * 10))
        node_sizes.append(size)
        
        # Cores baseadas na região (simplificado por estado)
        state = node_attrs.get('state', '')
        if state in ['California', 'Oregon', 'Washington', 'Nevada', 'Arizona']:
            node_colors.append('skyblue')  # Oeste
        elif state in ['Texas', 'Oklahoma', 'Louisiana', 'Arkansas']:
            node_colors.append('lightgreen')  # Sul/Centro
        elif state in ['Florida', 'Georgia', 'South Carolina', 'North Carolina']:
            node_colors.append('yellow')  # Sudeste
        elif state in ['New York', 'Massachusetts', 'Pennsylvania', 'New Jersey']:
            node_colors.append('lightcoral')  # Nordeste
        else:
            node_colors.append('gray')  # Outros estados
    
    # Desenhar os nós
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                          node_color=node_colors, alpha=0.7, ax=ax)
    
    # Desenhar as arestas com transparência proporcional à distância
    edge_alphas = []
    
    # Determinar o divisor para calcular alpha (usar o valor apropriado conforme disponibilidade)
    max_distance = r if r is not None else (d if d is not None else 1.0)
    distance_type = 'weight' if r is not None else 'km_dist'
    
    for u, v, data in G.edges(data=True):
        # Arestas mais curtas são mais visíveis
        if distance_type == 'km_dist' and 'km_dist' in data:
            weight = data.get('km_dist', 1.0)
        else:
            weight = data.get('weight', 1.0)
            
        alpha = max(0.1, min(0.8, 1.0 - weight/max_distance))
        edge_alphas.append(alpha)
        
    nx.draw_networkx_edges(G, pos, width=1, alpha=edge_alphas, ax=ax)
    
    # Desenhar rótulos apenas para as cidades mais importantes (até 20 cidades)
    top_cities = {}
    
    # Identificar até 20 nós com maior população
    node_pop = [(node_id, G.nodes[node_id].get('population', 0)) for node_id in G.nodes()]
    node_pop.sort(key=lambda x: x[1], reverse=True)
    
    for node_id, _ in node_pop[:20]:
        top_cities[node_id] = labels[node_id]
    
    nx.draw_networkx_labels(G, pos, labels=top_cities, font_size=9, 
                           font_family='sans-serif', ax=ax)
    
    # Adicionar legenda
    plt.figtext(0.15, 0.02, "Azul: Oeste", color='skyblue', ha='left')
    plt.figtext(0.35, 0.02, "Verde: Sul/Centro", color='lightgreen', ha='left')
    plt.figtext(0.55, 0.02, "Amarelo: Sudeste", color='yellow', ha='left')
    plt.figtext(0.75, 0.02, "Vermelho: Nordeste", color='lightcoral', ha='left')
    
    plt.tight_layout()
    
    return fig