# Standard library
import datetime
import json
import os
import time

# Third‑party libraries
import folium
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats
import streamlit as st
import streamlit_folium
from streamlit_option_menu import option_menu

# Local application imports
from app.components import city_selector, map_display, progress_bar, report_viewer
from app.utils import data_loader, graph_utils


def app():
    # Importação do módulo algorithms dentro da função para garantir que esteja no escopo correto
    from app.utils import algorithms
    
    # Esconder as informações não desejadas e aplicar estilos personalizados
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:16px;
    }
    /* Remove a barra horizontal no topo */
    header {
        background-color: transparent !important;
        border-bottom: none !important;
    }
    /* Ajusta o título para ficar mais próximo do topo */
    .block-container {
        padding-top: 1rem !important;
    }
    /* Deixa o título com estilo mais destacado */
    h1:first-of-type {
        margin-top: 0 !important;
        padding-top: 0 !important;
        font-size: 2.5rem !important;
        color: var(--primary-color) !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
    }
    /* Ocultar seletor de tema na barra superior */
    div[data-testid="stToolbar"] button[aria-label="View theme"] {
        display: none !important;
    }
    /* Remover qualquer barra de cores no topo */
    header::before, 
    body::before,
    .main::before,
    #root::before,
    [data-testid="stAppViewContainer"]::before,
    [data-testid="stHeader"]::before {
        content: none !important;
        background: none !important;
        display: none !important;
    }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Título e subtítulo centralizados com espaçamento reduzido
    st.markdown("""
    <div style="text-align: center;">
                    <h1 style="margin-top: 0.2rem; margin-bottom: 0.5rem;">City Router</h1>
    <h3 style="margin-bottom: 0.5rem; font-weight: normal;">Encontre a melhor rota entre cidades 
                americanas usando algoritmos clássicos de busca </h3>

    </div>
    """, unsafe_allow_html=True)
    
    # Calcular o caminho absoluto para o arquivo JSON
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, "data", "cities.json")
    
    # Verificar a existência do arquivo
    if not os.path.exists(json_path):
        st.error(f"Arquivo de dados não encontrado: {json_path}")
        # Expandir automaticamente a seção de configurações
        st.session_state.show_config = True
        st.info("Por favor, verifique se o arquivo cities.json existe na pasta data ou faça upload do arquivo na seção 'Configurações Rápidas' da barra lateral.")
        return
    
    # Carregar dados
    try:
        with st.spinner("Carregando dados do arquivo JSON..."):
            cities_df, name_to_id, id_to_name = data_loader.load_data(json_path)
            
            # Dashboard no topo da página
            st.markdown("""
            <div style="margin-bottom: 1.5rem; animation: fadeIn 0.5s ease forwards;">
                <p>Este aplicativo foi desenvolvido para atender à atividade de Problem Solving 
                        proposta pelo Professor Doutor Glauber Rodrigues Leite. A partir de um arquivo 
                        JSON contendo o ranking das cidades mais populosas dos Estados Unidos, o sistema 
                        cria um grafo onde duas cidades estão diretamente conectadas sempre que a distância 
                        euclidiana entre elas é menor ou igual a um parâmetro [ r ] definido pelo usuário. 
                        O objetivo principal é encontrar a rota de menor distância acumulada entre duas cidades 
                        arbitrárias, aplicando como critério de desempate o atributo de população (priorizando 
                        cidades menos populosas).</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Cards do Dashboard
            st.markdown("""
            <div style="margin-bottom: 2rem;">
                <h3 style="margin-bottom: 1rem;">📊 Resumo dos dados carregados</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Criar dashboard com cards
            col1, col2, col3, col4 = st.columns(4)
            
            # Calcular estatísticas para os cards
            total_cities = len(cities_df)
            total_population = cities_df['population'].sum()
            max_pop_city = cities_df.iloc[0]['city']
            states_count = len(cities_df['state'].unique())
            
            # Função para criar um card
            def create_card(column, title, value, icon, subtitle, color_class):
                delay_index = 1
                if column == col2:
                    delay_index = 2
                elif column == col3:
                    delay_index = 3
                elif column == col4:
                    delay_index = 4
                
                delay_class = f"delay-{delay_index}"
                column.markdown(f"""
                <div class="dashboard-card card-{color_class} animate-fadeIn {delay_class}">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-value">{value}</div>
                    <div class="card-subtitle">{subtitle}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Card 1 - Total de cidades
            create_card(
                col1, 
                "TOTAL DE CIDADES", 
                f"{total_cities:,}".replace(",", "."), 
                "🏙️", 
                "Base de dados completa", 
                "purple"
            )
            
            # Card 2 - População total
            create_card(
                col2, 
                "POPULAÇÃO TOTAL", 
                f"{total_population:,}".replace(",", "."), 
                "👥", 
                "Habitantes em todas as cidades", 
                "green"
            )
            
            # Card 3 - Maior cidade
            create_card(
                col3, 
                "MAIOR CIDADE", 
                max_pop_city, 
                "🌃", 
                f"População: {int(cities_df.iloc[0]['population']):,}".replace(",", "."), 
                "blue"
            )
            
            # Card 4 - Estados cobertos
            create_card(
                col4, 
                "ESTADOS COBERTOS", 
                str(states_count), 
                "🗺️", 
                "De 50 estados americanos", 
                "orange"
            )
            
            # Exibir informações sobre os dados na barra lateral
            st.sidebar.success(f"{len(cities_df)} cidades carregadas com sucesso!")
            st.sidebar.write("**Estatísticas dos Dados**")
            st.sidebar.write(f"• Maior cidade: {cities_df.iloc[0]['city']}, {cities_df.iloc[0]['state']}")
            st.sidebar.write(f"• População total: {cities_df['population'].sum():,} habitantes")
            st.sidebar.write(f"• Cobertura: {len(cities_df['state'].unique())} estados americanos")
            

            # Adicionar gráfico de distribuição populacional na barra lateral
            with st.sidebar.expander("📊 Distribuição populacional"):
                fig, ax = plt.subplots(figsize=(4, 2))
                
                # Usar KDE (Kernel Density Estimation) para mostrar a curva de distribuição
                
                # Remover outliers extremos para melhor visualização
                population_data = cities_df['population']
                q1, q3 = np.percentile(population_data, [25, 75])
                iqr = q3 - q1
                upper_limit = q3 + 5 * iqr  # Limite mais permissivo para manter mais dados
                filtered_data = population_data[population_data <= upper_limit]
                
                # Criar densidade de kernel para visualização da distribuição
                x = np.linspace(0, filtered_data.max(), 1000)
                density = stats.gaussian_kde(filtered_data)
                
                # Plotar a curva de densidade
                ax.plot(x, density(x), 'b-', lw=2, label='Densidade')
                
                # Adicionar histograma suave ao fundo para referência
                ax.hist(filtered_data, bins=20, density=True, alpha=0.3, color='purple')
                
                ax.set_xlabel('População')
                ax.set_ylabel('Densidade')
                ax.set_title('Forma da distribuição populacional')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        city_names = cities_df['city'].tolist()
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {str(e)}")
        st.stop()

    st.markdown("""### 🚏 Origem -> Destino
    """, unsafe_allow_html=True)

    st.write("Selecione as cidades de origem e destino para calcular a rota.")

    # Configurar área de seleção de origem e destino
    col1, col2 = st.columns([1, 1])
    
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
            "San Jose" if "San Jose" in city_names else city_names[1]
        )
        
        # Informações detalhadas sobre a cidade de destino
        cidade_destino = cities_df[cities_df['city'] == end_city].iloc[0]
        st.info(f"""
        **{end_city}, {cidade_destino['state']}**
        - População: {int(cidade_destino['population']):,} habitantes
        - Crescimento (2000-2013): {cidade_destino['growth_from_2000_to_2013']}
        - Posição no ranking: {cidade_destino['rank']}
        """)
    
    # Calcular distância direta entre origem e destino
    dist_direta = algorithms.calculate_distance_from_df(cities_df, start_city, end_city)
    dist_haversine = graph_utils.calculate_haversine_distance(
        cities_df[cities_df['city'] == start_city].iloc[0],
        cities_df[cities_df['city'] == end_city].iloc[0]
    )
    
    st.markdown(f"<div style='text-align: left;'><b>Distância em linha reta entre elas</b>: "
               f"{dist_direta:.2f} graus (aprox. {dist_haversine:.0f} km)</div>", unsafe_allow_html=True)
    
    # Primeiro retângulo - Configurações e algoritmo de busca
    st.markdown("""### ⚙️ Configurações
    """, unsafe_allow_html=True)
    
    # Configurações de desempenho
    with st.expander("🏙️ Quantidade de cidades utilizadas", expanded=False):
        # Função para incrementar/decrementar o número de cidades
        def increment_cities():
            step_value = 50
            if st.session_state.num_cities + step_value <= len(cities_df):
                st.session_state.num_cities += step_value
            else:
                st.session_state.num_cities = len(cities_df)
           
        def decrement_cities():
            step_value = 50
            if st.session_state.num_cities > 50 + step_value:
                st.session_state.num_cities -= step_value
            else:
                st.session_state.num_cities = 50
        
        # Inicializar o valor na session_state se não existir
        if 'num_cities' not in st.session_state:
            st.session_state.num_cities = 300

        numero_cidades = st.slider(
            "Número de cidades a considerar (afeta o desempenho)", 
            min_value=50, 
            max_value=len(cities_df), 
            value=st.session_state.num_cities,
            key="num_cities",
            help="Um número menor de cidades melhora o desempenho do aplicativo"
        )
        
        # Adicionar botões para incrementar/decrementar (centralizados)
        col_buttons = st.columns([1, 1, 1, 1, 1])
        with col_buttons[1]:
            st.button("-50", on_click=decrement_cities, use_container_width=True, key="dec_cities")
        with col_buttons[3]:
            st.button("+50", on_click=increment_cities, use_container_width=True, key="inc_cities")
        st.caption("Ajuste fino do número de cidades", unsafe_allow_html=True)
        
        cities_df = cities_df.head(numero_cidades)
        st.write(f"Usando as {numero_cidades} maiores cidades para os cálculos.")
        
    # Algoritmo de busca
    with st.expander("🔍 Escolha dos Algoritmos de Busca", expanded=True):
        st.markdown("Selecione os algoritmos que você deseja utilizar para encontrar a rota:")
        
        # Inicializar os estados dos checkboxes na session_state se não existirem
        if 'use_bfs' not in st.session_state:
            st.session_state.use_bfs = True
        if 'use_dfs' not in st.session_state:
            st.session_state.use_dfs = False
        if 'use_astar' not in st.session_state:
            st.session_state.use_astar = True
        if 'use_fuzzy' not in st.session_state:
            st.session_state.use_fuzzy = False
        if 'use_dijkstra' not in st.session_state:
            st.session_state.use_dijkstra = True
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.use_bfs = st.checkbox(
                "BFS (Busca em Largura)", 
                value=st.session_state.use_bfs,
                help="Encontra o caminho com menor número de cidades intermediárias"
            )
            st.session_state.use_dfs = st.checkbox(
                "DFS (Busca em Profundidade)", 
                value=st.session_state.use_dfs,
                help="Busca em profundidade otimizada para encontrar caminhos curtos"
            )
            st.session_state.use_astar = st.checkbox(
                "A* (A-Estrela)", 
                value=st.session_state.use_astar,
                help="Encontra o caminho mais curto em termos de distância"
            )
        
        with col2:
            st.session_state.use_fuzzy = st.checkbox(
                "Busca Fuzzy", 
                value=st.session_state.use_fuzzy,
                help="Lida com incertezas nas conexões e pode encontrar rotas alternativas"
            )
            st.session_state.use_dijkstra = st.checkbox(
                "Dijkstra (Menor Distância)", 
                value=st.session_state.use_dijkstra,
                help="Encontra o caminho de menor distância preferindo cidades menos populosas em caso de empate"
            )
            
        # Botão para selecionar todos
        if st.button("Selecionar Todos"):
            st.session_state.use_bfs = True
            st.session_state.use_dfs = True
            st.session_state.use_astar = True
            st.session_state.use_fuzzy = True
            st.session_state.use_dijkstra = True
            st.rerun()
        
        # Construir a string do algoritmo baseado nas seleções
        selected_algos = []
        if st.session_state.use_bfs:
            selected_algos.append("BFS")
        if st.session_state.use_dfs:
            selected_algos.append("DFS")
        if st.session_state.use_astar:
            selected_algos.append("A*")
        if st.session_state.use_fuzzy:
            selected_algos.append("Fuzzy")
        if st.session_state.use_dijkstra:
            selected_algos.append("Dijkstra")
        
        if len(selected_algos) == 5:
            algorithm_choice = "Todos"
        elif len(selected_algos) == 0:
            st.warning("Por favor, selecione pelo menos um algoritmo")
            algorithm_choice = None
        else:
            algorithm_choice = selected_algos[0] if len(selected_algos) == 1 else "Todos"
            # Mostrar quais algoritmos serão executados
            st.success(f"Algoritmos selecionados: {', '.join(selected_algos)}")
    
    # Valor de raio recomendado
    with st.expander("🔍 Recomendação de valores para raio (r) ou distância (d)", expanded=False):
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
    
    # Explicação da relação entre quilômetros e graus
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

    # Cálculo do raio máximo teórico (movido para antes do uso)
    max_latitudes = cities_df['latitude'].max() - cities_df['latitude'].min()
    max_longitudes = cities_df['longitude'].max() - cities_df['longitude'].min()
    max_theoretical_r = ((max_latitudes**2) + (max_longitudes**2))**0.5
    max_theoretical_km = max_theoretical_r * 111  # Aproximação usando 111km por grau

    # Adicionar expander para as configurações de conexão entre cidades
    with st.expander("🔄 Configurações de conexão entre cidades", expanded=True):
       # Adicionar opção para escolher o tipo de conexão
       connection_type = st.radio(
          "Tipo de conexão",
          ["Raio em graus (r)", "Distância em km (d)", "Ambos"],
          index=2,  # Default is now "Ambos" (index 2)
          help="Escolha o tipo de restrição para conexões entre cidades. Quando 'Ambos' está selecionado, o grafo é construído considerando as duas restrições simultaneamente: uma conexão é estabelecida entre duas cidades apenas quando a distância entre elas satisfaz TANTO o limite de raio em graus QUANTO o limite de distância em km. Por exemplo, com raio=1° e distância=400km, duas cidades só estarão conectadas se estiverem dentro de 1° E também a menos de 400km uma da outra."
       )
       
       # Inicializar variáveis de estado para o link entre sliders se não existir
       if 'link_sliders' not in st.session_state:
          st.session_state.link_sliders = True
          
       # Checkbox para controlar a trava entre os sliders
       link_sliders = st.checkbox(
          "Sincronizar sliders (raio e distância equivalentes)", 
          value=st.session_state.link_sliders,
          help="Quando marcado, o slider de distância em km será automaticamente atualizado para corresponder ao valor do raio em graus (1° ≈ 111 km)."
       )
       st.session_state.link_sliders = link_sliders
       
       # Configuração baseada no tipo de conexão
       col1, col2 = st.columns(2)
       
       # Função para atualizar o valor de d quando r muda (se link estiver ativado)
       def update_d_from_r():
          if st.session_state.link_sliders and 'r_value' in st.session_state:
             st.session_state.d_value = st.session_state.r_value * 111
       
       # Função para atualizar o valor de r quando d muda (se link estiver ativado)
       def update_r_from_d():
          if st.session_state.link_sliders and 'd_value' in st.session_state:
             st.session_state.r_value = st.session_state.d_value / 111
       
       # Funções para incrementar/decrementar os valores
       def increment_r():
           step_value = 0.1
           st.session_state.r_value += step_value
           update_d_from_r()
           
       def decrement_r():
           step_value = 0.1
           # Não permitir valores negativos ou abaixo de 1.0
           if st.session_state.r_value > 1.0 + step_value:
               st.session_state.r_value -= step_value
               update_d_from_r()
           
       def increment_d():
           step_value = 50.0
           st.session_state.d_value += step_value
           update_r_from_d()
           
       def decrement_d():
           step_value = 50.0
           # Não permitir valores negativos ou abaixo de 100.0
           if st.session_state.d_value > 100.0 + step_value:
               st.session_state.d_value -= step_value
               update_r_from_d()
       
       with col1:
          if connection_type in ["Raio em graus (r)", "Ambos"]:
             # Valor sugerido para o raio (1/3 da distância direta, mas no mínimo 1.0)
             suggested_r = max(1.0, min(5.0, dist_direta / 3))
             
             # Inicializar o valor na session_state se não existir
             if 'r_value' not in st.session_state:
                st.session_state.r_value = suggested_r
             
             r = st.slider(
                "Raio de conexão (r)", 
                min_value=1.0, 
                max_value=float(max_theoretical_r),
                value=st.session_state.r_value,
                step=0.1,
                key="r_value",
                on_change=update_d_from_r,
                help=f"""Define a distância máxima em graus para conexão direta entre cidades.

                    Valores recomendados:
                    • r < 1° (até ~111 km): Apenas cidades muito próximas
                    • 1° ≤ r ≤ 5° (~111-555 km): Cidades regionalmente próximas
                    • 5° < r ≤ 10° (~555-1110 km): Cidades em estados vizinhos
                    • 10° < r ≤ 20° (~1110-2220 km): Conexões de longa distância
                    • r > 20°: Não recomendado - conexões entre cidades muito distantes

                    O valor máximo teórico é {max_theoretical_r:.1f} graus, que corresponde à maior distância possível 
                    entre quaisquer duas cidades no conjunto de dados. No entanto, valores acima de 20° podem resultar 
                    em caminhos diretos irrealistas entre cidades muito distantes.
                    
                    💡 Dica: Um bom valor inicial é aproximadamente 1/3 da distância em linha reta entre origem e destino."""
             )
             
             # Converter para km para referência
             r_in_km = r * 111
             st.caption(f"Raio selecionado: {r:.1f}° ≈ {r_in_km:.0f} km")
             
             # Adicionar botões para incrementar/decrementar (centralizados)
             col_buttons = st.columns([1, 1, 1, 1, 1])
             with col_buttons[1]:
                 st.button("-0.1°", on_click=decrement_r, use_container_width=True, key="dec_r")
             with col_buttons[3]:
                 st.button("+0.1°", on_click=increment_r, use_container_width=True, key="inc_r")
             st.caption("Ajuste fino do raio", unsafe_allow_html=True)
          else:
             r = None
             
       with col2:
          if connection_type in ["Distância em km (d)", "Ambos"]:
             # Converter valor em graus para km para um valor padrão inicial
             default_d_value = max(100.0, min(333.0, dist_haversine / 3))
             
             # Inicializar o valor na session_state se não existir
             if 'd_value' not in st.session_state:
                st.session_state.d_value = default_d_value
                
             # Se os sliders estiverem sincronizados, usar o valor de r convertido
             if st.session_state.link_sliders and 'r_value' in st.session_state and connection_type == "Ambos":
                st.session_state.d_value = st.session_state.r_value * 111
             
             d = st.slider(
                "Distância máxima em km (d)", 
                min_value=100.0, 
                max_value=float(max_theoretical_km),
                value=st.session_state.d_value,
                step=50.0,
                key="d_value",
                on_change=update_r_from_d,
                disabled=st.session_state.link_sliders and connection_type == "Ambos",
                help=f"""Define a distância máxima em quilômetros para conexão direta entre cidades.

                    Valores recomendados:
                    • d < 100 km: Apenas cidades muito próximas (mesma região metropolitana)
                    • 100 ≤ d ≤ 500 km: Cidades na mesma região
                    • 500 < d ≤ 1000 km: Cidades em estados vizinhos
                    • 1000 < d ≤ 2000 km: Conexões de longa distância
                    • d > 2000 km: Não recomendado - conexões entre cidades muito distantes

                    O valor máximo teórico é {max_theoretical_km:.0f} km, que corresponde à maior distância possível 
                    entre quaisquer duas cidades no conjunto de dados. No entanto, valores acima de 2000 km podem resultar 
                    em caminhos diretos irrealistas entre cidades muito distantes.
                    
                    💡 Dica: Um bom valor inicial é aproximadamente 1/3 da distância em linha reta entre origem e destino."""
             )
             
             # Adicionar botões para incrementar/decrementar se o slider estiver ativado
             if not (st.session_state.link_sliders and connection_type == "Ambos"):
                 col_buttons = st.columns([1, 1, 1, 1, 1])
                 with col_buttons[1]:
                     st.button("-50km", on_click=decrement_d, use_container_width=True, key="dec_d")
                 with col_buttons[3]:
                     st.button("+50km", on_click=increment_d, use_container_width=True, key="inc_d")
                 st.caption("Ajuste fino da distância", unsafe_allow_html=True)
             
             # Adicionar nota explicativa quando o slider estiver desativado
             if st.session_state.link_sliders and connection_type == "Ambos":
                st.caption("⚠️ Slider desativado porque a sincronização está ativa. Ajuste o raio para alterar a distância.")
    # Adicionar botão para procurar rota
    col_button = st.columns(3)
    with col_button[1]:
        search_route = st.button(
            "🔍 Procurar Rota",
            help="Clique para encontrar a melhor rota entre as cidades selecionadas",
            use_container_width=True,
            type="primary"
        )
    
    # Lógica para processar a busca quando o botão for clicado
    if search_route:
        # Iniciar o temporizador para medir o tempo de processamento
        start_time = time.time()
        
        # Mostrar barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Criando grafo de conectividade...")
            
            # Atualizar barra de progresso
            progress_bar.progress(10)
            
            # Construir grafo baseado no tipo de conexão selecionado
            if connection_type == "Raio em graus (r)":
                G = graph_utils.build_graph(cities_df, r=r, name_to_id=name_to_id, id_to_name=id_to_name)
                connection_parameter = r
                connection_unit = "graus"
            elif connection_type == "Distância em km (d)":
                d_km = d  # Já está em km
                G = graph_utils.build_graph(cities_df, d=d_km, name_to_id=name_to_id, id_to_name=id_to_name)
                connection_parameter = d_km
                connection_unit = "km"
            else:  # Ambos
                G = graph_utils.build_graph(cities_df, r=r, d=d, name_to_id=name_to_id, id_to_name=id_to_name)
                connection_parameter = f"{r} graus / {d} km"
                connection_unit = "mistos"
            
            # Verificar se as cidades estão no grafo
            start_city_id = name_to_id.get(start_city)
            end_city_id = name_to_id.get(end_city)
            
            if start_city_id is None or end_city_id is None or start_city_id not in G.nodes or end_city_id not in G.nodes:
                error_msg = "Uma ou ambas as cidades selecionadas não estão no grafo. "
                if start_city_id is None or start_city_id not in G.nodes:
                    error_msg += f"'{start_city}' está isolada. "
                if end_city_id is None or end_city_id not in G.nodes:
                    error_msg += f"'{end_city}' está isolada. "
                error_msg += f"Tente aumentar o valor do raio de conexão para incluir mais cidades."
                st.error(error_msg)
                progress_bar.progress(100)
                return
            
            # Atualizar barra de progresso
            progress_bar.progress(30)
            status_text.text("Verificando conectividade...")
            
            # Verificar se existe um caminho entre as cidades
            if not nx.has_path(G, start_city_id, end_city_id):
                st.warning(f"Não existe caminho entre {start_city} e {end_city} com o raio de conexão atual ({connection_parameter} {connection_unit}). Tente aumentar o valor do raio.")
                
                # Sugerir um valor de r adequado
                components = list(nx.connected_components(G))
                start_component = None
                end_component = None
                
                for i, comp in enumerate(components):
                    if start_city_id in comp:
                        start_component = i
                    if end_city_id in comp:
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
                
                progress_bar.progress(100)
                return
            
            # Atualizar barra de progresso
            progress_bar.progress(50)
            status_text.text("Executando algoritmos de busca...")
            
            # Execução dos algoritmos selecionados
            results = {}
            
            # Converter nomes de cidades para IDs para usar nos algoritmos
            start_id = name_to_id.get(start_city)
            end_id = name_to_id.get(end_city)
            
            # Helper para converter caminhos de IDs para nomes
            def convert_path_to_names(path_ids):
                return [id_to_name.get(node_id, f"ID:{node_id}") for node_id in path_ids]
            
            # Usar diretamente os checkboxes da session_state para determinar quais algoritmos executar
            if st.session_state.use_bfs:
                status_text.text("Executando BFS...")
                bfs_result = algorithms.bfs_search(G, cities_df, start_id, end_id)
                if bfs_result and len(bfs_result) >= 2:
                    # Substituir IDs por nomes no caminho retornado
                    path_ids = bfs_result[0]
                    path_names = convert_path_to_names(path_ids)
                    # Criar novo resultado com nomes em vez de IDs
                    results["BFS"] = (path_names,) + bfs_result[1:]
                
            if st.session_state.use_dfs:
                status_text.text("Executando DFS...")
                dfs_result = algorithms.dfs_search(G, cities_df, start_id, end_id)
                if dfs_result and len(dfs_result) >= 2:
                    path_ids = dfs_result[0]
                    path_names = convert_path_to_names(path_ids)
                    results["DFS"] = (path_names,) + dfs_result[1:]
                
            if st.session_state.use_astar:
                status_text.text("Executando A*...")
                a_star_result = algorithms.a_star_search(G, cities_df, start_id, end_id)
                if a_star_result and len(a_star_result) >= 2:
                    path_ids = a_star_result[0]
                    path_names = convert_path_to_names(path_ids)
                    results["A*"] = (path_names,) + a_star_result[1:]
                
            if st.session_state.use_fuzzy:
                status_text.text("Executando Busca Fuzzy...")
                fuzzy_result = algorithms.fuzzy_search(G, cities_df, start_id, end_id)
                if fuzzy_result and len(fuzzy_result) >= 2:
                    path_ids = fuzzy_result[0]
                    path_names = convert_path_to_names(path_ids)
                    results["Fuzzy"] = (path_names,) + fuzzy_result[1:]
                
            if st.session_state.use_dijkstra:
                status_text.text("Executando Dijkstra...")
                dijkstra_result = algorithms.dijkstra_search(G, cities_df, start_id, end_id)
                if dijkstra_result and len(dijkstra_result) >= 2:
                    path_ids = dijkstra_result[0]
                    path_names = convert_path_to_names(path_ids)
                    results["Dijkstra"] = (path_names,) + dijkstra_result[1:]
            
            # Verificar se algum algoritmo conseguiu encontrar um caminho
            if not results:
                st.warning("Nenhum dos algoritmos conseguiu encontrar um caminho válido entre as cidades selecionadas. Tente aumentar o raio de conexão.")
                progress_bar.progress(100)
                return
            
            # Atualizar barra de progresso
            progress_bar.progress(80)
            status_text.text("Gerando visualização...")
            
            # Calcular tempo de processamento
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Atualizar a barra de progresso e remover mensagem de status
            progress_bar.progress(100)
            status_text.empty()
            
            # Verificação adicional para garantir que os resultados tenham os valores esperados
            for algo, resultado in list(results.items()):
                if not isinstance(resultado, tuple) or len(resultado) < 2:
                    st.warning(f"O algoritmo {algo} retornou um resultado em formato inválido. Este algoritmo será ignorado.")
                    del results[algo]
                    
            if not results:
                st.warning("Nenhum algoritmo conseguiu encontrar um caminho válido após validação dos resultados.")
                return
            
            # Passar os parâmetros r e d apenas se estiverem definidos
            d_param = d if connection_type in ["Distância em km (d)", "Ambos"] else None
            r_param = r if connection_type in ["Raio em graus (r)", "Ambos"] else None
            
            fig = map_display.display_graph_visualization(G, cities_df, r=r_param, d=d_param)

                
            # --- SEÇÃO DE COMPARAÇÃO VISUAL ENTRE ALGORITMOS ---
            st.markdown("""
            <div style="border-top: 1px solid rgba(49, 51, 63, 0.2); margin: 1em 0;"></div>
            <h2 style="text-align: center; margin-bottom: 1em;">🔍 Resultados</h2>
            """, unsafe_allow_html=True)
            
            # Mostrar mapa comparativo com todas as rotas e grafo lado a lado          
            # Usar colunas para colocar o mapa e o grafo lado a lado
            col_map, col_graph = st.columns(2)
            
            with col_map:
                st.markdown("#### Mapa de Rotas")
                st.markdown("As rotas estão representadas em cores diferentes: BFS (azul), DFS (roxo), A* (verde), Fuzzy (vermelho) e Dijkstra (laranja).")
                map_container = map_display.display_all_routes_map(cities_df, results)
                st.caption("**Dica**: Utilize o controle de camadas no canto superior direito para exibir/ocultar rotas e cidades.")
                
            with col_graph:
                st.markdown("#### Visualização do Grafo")
                st.markdown("A imagem abaixo mostra a rede de conexões entre cidades. **Nós**: Representam cidades - "
                "**Arestas**: Representam conexões diretas possíveis - **Tamanho dos nós**: Proporcional à população da cidade")
                # Define figure size to match the map dimensions (using the same height/width ratio)
                graph_fig = map_display.display_graph_visualization(
                    G, 
                    cities_df, 
                    r if connection_type in ["Raio em graus (r)", "Ambos"] else None,
                    d if connection_type in ["Distância em km (d)", "Ambos"] else None
                )
                st.pyplot(graph_fig)
                               
                st.markdown(f"""
                - Número de cidades (nós): {len(G.nodes())}
                - Número de conexões (arestas): {len(G.edges())}
                - Densidade da rede: {nx.density(G):.4f}
                """)
                
            # --- SEÇÃO DE ESTATÍSTICAS COMPARATIVAS ---
            st.subheader("Comparação dos Resultados")
            
            # Coletar dados para tabela comparativa
            comparison_data = []
            for algo, resultado in results.items():
                path = resultado[0]
                distance = resultado[1]
                # Verificar se temos dados de tempo de execução (3º elemento)
                elapsed_time = resultado[2] if len(resultado) > 2 else 0.0
                
                # Para o Fuzzy, verificar se temos dados de certeza (4º elemento)
                certainty = ""
                if algo == "Fuzzy" and len(resultado) > 3:
                    certainty = f"{resultado[3]*100:.1f}%"
                
                # Calcular a eficiência correta: ((distância em linha reta / distância real) * 100 )
                # Valores mais próximos de 100% são melhores (rota mais direta)
                km_distance = distance * 111
                efficiency = (dist_haversine / km_distance) * 100 if km_distance > 0 else 0
                
                # A eficiência deve ser naturalmente <= 100% porque a distância em linha reta
                # é sempre menor ou igual à distância real do caminho
                # Nenhuma limitação artificial é necessária aqui
                
                # Calcular população total da rota
                total_population = 0
                for city in path:
                    city_data = cities_df[cities_df['city'] == city]
                    if not city_data.empty:
                        total_population += int(city_data.iloc[0]['population'])
                
                comparison_data.append({
                    "Algoritmo": algo,
                    "Distância": f"{distance:.2f}°",
                    "Distância (km)": f"{distance*111:.0f} km",
                    "Cidades": len(path),
                    "Cidades intermediárias": len(path) - 2 if len(path) >= 2 else 0,
                    "Eficiência": f"{efficiency:.2f}%",
                    "População Total": f"{total_population:,}".replace(",", "."),
                    "Tempo de execução": f"{elapsed_time:.2f} ms",
                    "Certeza (Fuzzy)": certainty
                })
            
            # Mostrar tabela comparativa
            st.table(pd.DataFrame(comparison_data))

                        # Adicionar um expander para explicar o que é eficiência
            with st.expander("ℹ️ Entendendo a medida de Eficiência"):
                st.markdown("""
                ### Medida de Eficiência das Rotas
             
                A **eficiência** de uma rota é calculada como a proporção entre:
                
                ```
                Eficiência = (Distância em linha reta / Distância real da rota) × 100%
                ```
                
                #### Interpretação:
                - **100%**: Rota perfeitamente eficiente (segue a linha reta ideal)
                - **50%**: A rota é duas vezes mais longa que a linha reta
                - **25%**: A rota é quatro vezes mais longa que a linha reta
                
                Valores mais altos indicam rotas mais eficientes que se aproximam da distância ideal em linha reta.
                
                A distância em linha reta é calculada usando a fórmula de Haversine, que considera a curvatura da Terra.
                """)
            
            
            # --- VISUALIZAÇÕES GRÁFICAS COMPARATIVAS ---
            st.subheader("Comparação Visual")
            
            # Criar gráficos comparativos (2x2 layout)
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de distâncias
                fig_dist = plt.figure(figsize=(4, 3))
                algos = [data["Algoritmo"] for data in comparison_data]
                distances = [float(data["Distância"].replace("°", "")) * 111 for data in comparison_data]
                
                plt.bar(algos, distances, color=['blue', 'purple', 'green', 'red', 'orange'])
                plt.ylabel("Distância (km)")
                plt.title("Comparação de Distância Total")
                plt.xticks(rotation=45)
                
                for i, d in enumerate(distances):
                    plt.text(i, d + 50, f"{d:.0f} km", ha='center')
                    
                plt.tight_layout()
                st.pyplot(fig_dist)
                
                # Gráfico de tempo de execução
                fig_time = plt.figure(figsize=(4, 3))
                times = [float(data["Tempo de execução"].replace(" ms", "")) for data in comparison_data]
                
                plt.bar(algos, times, color=['blue', 'purple', 'green', 'red', 'orange'])
                plt.ylabel("Tempo (ms)")
                plt.title("Tempo de execução por algoritmo")
                plt.xticks(rotation=45)
                
                for i, t in enumerate(times):
                    plt.text(i, t + 0.05, f"{t:.2f} ms", ha='center')
                    
                plt.tight_layout()
                st.pyplot(fig_time)
            
            with col2:
                # Gráfico de número de cidades
                fig_cities = plt.figure(figsize=(4, 3))
                city_counts = [data["Cidades"] for data in comparison_data]
                
                plt.bar(algos, city_counts, color=['blue', 'purple', 'green', 'red', 'orange'])
                plt.ylabel("Número de cidades")
                plt.title("Comparação de número de cidades")
                plt.xticks(rotation=45)
                
                for i, c in enumerate(city_counts):
                    plt.text(i, c + 0.3, str(c), ha='center')
                    
                plt.tight_layout()
                st.pyplot(fig_cities)
                
                # NOVO: Gráfico de população total por rota
                fig_pop = plt.figure(figsize=(4, 3))
                populations = [int(data["População Total"].replace(".", "")) / 1000000 for data in comparison_data]
                
                plt.bar(algos, populations, color=['blue', 'purple', 'green', 'red', 'orange'])
                plt.ylabel("População (milhões)")
                plt.title("População total das cidades por rota")
                plt.xticks(rotation=45)
                
                for i, p in enumerate(populations):
                    plt.text(i, p + 0.2, f"{p:.1f}M", ha='center')
                    
                plt.tight_layout()
                st.pyplot(fig_pop)
            
            # Identificar algoritmo mais rápido e mais lento
            if times:
                min_time_idx = times.index(min(times))
                max_time_idx = times.index(max(times))
                min_algo = algos[min_time_idx]
                max_algo = algos[max_time_idx]
                
                st.info(f"O algoritmo {min_algo} foi o mais rápido ({times[min_time_idx]:.2f} ms).")
                st.info(f"O algoritmo {max_algo} foi o mais lento ({times[max_time_idx]:.2f} ms).")
            
            # --- SEÇÃO DE RESULTADOS DETALHADOS ---
            st.markdown("""
            <div style="border-top: 1px solid rgba(49, 51, 63, 0.2); margin: 1em 0;"></div>
            <h2 style="text-align: center; margin-bottom: 1em;">🛣️ Detalhes das Rotas</h2>
            """, unsafe_allow_html=True)
            
            # Exibir resultados em abas
            tabs = st.tabs([f"{algo} ({len(resultado[0])} cidades)" for algo, resultado in results.items()])
            
            for i, (algo, resultado) in enumerate(results.items()):
                # Extrair os valores do resultado
                path = resultado[0]  # O caminho é sempre o primeiro elemento
                distance = resultado[1]  # A distância é sempre o segundo elemento
                
                with tabs[i]:
                    st.subheader(f"Rota encontrada usando {algo}")
                    
                    # Detalhes da rota
                    distance_km = distance * 111 if distance else 0  # Conversão aproximada para km
                    # Calcular a eficiência correta com a mesma lógica da tabela comparativa
                    km_distance = distance * 111
                    efficiency = (dist_haversine / km_distance) * 100 if km_distance > 0 else 0
                    efficiency = min(100, efficiency)  # Limitar a 100% para evitar valores irrealistas
                    
                    # Adicionar informações de certeza para a busca fuzzy
                    additional_info = ""
                    if algo == "Fuzzy" and len(resultado) > 3:
                        certainty = resultado[3]
                        additional_info = f'<div class="result-item"><span class="result-label">Certeza da rota</span><span class="result-value">{certainty*100:.1f}%</span></div>'
                    
                    st.markdown(f"""
                    <div class="result-summary">
                        <div class="result-item">
                            <span class="result-label">Cidades visitadas</span>
                            <span class="result-value">{len(path)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Distância total</span>
                            <span class="result-value">{distance:.2f}° ({distance_km:.0f} km)</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Eficiência</span>
                            <span class="result-value">{efficiency:.2f}% da linha reta</span>
                        </div>
                        {additional_info}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Layout de duas colunas para a lista de cidades e o mapa
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Lista de cidades no caminho
                        st.markdown("##### Cidades no caminho")
                        cities_in_path = []
                        for city in path:
                            city_info = cities_df[cities_df['city'] == city].iloc[0]
                            cities_in_path.append({
                                "Cidade": f"{city}, {city_info['state']}",
                                "População": int(city_info['population']),
                                "Ranking": city_info['rank']
                            })
                        
                        st.table(pd.DataFrame(cities_in_path))
                    
                    with col2:
                        # Mapa da rota - agora ocupa toda a largura da coluna
                        st.markdown("##### Visualização da rota no mapa")
                        route_map = map_display.display_path_on_map(cities_df, path, f"Rota encontrada usando {algo}")
                        # O mapa já é renderizado na função display_path_on_map
            
            # Salvar resultados no histórico da sessão
            history_entry = {
                'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'start_city': start_city,
                'end_city': end_city,
                'connection_type': connection_type,
                'connection_parameter': connection_parameter,
                'connection_unit': connection_unit,
                'algorithms': {}
            }
            
            for algo, resultado in results.items():
                path = resultado[0]
                distance = resultado[1]
                
                # Verificar se temos dados de tempo de execução (3º elemento)
                elapsed_time = resultado[2] if len(resultado) > 2 else 0.0
                
                # Para o Fuzzy, verificar se temos dados de certeza (4º elemento)
                certainty = None
                if algo == "Fuzzy" and len(resultado) > 3:
                    certainty = resultado[3]
                
                history_entry['algorithms'][algo] = {
                    'path': path,
                    'distance_degrees': distance,
                    'distance_km': distance * 111,
                    'cities_count': len(path),
                    'elapsed_time': elapsed_time,
                    'certainty': certainty
                }
            
            # Adicionar ao histórico da sessão
            st.session_state.search_history.append(history_entry)
            
            # Mostrar histórico de buscas
            with st.expander("📜 Histórico de Buscas", expanded=False):                
                # Mostrar apenas as últimas 5 buscas (excluindo a atual)
                if len(st.session_state.search_history) > 1:
                    history = st.session_state.search_history[:-1]  # Excluir a busca atual
                    history.reverse()  # Mais recentes primeiro
                    
                    for i, search in enumerate(history[:5]):  # Mostrar apenas as 5 mais recentes
                        st.markdown(f"#### Busca {i+1}: {search['start_city']} → {search['end_city']} ({search['timestamp']})")
                        st.write(f"**Tipo de conexão**: {search['connection_type']}")
                        st.write(f"**Parâmetro de conexão**: {search['connection_parameter']} {search['connection_unit']}")
                        
                        # Mostrar resultados resumidos para cada algoritmo
                        for alg_name, alg_results in search['algorithms'].items():
                            st.write(f"**{alg_name}**: {alg_results['distance_km']:.0f} km, {alg_results['cities_count']} cidades")
                            if alg_results['certainty'] is not None:
                                st.write(f"Certeza: {alg_results['certainty']:.2f}")
                        
                        # Adicionar uma linha divisória entre as buscas
                        if i < min(4, len(history[:5])-1):  # Não adicionar após o último item
                            st.markdown("---")
                else:
                    st.info("Nenhuma busca anterior registrada.")
            
        except Exception as e:
            st.error(f"Erro ao processar a rota: {str(e)}")
            import traceback

            st.error(traceback.format_exc())
            progress_bar.progress(100)