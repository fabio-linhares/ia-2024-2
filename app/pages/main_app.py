import streamlit as st
import pandas as pd
import networkx as nx
import streamlit_folium
import folium
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from app.components import city_selector, map_display, progress_bar, report_viewer
from app.utils import algorithms, data_loader, graph_utils

def app():
    st.title("Localizador de Rotas entre Cidades")
    st.markdown("""
    ### Encontre o melhor caminho entre cidades americanas usando algoritmos de busca
    
    Este aplicativo utiliza dados reais de mais de 1000 cidades dos Estados Unidos para calcular 
    rotas ótimas considerando distância e outros fatores. Você pode comparar o desempenho de 
    diferentes algoritmos de busca e visualizar os resultados em um mapa interativo.
    
    **Como funciona**:
    1. O parâmetro **r** representa o raio máximo de conexão direta entre cidades (em graus de coordenadas)
    2. Um valor menor de **r** cria conexões mais curtas, simulando estradas locais
    3. Um valor maior permite "saltos" maiores entre cidades, simulando conexões aéreas ou interestaduais
    """)

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
        st.info("Carregando dados de cidades dos EUA... Este processo pode levar alguns segundos.")
        cities_df = data_loader.load_data(json_path)
        
        # Exibir informações sobre os dados
        st.sidebar.success(f"{len(cities_df)} cidades carregadas com sucesso!")
        st.sidebar.write("**Estatísticas dos Dados**")
        st.sidebar.write(f"• Maior cidade: {cities_df.iloc[0]['city']}, {cities_df.iloc[0]['state']}")
        st.sidebar.write(f"• População total: {cities_df['population'].sum():,} habitantes")
        st.sidebar.write(f"• Cobertura: {len(cities_df['state'].unique())} estados americanos")
        
        # Limitar para as 200 maiores cidades para melhor desempenho
        with st.expander("⚙️ Configurações de desempenho"):
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

    # Interface do usuário
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
    
    # Seletor de algoritmo e raio com explicações
    st.write("### Parâmetros do algoritmo")
    
    # Adicionar opção para escolher o tipo de conexão
    connection_type = st.radio(
        "Tipo de conexão",
        ["Raio em graus (r)", "Distância em km (d)", "Ambos"],
        help="Escolha o tipo de restrição para conexões entre cidades"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if connection_type in ["Raio em graus (r)", "Ambos"]:
            r = st.slider(
                "Raio de conexão (r)", 
                min_value=1.0, 
                max_value=20.0, 
                value=min(10.0, dist_direta / 3),
                step=0.5,
                help="Define a distância máxima em graus para conexão direta entre cidades."
            )
        else:
            r = None
            
    with col2:
        if connection_type in ["Distância em km (d)", "Ambos"]:
            # Converter valor em graus para km para um valor padrão inicial
            default_d_value = min(1000.0, dist_haversine / 3)
            d = st.slider(
                "Distância máxima em km (d)", 
                min_value=100.0, 
                max_value=3000.0, 
                value=default_d_value,
                step=50.0,
                help="Define a distância máxima em quilômetros para conexão direta entre cidades."
            )
        else:
            d = None
            
    with st.expander("ℹ️ Sobre os parâmetros de conexão"):
        st.markdown("""
        - **Raio em graus (r)**: Usa a distância euclidiana entre as coordenadas (em graus). 
          Valores típicos variam de 1 a 20.
        - **Distância em km (d)**: Usa a distância real em quilômetros (fórmula de Haversine). 
          Mais intuitiva e precisa para distâncias reais.
        - **Ambos**: Cria conexão apenas se ambas as condições forem satisfeitas.
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
                connection_info = f"Conexões baseadas em raio de {r} graus"
            elif connection_type == "Distância em km (d)":
                connection_info = f"Conexões baseadas em distância máxima de {d} km"
            else:  # Ambos
                connection_info = f"Conexões baseadas em raio de {r} graus E distância máxima de {d} km"
            
            st.write(f"**Tipo de conexão utilizado:** {connection_info}")
            
            # Visualizar o grafo
            st.subheader("Visualização do Grafo")
            st.write("""
            A imagem abaixo mostra a rede de conexões entre cidades. 
            - **Nós**: Representam cidades 
            - **Arestas**: Representam conexões diretas possíveis
            - **Tamanho dos nós**: Proporcional à população da cidade
            
            Um grafo mais denso (com mais conexões) facilita encontrar caminhos, mas pode aumentar o tempo de processamento.
            """)
            
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
                st.error(f"Não foi possível encontrar um caminho entre {start_city} e {end_city} com o raio r={r}.")
                st.info("Tente aumentar o valor do raio (r) ou escolher cidades mais próximas.")
                
                # Sugerir um valor de r adequado
                components = list(nx.connected_components(G))
                start_component = None
                end_component = None
                
                for i, comp in enumerate(components):
                    if start_city in comp:
                        start_component = i
                    if end_city in comp:
                        end_component = i
                
                if start_component != end_component:
                    st.warning(f"As cidades estão em componentes diferentes do grafo. Origem: componente {start_component+1}, Destino: componente {end_component+1}")
                    
                    # Encontrar o menor r que conectaria as cidades
                    min_r = dist_direta
                    st.info(f"Sugestão: Tente um raio de pelo menos {min_r:.1f} para ter uma conexão direta entre a origem e o destino.")
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

            # Exibir resultados detalhados
            st.header("Resultados da Busca")
            st.write("""
            Os resultados abaixo mostram as rotas encontradas pelos diferentes algoritmos.
            Compare as distâncias totais e o número de cidades intermediárias para entender
            as vantagens de cada abordagem.
            """)

            paths_to_display = []
            
            if algorithm_choice in ["Todos", "BFS (Busca em Largura)"]:
                if bfs_path:
                    bfs_km = calcular_distancia_km_caminho(bfs_path)
                    st.subheader("🔄 Busca em Largura (BFS)")
                    st.write("""
                    A BFS encontra o caminho com o menor número de cidades intermediárias, 
                    mas não necessariamente a menor distância total.
                    """)
                    st.write(f"**Caminho BFS:** { ' → '.join(bfs_path) }")
                    st.write(f"**Distância BFS:** {bfs_distance:.2f} graus (aprox. {bfs_km:.0f} km)")
                    st.write(f"**Número de cidades no caminho:** {len(bfs_path)}")
                    paths_to_display.append(bfs_path)
                else:
                    st.write("BFS: Nenhum caminho encontrado.")
                    paths_to_display.append([])

            if algorithm_choice in ["Todos", "A* (A-Estrela)"]:
                if a_star_path:
                    astar_km = calcular_distancia_km_caminho(a_star_path)
                    st.subheader("⭐ A* (A-Estrela)")
                    st.write("""
                    O A* combina a distância percorrida com uma estimativa da distância restante.
                    Geralmente encontra o caminho mais curto em termos de distância total.
                    """)
                    st.write(f"**Caminho A*:** { ' → '.join(a_star_path) }")
                    st.write(f"**Distância A*:** {a_star_distance:.2f} graus (aprox. {astar_km:.0f} km)")
                    st.write(f"**Número de cidades no caminho:** {len(a_star_path)}")
                    paths_to_display.append(a_star_path)
                else:
                    st.write("A*: Nenhum caminho encontrado.")
                    paths_to_display.append([])

            if algorithm_choice in ["Todos", "Busca Fuzzy"]:
                if fuzzy_path:
                    fuzzy_km = calcular_distancia_km_caminho(fuzzy_path)
                    st.subheader("🧩 Busca Fuzzy")
                    st.write("""
                    A Busca Fuzzy lida com incertezas nas conexões. O valor de certeza indica a 
                    confiabilidade da rota, com 1.0 sendo completamente confiável e valores menores 
                    indicando rotas menos confiáveis, mas potencialmente úteis.
                    """)
                    st.write(f"**Caminho Fuzzy:** { ' → '.join(fuzzy_path) }")
                    st.write(f"**Distância Fuzzy:** {fuzzy_distance:.2f} graus (aprox. {fuzzy_km:.0f} km)")
                    st.write(f"**Certeza Fuzzy:** {fuzzy_certainty:.2f} (quanto maior, mais confiável)")
                    st.write(f"**Número de cidades no caminho:** {len(fuzzy_path)}")
                    paths_to_display.append(fuzzy_path)
                    
                    # Explicar o valor de certeza
                    if fuzzy_certainty < 0.3:
                        st.warning("A certeza baixa sugere que este caminho pode não ser ideal ou confiável.")
                    elif fuzzy_certainty > 0.7:
                        st.success("A alta certeza sugere que este caminho é altamente confiável.")
                else:
                    st.write("Fuzzy: Nenhum caminho encontrado.")
                    paths_to_display.append([])
            
            # Realizar comparação entre algoritmos se mais de um foi executado
            if algorithm_choice == "Todos":
                st.subheader("📊 Comparação entre Algoritmos")
                
                # Criar dataframe para comparação
                comparison_data = []
                
                if bfs_path:
                    bfs_km = calcular_distancia_km_caminho(bfs_path)
                    comparison_data.append({
                        "Algoritmo": "BFS", 
                        "Distância_valor": bfs_km,  # Valor numérico para comparação (agora em KM)
                        "Distância": f"{bfs_distance:.2f} graus",
                        "Distância (km)": f"{bfs_km:.0f} km",
                        "Cidades": len(bfs_path),
                        "Cidades intermediárias": len(bfs_path) - 2
                    })
                
                if a_star_path:
                    astar_km = calcular_distancia_km_caminho(a_star_path)
                    comparison_data.append({
                        "Algoritmo": "A*", 
                        "Distância_valor": astar_km,  # Valor numérico para comparação (agora em KM)
                        "Distância": f"{a_star_distance:.2f} graus",
                        "Distância (km)": f"{astar_km:.0f} km",
                        "Cidades": len(a_star_path),
                        "Cidades intermediárias": len(a_star_path) - 2
                    })
                
                if fuzzy_path:
                    fuzzy_km = calcular_distancia_km_caminho(fuzzy_path)
                    comparison_data.append({
                        "Algoritmo": "Fuzzy", 
                        "Distância_valor": fuzzy_km,  # Valor numérico para comparação (agora em KM)
                        "Distância": f"{fuzzy_distance:.2f} graus",
                        "Distância (km)": f"{fuzzy_km:.0f} km",
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

            # Exibir mapa
            st.subheader("🗺️ Visualização das Rotas no Mapa")
            st.write("""
            O mapa abaixo mostra as rotas encontradas pelos algoritmos selecionados. 
            - **Azul**: Rota do BFS
            - **Verde**: Rota do A*
            - **Vermelho**: Rota do Fuzzy Search
            
            Você pode usar o zoom e arrastar para explorar melhor o mapa.
            """)
            map_display.display_route_map(cities_df, paths_to_display)
            
            # Exibir mais detalhes sobre as cidades no caminho
            if any(paths_to_display):
                # Pegar o primeiro caminho não vazio
                path_for_details = next((p for p in paths_to_display if p), None)
                
                if path_for_details:
                    st.subheader("📋 Detalhes das Cidades no Caminho")
                    st.write("Abaixo estão detalhes demográficos e geográficos das cidades no caminho selecionado:")
                    
                    # Criar DataFrame com informações das cidades no caminho
                    path_cities = cities_df[cities_df['city'].isin(path_for_details)].sort_values(
                        by='city', 
                        key=lambda x: pd.Series(x).map({city: i for i, city in enumerate(path_for_details)})
                    )
                    
                    # Limpar e formatar os dados para exibição
                    display_cols = ['city', 'state', 'population', 'growth_from_2000_to_2013', 'latitude', 'longitude']
                    st.dataframe(path_cities[display_cols], use_container_width=True)