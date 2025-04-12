import streamlit as st
import pandas as pd
import networkx as nx
import streamlit_folium
import folium
import os
import matplotlib.pyplot as plt
import json
import datetime
from streamlit_option_menu import option_menu
from app.components import city_selector, map_display, progress_bar, report_viewer
from app.utils import data_loader, graph_utils

def app():
    # Importação do módulo algorithms dentro da função para garantir que esteja no escopo correto
    from app.utils import algorithms
    
    # Esconder as informações não desejadas
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:16px;
    }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("Localizador de Rotas entre Cidades")
    st.markdown("""
    ### Encontre o melhor caminho entre cidades americanas usando algoritmos de busca
    
    Este aplicativo utiliza dados reais de mais de 1000 cidades dos Estados Unidos para calcular 
    rotas ótimas considerando distância e outros fatores. Você pode comparar o desempenho de 
    diferentes algoritmos de busca e visualizar os resultados em um mapa interativo.
    """)

    # Inicializar estado de sessão para histórico se não existir
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    # Calcular o caminho absoluto para o arquivo JSON
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, "data", "cities.json")
    
    # Verificar a existência do arquivo
    if not os.path.exists(json_path):
        st.error(f"Arquivo de dados não encontrado: {json_path}")
        st.info("Por favor, verifique se o arquivo cities.json existe na pasta data.")
        return
    
    # Carregar dados
    try:
        with st.spinner("Carregando dados de cidades dos EUA..."):
            cities_df = data_loader.load_data(json_path)
            
            # Exibir informações sobre os dados
            st.sidebar.success(f"{len(cities_df)} cidades carregadas com sucesso!")
            st.sidebar.write("**Estatísticas dos Dados**")
            st.sidebar.write(f"• Maior cidade: {cities_df.iloc[0]['city']}, {cities_df.iloc[0]['state']}")
            st.sidebar.write(f"• População total: {cities_df['population'].sum():,} habitantes")
            st.sidebar.write(f"• Cobertura: {len(cities_df['state'].unique())} estados americanos")
            
            # Adicionar histograma de população se espaço permitir
            with st.sidebar.expander("📊 Distribuição populacional"):
                fig, ax = plt.subplots(figsize=(4, 2))
                ax.hist(cities_df['population'], bins=20, color='purple', alpha=0.7)
                ax.set_xlabel('População')
                ax.set_ylabel('Frequência')
                ax.set_title('Distribuição populacional')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        # Limitar para as 200 maiores cidades para melhor desempenho
        with st.expander("⚙️ Configurações de desempenho", expanded=False):
            numero_cidades = st.slider(
                "Número de cidades a considerar (afeta o desempenho)", 
                min_value=50, 
                max_value=len(cities_df), 
                value=200,
                help="Um número menor de cidades melhora o desempenho do aplicativo"
            )
            cities_df = cities_df.head(numero_cidades)
            st.write(f"Usando as {numero_cidades} maiores cidades para os cálculos.")
        
        city_names = cities_df['city'].tolist()
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {str(e)}")
        st.stop()

    # Interface do usuário em um layout mais limpo
    col1, col2 = st.columns(2)
    
    with col1:
        start_city = city_selector.city_selector(
            "Cidade de Origem", 
            city_names, 
            "New York" if "New York" in city_names else city_names[0]
        )
        
        # Informações detalhadas sobre a cidade de origem
        cidade_origem = cities_df[cities_df['city'] == start_city].iloc[0]
        st.info(f"""
        **{start_city}, {cidade_origem['state']}**
        - População: {int(cidade_origem['population']):,} habitantes
        - Crescimento (2000-2013): {cidade_origem['growth_from_2000_to_2013']}
        - Posição no ranking: {cidade_origem['rank']}
        """)
        
    with col2:
        end_city = city_selector.city_selector(
            "Cidade de Destino", 
            city_names, 
            "Los Angeles" if "Los Angeles" in city_names else city_names[-1]
        )
        
        # Informações detalhadas sobre a cidade de destino
        cidade_destino = cities_df[cities_df['city'] == end_city].iloc[0]
        st.info(f"""
        **{end_city}, {cidade_destino['state']}**
        - População: {int(cidade_destino['population']):,} habitantes
        - Crescimento (2000-2013): {cidade_destino['growth_from_2000_to_2013']}
        - Posição no ranking: {cidade_destino['rank']}
        """)
    
    # Calcular distância direta entre origem e destino usando Haversine
    dist_direta = algorithms.calculate_distance_from_df(cities_df, start_city, end_city)
    dist_haversine = graph_utils.calculate_haversine_distance(
        cities_df[cities_df['city'] == start_city].iloc[0],
        cities_df[cities_df['city'] == end_city].iloc[0]
    )
    
    st.write(f"**Distância em linha reta**: {dist_direta:.2f} graus (aprox. {dist_haversine:.0f} km)")
    
    # Explicação melhorada sobre a relação entre quilômetros e graus
    with st.expander("ℹ️ Conversão entre graus e quilômetros", expanded=False):
        st.markdown("""
        ### Relação entre graus de coordenadas e quilômetros

        Em coordenadas geográficas na superfície da Terra:
        
        - **1 grau de latitude ≈ 111 km** (constante em qualquer lugar da Terra)
        - **1 grau de longitude** varia dependendo da latitude:
          - No Equador (latitude 0°): 1° longitude ≈ 111 km
          - Em latitudes médias (45°): 1° longitude ≈ 79 km
          - Perto dos Polos (90°): 1° longitude ≈ 0 km

        #### Fórmula simplificada
        
        Para uma estimativa rápida:
        ```
        distância em km ≈ graus × 111
        ```
        
        Para cálculos precisos, usamos a **fórmula de Haversine** que leva em conta a curvatura da Terra.
        
        #### Exemplo:
        
        - Raio (r) = 1°
          - Distância em linha reta ≈ 111 km
          - Esta é aproximadamente a distância entre cidades vizinhas ou próximas
        
        - Raio (r) = 10°
          - Distância em linha reta ≈ 1110 km
          - Esta é aproximadamente a distância entre grandes cidades em estados diferentes
        """)
    
    # Seletor de algoritmo e raio com explicações
    st.write("### Parâmetros do algoritmo")
    
    # Adicionar opção para escolher o tipo de conexão
    connection_type = st.radio(
        "Tipo de conexão",
        ["Raio em graus (r)", "Distância em km (d)", "Ambos"],
        help="Escolha o tipo de restrição para conexões entre cidades"
    )
    
    col1, col2 = st.columns(2)
    
    # Cálculo do raio máximo teórico (a distância máxima entre quaisquer duas cidades no conjunto de dados)
    max_latitudes = cities_df['latitude'].max() - cities_df['latitude'].min()
    max_longitudes = cities_df['longitude'].max() - cities_df['longitude'].min()
    max_theoretical_r = ((max_latitudes**2) + (max_longitudes**2))**0.5
    max_theoretical_km = max_theoretical_r * 111  # Aproximação usando 111km por grau
    
    with col1:
        if connection_type in ["Raio em graus (r)", "Ambos"]:
            # Valor sugerido para o raio (1/3 da distância direta, mas permitindo aumentar até o máximo)
            suggested_r = min(10.0, dist_direta / 3)
            
            r = st.slider(
                "Raio de conexão (r)", 
                min_value=1.0, 
                max_value=float(max_theoretical_r),
                value=suggested_r,
                step=0.5,
                help=f"""Define a distância máxima em graus para conexão direta entre cidades. 
                      O valor máximo teórico é {max_theoretical_r:.1f} graus, mas valores acima de 20 
                      podem resultar em caminhos diretos entre cidades muito distantes."""
            )
            
            # Converter para km para referência
            r_in_km = r * 111
            st.caption(f"Raio selecionado: {r:.1f}° ≈ {r_in_km:.0f} km")
        else:
            r = None
            
    with col2:
        if connection_type in ["Distância em km (d)", "Ambos"]:
            # Converter valor em graus para km para um valor padrão inicial
            default_d_value = min(1000.0, dist_haversine / 3)
            
            d = st.slider(
                "Distância máxima em km (d)", 
                min_value=100.0, 
                max_value=float(max_theoretical_km),
                value=default_d_value,
                step=50.0,
                help=f"""Define a distância máxima em quilômetros para conexão direta entre cidades.
                      O valor máximo teórico é {max_theoretical_km:.0f} km, mas valores muito altos
                      podem resultar em caminhos diretos entre cidades muito distantes."""
            )
            
            # Converter para graus para referência
            d_in_degrees = d / 111
            st.caption(f"Distância selecionada: {d:.0f} km ≈ {d_in_degrees:.2f}°")
        else:
            d = None
            
    # Valor de raio recomendado
    with st.expander("🔍 Recomendação de valores para raio (r) ou distância (d)"):
        st.markdown("""
        ### Valores recomendados
        
        #### Para raio em graus (r):
        - **r < 1°**: Apenas cidades muito próximas (até ~111 km)
        - **1° ≤ r ≤ 5°**: Cidades regionalmente próximas (~111-555 km)
        - **5° < r ≤ 10°**: Cidades em estados vizinhos (~555-1110 km)
        - **10° < r ≤ 20°**: Conexões de longa distância (~1110-2220 km)
        - **r > 20°**: Conexões entre cidades muito distantes (não recomendado para roteamento realista)
        
        #### Para distância em km (d):
        - **d < 100 km**: Cidades muito próximas (mesma região metropolitana)
        - **100 ≤ d ≤ 500 km**: Cidades na mesma região
        - **500 < d ≤ 1000 km**: Cidades em estados vizinhos
        - **1000 < d ≤ 2000 km**: Conexões de longa distância
        - **d > 2000 km**: Conexões entre cidades muito distantes (não recomendado para roteamento realista)
        
        Um bom valor inicial é aproximadamente **1/3 da distância em linha reta** entre a origem e o destino.
        """)
    
    algorithm_choice = st.selectbox(
        "Algoritmo de busca", 
        ["Todos", "BFS (Busca em Largura)", "A* (A-Estrela)", "Busca Fuzzy"],
        help="""
        - BFS: Encontra o caminho com menor número de cidades intermediárias
        - A*: Encontra o caminho mais curto em termos de distância
        - Fuzzy: Lida com incertezas nas conexões e pode encontrar rotas alternativas
        """
    )

    # Botão para encontrar a rota com explicação detalhada
    if st.button("🔍 Encontrar Rota", help="Calcula a melhor rota entre as cidades selecionadas"):
        with st.spinner("Calculando a melhor rota... Este processo pode levar alguns segundos dependendo do número de cidades."):
            # Construir o grafo com base no tipo de conexão escolhido
            G = graph_utils.build_graph(cities_df, r=r, d=d)
            
            # Mostrar informações sobre o tipo de conexão utilizado
            connection_info = ""
            if connection_type == "Raio em graus (r)":
                connection_info = f"Conexões baseadas em raio de {r} graus ({r*111:.0f} km)"
            elif connection_type == "Distância em km (d)":
                connection_info = f"Conexões baseadas em distância máxima de {d} km ({d/111:.2f} graus)"
            else:  # Ambos
                connection_info = f"Conexões baseadas em raio de {r} graus ({r*111:.0f} km) E distância máxima de {d} km"
            
            st.write(f"**Tipo de conexão utilizado:** {connection_info}")
            
            # Visualizar o grafo
            st.subheader("Visualização do Grafo")
            st.markdown("""
            <div class="map-container">
            A imagem abaixo mostra a rede de conexões entre cidades. 
            - **Nós**: Representam cidades 
            - **Arestas**: Representam conexões diretas possíveis
            - **Tamanho dos nós**: Proporcional à população da cidade
            </div>
            """, unsafe_allow_html=True)
            
            fig = map_display.display_graph_visualization(G, cities_df, r=r, d=d)
            st.pyplot(fig)
            
            # Estatísticas do grafo
            st.write(f"**Estatísticas da Rede**:")
            st.write(f"- Número de cidades (nós): {G.number_of_nodes():,}")
            st.write(f"- Número de conexões (arestas): {G.number_of_edges():,}")
            st.write(f"- Densidade da rede: {nx.density(G):.4f}")
            
            # Verificar se existe um caminho entre as cidades
            path_exists = nx.has_path(G, start_city, end_city)
            if not path_exists:
                st.error(f"Não foi possível encontrar um caminho entre {start_city} e {end_city} com os parâmetros atuais.")
                
                # Sugerir um valor de r adequado
                components = list(nx.connected_components(G))
                start_component = None
                end_component = None
                
                for i, comp in enumerate(components):
                    if start_city in comp:
                        start_component = i
                    if end_city in comp:
                        end_component = i
                
                if start_component is not None and end_component is not None and start_component != end_component:
                    st.warning(f"As cidades estão em componentes diferentes do grafo. Origem: componente {start_component+1}, Destino: componente {end_component+1}")
                    
                    # Encontrar o menor r que conectaria as cidades
                    if connection_type in ["Raio em graus (r)", "Ambos"]:
                        min_r = dist_direta
                        st.info(f"Sugestão: Tente um raio de pelo menos {min_r:.1f}° (aprox. {min_r*111:.0f} km) para ter uma conexão direta entre a origem e o destino.")
                    elif connection_type == "Distância em km (d)":
                        min_d = dist_haversine
                        st.info(f"Sugestão: Tente uma distância de pelo menos {min_d:.0f} km para ter uma conexão direta entre a origem e o destino.")
                return

            # Resultados
            bfs_path, bfs_distance = None, None
            a_star_path, a_star_distance = None, None
            fuzzy_path, fuzzy_distance, fuzzy_certainty = None, None, None
            
            # Executar os algoritmos selecionados
            if algorithm_choice in ["Todos", "BFS (Busca em Largura)"]:
                progress_bar.update_progress(0.25, "Executando BFS...")
                bfs_path, bfs_distance = algorithms.breadth_first_search(G, start_city, end_city)
            
            if algorithm_choice in ["Todos", "A* (A-Estrela)"]:
                progress_bar.update_progress(0.50, "Executando A*...")
                a_star_path, a_star_distance = algorithms.a_star_search(G, cities_df, start_city, end_city)
            
            if algorithm_choice in ["Todos", "Busca Fuzzy"]:
                progress_bar.update_progress(0.75, "Executando Busca Fuzzy...")
                fuzzy_path, fuzzy_distance, fuzzy_certainty = algorithms.fuzzy_search(G, cities_df, start_city, end_city, r=r, d=d)
            
            progress_bar.update_progress(1.0, "Concluído!")

            # Função para calcular a distância total em km de um caminho
            def calcular_distancia_km_caminho(path):
                if not path or len(path) < 2:
                    return 0
                
                distancia_total = 0
                for i in range(len(path)-1):
                    cidade1 = cities_df[cities_df['city'] == path[i]].iloc[0]
                    cidade2 = cities_df[cities_df['city'] == path[i+1]].iloc[0]
                    distancia_total += graph_utils.calculate_haversine_distance(cidade1, cidade2)
                
                return distancia_total

            # Criação de um dicionário para armazenar os resultados
            results = {
                'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'start_city': start_city,
                'end_city': end_city,
                'params': connection_info,
                'algorithms': {}
            }

            paths_to_display = []
            
            if algorithm_choice in ["Todos", "BFS (Busca em Largura)"]:
                if bfs_path:
                    bfs_km = calcular_distancia_km_caminho(bfs_path)
                    results['algorithms']['BFS'] = {
                        'path': bfs_path,
                        'distance_degrees': bfs_distance,
                        'distance_km': bfs_km,
                        'cities_count': len(bfs_path)
                    }
                    paths_to_display.append(bfs_path)
                else:
                    results['algorithms']['BFS'] = None
                    paths_to_display.append([])

            if algorithm_choice in ["Todos", "A* (A-Estrela)"]:
                if a_star_path:
                    astar_km = calcular_distancia_km_caminho(a_star_path)
                    results['algorithms']['A*'] = {
                        'path': a_star_path,
                        'distance_degrees': a_star_distance,
                        'distance_km': astar_km,
                        'cities_count': len(a_star_path)
                    }
                    paths_to_display.append(a_star_path)
                else:
                    results['algorithms']['A*'] = None
                    paths_to_display.append([])

            if algorithm_choice in ["Todos", "Busca Fuzzy"]:
                if fuzzy_path:
                    fuzzy_km = calcular_distancia_km_caminho(fuzzy_path)
                    results['algorithms']['Fuzzy'] = {
                        'path': fuzzy_path,
                        'distance_degrees': fuzzy_distance,
                        'distance_km': fuzzy_km,
                        'cities_count': len(fuzzy_path),
                        'certainty': fuzzy_certainty
                    }
                    paths_to_display.append(fuzzy_path)
                else:
                    results['algorithms']['Fuzzy'] = None
                    paths_to_display.append([])
            
            # Salvar resultados no histórico da sessão
            st.session_state.search_history.append(results)
            
            # Exibir resultados detalhados em um sistema de abas
            st.header("Resultados da Busca")
            
            # Definir abas para os resultados
            tabs = []
            tab_titles = []
            
            # Sempre adicionar a aba principal
            tab_titles.append("Rotas Encontradas")
            
            # Adicionar as outras abas conforme os algoritmos utilizados
            if algorithm_choice in ["Todos", "BFS (Busca em Largura)"] and bfs_path:
                tab_titles.append("BFS")
                
            if algorithm_choice in ["Todos", "A* (A-Estrela)"] and a_star_path:
                tab_titles.append("A*")
                
            if algorithm_choice in ["Todos", "Busca Fuzzy"] and fuzzy_path:
                tab_titles.append("Fuzzy")
            
            # Se mais de um algoritmo foi executado, adicionar aba de comparação
            if (algorithm_choice == "Todos" and 
                sum(1 for p in [bfs_path, a_star_path, fuzzy_path] if p) > 1):
                tab_titles.append("Comparação")
            
            # Adicionar aba para estatísticas
            tab_titles.append("Estatísticas")
            
            # Criar as abas
            tabs = st.tabs(tab_titles)
            
            # Aba principal - Rotas Encontradas
            with tabs[0]:
                st.markdown("""
                As rotas encontradas são mostradas no mapa abaixo. Você pode comparar as diferentes 
                abordagens e seus resultados nas outras abas.
                """)
                
                # Exibir mapa
                st.subheader("🗺️ Visualização das Rotas no Mapa")
                st.markdown("""
                <div class="map-container">
                O mapa abaixo mostra as rotas encontradas pelos algoritmos selecionados. 
                - **Azul**: Rota do BFS
                - **Verde**: Rota do A*
                - **Vermelho**: Rota do Fuzzy Search
                
                Você pode usar o zoom e arrastar para explorar melhor o mapa.
                </div>
                """, unsafe_allow_html=True)
                
                map_display.display_route_map(cities_df, paths_to_display)
            
            # Contador para acompanhar o índice da aba atual
            tab_index = 1
                
            # Aba BFS
            if "BFS" in tab_titles:
                with tabs[tab_index]:
                    st.subheader("🔄 Busca em Largura (BFS)")
                    st.write("""
                    A BFS encontra o caminho com o menor número de cidades intermediárias, 
                    mas não necessariamente a menor distância total.
                    """)
                    st.write(f"**Caminho BFS:** { ' → '.join(bfs_path) }")
                    st.write(f"**Distância BFS:** {bfs_distance:.2f} graus (aprox. {results['algorithms']['BFS']['distance_km']:.0f} km)")
                    st.write(f"**Número de cidades no caminho:** {len(bfs_path)}")
                    
                    # Mostrar detalhes do caminho
                    st.subheader("📋 Detalhes das Cidades no Caminho BFS")
                    path_cities = cities_df[cities_df['city'].isin(bfs_path)].sort_values(
                        by='city', 
                        key=lambda x: pd.Series(x).map({city: i for i, city in enumerate(bfs_path)})
                    )
                    display_cols = ['city', 'state', 'population', 'growth_from_2000_to_2013', 'latitude', 'longitude']
                    st.dataframe(path_cities[display_cols], use_container_width=True)
                    
                tab_index += 1
            
            # Aba A*
            if "A*" in tab_titles:
                with tabs[tab_index]:
                    st.subheader("⭐ A* (A-Estrela)")
                    st.write("""
                    O A* combina a distância percorrida com uma estimativa da distância restante.
                    Geralmente encontra o caminho mais curto em termos de distância total.
                    """)
                    st.write(f"**Caminho A*:** { ' → '.join(a_star_path) }")
                    st.write(f"**Distância A*:** {a_star_distance:.2f} graus (aprox. {results['algorithms']['A*']['distance_km']:.0f} km)")
                    st.write(f"**Número de cidades no caminho:** {len(a_star_path)}")
                    
                    # Mostrar detalhes do caminho
                    st.subheader("📋 Detalhes das Cidades no Caminho A*")
                    path_cities = cities_df[cities_df['city'].isin(a_star_path)].sort_values(
                        by='city', 
                        key=lambda x: pd.Series(x).map({city: i for i, city in enumerate(a_star_path)})
                    )
                    display_cols = ['city', 'state', 'population', 'growth_from_2000_to_2013', 'latitude', 'longitude']
                    st.dataframe(path_cities[display_cols], use_container_width=True)
                    
                tab_index += 1
                
            # Aba Fuzzy
            if "Fuzzy" in tab_titles:
                with tabs[tab_index]:
                    st.subheader("🧩 Busca Fuzzy")
                    st.write("""
                    A Busca Fuzzy lida com incertezas nas conexões. O valor de certeza indica a 
                    confiabilidade da rota, com 1.0 sendo completamente confiável e valores menores 
                    indicando rotas menos confiáveis, mas potencialmente úteis.
                    """)
                    st.write(f"**Caminho Fuzzy:** { ' → '.join(fuzzy_path) }")
                    st.write(f"**Distância Fuzzy:** {fuzzy_distance:.2f} graus (aprox. {results['algorithms']['Fuzzy']['distance_km']:.0f} km)")
                    st.write(f"**Certeza Fuzzy:** {fuzzy_certainty:.2f} (quanto maior, mais confiável)")
                    st.write(f"**Número de cidades no caminho:** {len(fuzzy_path)}")
                    
                    # Explicar o valor de certeza
                    if fuzzy_certainty < 0.3:
                        st.warning("A certeza baixa sugere que este caminho pode não ser ideal ou confiável.")
                    elif fuzzy_certainty > 0.7:
                        st.success("A alta certeza sugere que este caminho é altamente confiável.")
                        
                    # Mostrar detalhes do caminho
                    st.subheader("📋 Detalhes das Cidades no Caminho Fuzzy")
                    path_cities = cities_df[cities_df['city'].isin(fuzzy_path)].sort_values(
                        by='city', 
                        key=lambda x: pd.Series(x).map({city: i for i, city in enumerate(fuzzy_path)})
                    )
                    display_cols = ['city', 'state', 'population', 'growth_from_2000_to_2013', 'latitude', 'longitude']
                    st.dataframe(path_cities[display_cols], use_container_width=True)
                    
                tab_index += 1
                
            # Aba de Comparação
            if "Comparação" in tab_titles:
                with tabs[tab_index]:
                    st.subheader("📊 Comparação entre Algoritmos")
                    
                    # Criar dataframe para comparação
                    comparison_data = []
                    
                    if bfs_path:
                        comparison_data.append({
                            "Algoritmo": "BFS", 
                            "Distância_valor": results['algorithms']['BFS']['distance_km'],
                            "Distância": f"{bfs_distance:.2f} graus",
                            "Distância (km)": f"{results['algorithms']['BFS']['distance_km']:.0f} km",
                            "Cidades": len(bfs_path),
                            "Cidades intermediárias": len(bfs_path) - 2
                        })
                    
                    if a_star_path:
                        comparison_data.append({
                            "Algoritmo": "A*", 
                            "Distância_valor": results['algorithms']['A*']['distance_km'],
                            "Distância": f"{a_star_distance:.2f} graus",
                            "Distância (km)": f"{results['algorithms']['A*']['distance_km']:.0f} km",
                            "Cidades": len(a_star_path),
                            "Cidades intermediárias": len(a_star_path) - 2
                        })
                    
                    if fuzzy_path:
                        comparison_data.append({
                            "Algoritmo": "Fuzzy", 
                            "Distância_valor": results['algorithms']['Fuzzy']['distance_km'],
                            "Distância": f"{fuzzy_distance:.2f} graus",
                            "Distância (km)": f"{results['algorithms']['Fuzzy']['distance_km']:.0f} km",
                            "Cidades": len(fuzzy_path),
                            "Cidades intermediárias": len(fuzzy_path) - 2,
                            "Certeza": f"{fuzzy_certainty:.2f}"
                        })
                    
                    if comparison_data:
                        # Criar cópia sem a coluna Distância_valor para exibição
                        display_data = [{k: v for k, v in d.items() if k != 'Distância_valor'} for d in comparison_data]
                        st.table(pd.DataFrame(display_data))
                        
                        # Determinar o algoritmo mais eficiente usando o valor numérico
                        best_distance = min([d['Distância_valor'] for d in comparison_data])
                        best_algorithm = [d['Algoritmo'] for d in comparison_data if d['Distância_valor'] == best_distance][0]
                        st.success(f"Para este caso específico, o algoritmo **{best_algorithm}** encontrou o caminho mais curto.")
                        
                        # Adicionar gráficos de comparação
                        st.subheader("Comparação Visual")
                        
                        # Gráfico de barras para distância
                        fig1, ax1 = plt.subplots(figsize=(10, 6))
                        algorithms = [d["Algoritmo"] for d in comparison_data]
                        distances = [d["Distância_valor"] for d in comparison_data]
                        colors = ["#5470C6", "#91CC75", "#EE6666"][:len(algorithms)]
                        
                        ax1.bar(algorithms, distances, color=colors)
                        ax1.set_ylabel("Distância (km)")
                        ax1.set_title("Comparação de distância total por algoritmo")
                        ax1.grid(axis='y', alpha=0.3)
                        
                        for i, v in enumerate(distances):
                            ax1.text(i, v + 50, f"{v:.0f} km", ha='center', fontweight='bold')
                            
                        st.pyplot(fig1)
                        
                        # Gráfico de barras para número de cidades
                        fig2, ax2 = plt.subplots(figsize=(10, 6))
                        city_counts = [d["Cidades"] for d in comparison_data]
                        
                        ax2.bar(algorithms, city_counts, color=colors)
                        ax2.set_ylabel("Número de cidades")
                        ax2.set_title("Comparação de número de cidades no caminho")
                        ax2.grid(axis='y', alpha=0.3)
                        
                        for i, v in enumerate(city_counts):
                            ax2.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
                            
                        st.pyplot(fig2)
                    
                tab_index += 1
                
            # Aba de Estatísticas
            with tabs[tab_index]:
                st.subheader("📈 Estatísticas Detalhadas")
                
                # Se temos pelo menos um caminho
                if any(paths_to_display):
                    # Escolher o primeiro caminho válido para estatísticas
                    valid_path = next((p for p in paths_to_display if p), None)
                    
                    if valid_path:
                        # Estatísticas das cidades no caminho
                        path_cities = cities_df[cities_df['city'].isin(valid_path)]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("População total nas cidades do caminho", 
                                      f"{path_cities['population'].sum():,}")
                            
                            # Média de população
                            avg_pop = path_cities['population'].mean()
                            st.metric("População média por cidade", 
                                      f"{avg_pop:,.0f}")
                        
                        with col2:
                            # Encontrar a cidade mais populosa
                            most_populous = path_cities.loc[path_cities['population'].idxmax()]
                            st.metric("Cidade mais populosa no caminho", 
                                      f"{most_populous['city']}", 
                                      f"{most_populous['population']:,} habitantes")
                            
                            # Calcular o crescimento médio
                            avg_growth = path_cities['growth_from_2000_to_2013'].str.rstrip('%').astype(float).mean()
                            st.metric("Crescimento populacional médio", 
                                      f"{avg_growth:.1f}%")
                        
                        # Distribuição de população nas cidades do caminho
                        st.subheader("Distribuição populacional das cidades no caminho")
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        cities_sorted = path_cities.sort_values(by='population', ascending=False)
                        
                        ax.bar(cities_sorted['city'], cities_sorted['population'], color='purple')
                        ax.set_xlabel("Cidade")
                        ax.set_ylabel("População")
                        ax.tick_params(axis='x', rotation=45)
                        ax.grid(axis='y', alpha=0.3)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Distribuição por estado
                        st.subheader("Distribuição de cidades por estado")
                        state_counts = path_cities['state'].value_counts()
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.pie(state_counts, labels=state_counts.index, autopct='%1.1f%%', 
                              startangle=90, shadow=True)
                        ax.axis('equal')
                        plt.tight_layout()
                        st.pyplot(fig)
                else:
                    st.warning("Nenhum caminho válido encontrado para análise estatística.")
            
            # Adicionar a entrada do histórico para o último resultado
            st.divider()
            st.header("Histórico de Buscas")
            
            # Exibir histórico de buscas em formato de cards
            if st.session_state.search_history:
                # Mostrar apenas as últimas 10 buscas (incluindo a atual)
                history = st.session_state.search_history[-10:]
                history.reverse()  # Mais recentes primeiro
                
                for i, search in enumerate(history):
                    if i > 0:  # Pular o resultado atual que já está sendo exibido em detalhes
                        with st.expander(f"Busca {len(history)-i}: {search['start_city']} → {search['end_city']} ({search['timestamp']})"):
                            st.write(f"**Parâmetros**: {search['params']}")
                            
                            # Mostrar resultados resumidos para cada algoritmo
                            for alg_name, alg_results in search['algorithms'].items():
                                if alg_results:
                                    st.write(f"**{alg_name}**: {alg_results['distance_km']:.0f} km, {alg_results['cities_count']} cidades")
                                    if 'certainty' in alg_results:
                                        st.write(f"Certeza: {alg_results['certainty']:.2f}")
                                else:
                                    st.write(f"**{alg_name}**: Nenhum caminho encontrado")
            else:
                st.info("Nenhuma busca anterior registrada.")