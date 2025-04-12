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
    """
    # Verificação de dados
    if 'latitude' not in cities_df.columns or 'longitude' not in cities_df.columns:
        st.error("Dados de latitude e longitude não encontrados. Verifique o arquivo cities.json.")
        st.write("Colunas disponíveis:", cities_df.columns.tolist())
        st.write("Primeiras linhas dos dados:", cities_df.head().to_dict())
        return
    
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
                Cores das Rotas: Azul (BFS), Verde (A*), Vermelho (Fuzzy)
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
            Crescimento (2000-2013): {row['growth_from_2000_to_2013']}<br>
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
        colors = ['blue', 'green', 'red', 'purple', 'orange']
        route_names = ["Rota BFS", "Rota A*", "Rota Fuzzy"]
        
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
                folium.PolyLine(
                    route_points,
                    weight=4,
                    color=colors[i % len(colors)],
                    opacity=0.8,
                    tooltip=route_name,
                    popup=f"{route_name}: {len(path)} cidades, {len(path)-2} paradas intermediárias"
                ).add_to(m)
            else:
                st.warning(f"Pontos insuficientes para desenhar a rota {i+1}: apenas {len(route_points)} pontos encontrados")
        
        # Adicionar escala e controle de camadas ao mapa
        folium.LayerControl(position='topright', collapsed=False).add_to(m)
        
        # Exibir o mapa no Streamlit
        folium_static(m, width=800, height=500)
        
        st.caption("**Dica**: Utilize o controle de camadas no canto superior direito para exibir/ocultar rotas e cidades.")
        
    except Exception as e:
        st.error(f"Erro ao criar o mapa: {str(e)}")
        st.write("Dados utilizados:", cities_df.head())
        
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
    
    # Posições dos nós baseadas em coordenadas
    pos = {}
    for index, data in cities_df.iterrows():
        # Usar coordenadas geográficas para posicionar os nós
        pos[data['city']] = (data['longitude'], data['latitude'])
    
    # Desenhar os nós - tamanho baseado no log da população
    node_sizes = []
    node_colors = []
    for node in G.nodes():
        city_data = cities_df[cities_df['city'] == node]
        if not city_data.empty:
            # Usar log para evitar nós muito grandes
            size = max(50, min(300, math.log(int(city_data.iloc[0]['population'])) * 10))
            node_sizes.append(size)
            
            # Cores baseadas na região (simplificado por estado)
            state = city_data.iloc[0]['state']
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
        else:
            node_sizes.append(100)  # Tamanho padrão
            node_colors.append('gray')
    
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
    
    # Desenhar rótulos apenas para as cidades mais importantes (top 20)
    important_cities = cities_df.nlargest(20, 'population')['city'].tolist()
    labels = {city: city for city in G.nodes() if city in important_cities}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, 
                         font_family='sans-serif', ax=ax)
    
    # Adicionar legenda
    plt.figtext(0.15, 0.02, "Azul: Oeste", color='skyblue', ha='left')
    plt.figtext(0.35, 0.02, "Verde: Sul/Centro", color='lightgreen', ha='left')
    plt.figtext(0.55, 0.02, "Amarelo: Sudeste", color='yellow', ha='left')
    plt.figtext(0.75, 0.02, "Vermelho: Nordeste", color='lightcoral', ha='left')
    
    plt.tight_layout()
    
    return fig