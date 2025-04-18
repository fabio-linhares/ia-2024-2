import streamlit as st

# Forçar o tema escuro, independente das configurações do sistema
st.set_page_config(
    page_title="City Router - UFAL",
    page_icon=":cityscape:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "City Router - Projeto de Avaliação B1 da Disciplina de nteligência Artificial - PPGI-UFAL"
    }
)

# Forçar tema escuro via CSS
force_dark_theme = """
<style>
:root {color-scheme: dark;}
html, body, [class*="css"] {
    color: white !important;
    background-color: #0e1117 !important;
}

/* Forçar classe 'dark' no corpo do documento */
body {
    color-scheme: dark;
    -webkit-font-smoothing: antialiased;
}

/* Garantir que elementos dentro de iframes também tenham tema escuro */
iframe {
    color-scheme: dark;
}

/* Fundo uniforme sem gradiente */
.stApp {
    background: #171C28 !important;
}

/* Remover qualquer barra de gradiente no topo da página */
header {
    background: none !important;
}

/* Garantir que não haja elementos visuais indesejados no topo */
.main > div:first-child {
    background: none !important;
}

/* Remover elementos decorativos potencialmente sobrepostos */
[data-testid="stDecoration"] {
    display: none !important;
}

</style>
"""
st.markdown(force_dark_theme, unsafe_allow_html=True)

import os
import base64
import json
import pandas as pd
from io import StringIO
from io import BytesIO  # Para lidar com arquivos carregados
import shutil  # Para operações de arquivos
from pathlib import Path  # Para manipulação de caminhos
from app.pages.main_app import app as main_app
from app.pages.about import app as about_app
from app.pages.report_page import app as report_app
from app.pages.haversine_page import app as haversine_app
from app.pages.algorithms import (
    astar_page, bfs_page, dfs_page, dijkstra_page, fuzzy_page
)

# Inicialização do estado da sessão para o tema (sempre escuro)
st.session_state.theme = "dark"

# Funções para verificar e carregar o arquivo de cidades
def check_cities_file():
    """Verifica se o arquivo cities.json existe e está formatado corretamente."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "cities.json")
    
    if not os.path.exists(json_path):
        return False, "Arquivo cities.json não encontrado na pasta data."
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list) or len(data) == 0:
                return False, "Arquivo cities.json existe, mas o formato é inválido (deve ser uma lista)."
            
            # Verificar se tem os campos necessários
            required_fields = ['city', 'state', 'latitude', 'longitude', 'population']
            if not all(field in data[0] for field in required_fields):
                return False, "Arquivo cities.json existe, mas faltam campos obrigatórios."
                
        return True, "Arquivo cities.json encontrado e válido."
    except json.JSONDecodeError:
        return False, "Arquivo cities.json existe, mas contém JSON inválido."
    except Exception as e:
        return False, f"Erro ao verificar o arquivo cities.json: {str(e)}"

def save_uploaded_cities_file(uploaded_file):
    """Salva o arquivo cities.json carregado pelo usuário."""
    try:
        # Verificar se o arquivo é um JSON válido
        try:
            content = uploaded_file.getvalue().decode("utf-8")
            data = json.loads(content)
            
            # Verificar se é uma lista e tem os campos necessários
            if not isinstance(data, list) or len(data) == 0:
                return False, "O arquivo carregado não contém uma lista válida de cidades."
            
            required_fields = ['city', 'state', 'latitude', 'longitude', 'population']
            if not all(field in data[0] for field in required_fields):
                return False, "O arquivo carregado não contém todos os campos obrigatórios."
        except json.JSONDecodeError:
            return False, "O arquivo carregado não é um JSON válido."
        
        # Salvar o arquivo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "cities.json")
        
        # Fazer backup do arquivo atual se existir
        if os.path.exists(json_path):
            backup_path = os.path.join(base_dir, "data", "cities.json.bak")
            shutil.copy2(json_path, backup_path)
        
        # Salvar o novo arquivo
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Resetar qualquer cache ou dados em cache na sessão
        if 'data_loaded' in st.session_state:
            del st.session_state.data_loaded
        
        return True, "Arquivo cities.json carregado com sucesso! A página será atualizada."
    except Exception as e:
        return False, f"Erro ao salvar o arquivo: {str(e)}"

# Exibir mensagem de sucesso ou erro
def show_file_status_message(status, message):
    """Exibe uma mensagem de sucesso ou erro com base no status."""
    if status:
        st.success(message)
    else:
        st.error(message)
        # Adicionar explicação sobre o formato esperado
        st.info("""
        O arquivo cities.json deve seguir este formato:
        ```json
        [
          {
            "city": "New York",
            "state": "New York",
            "population": 8175133,
            "latitude": 40.6643,
            "longitude": -73.9385,
            "growth_from_2000_to_2013": "4.8%",
            "rank": 1
          },
          ...
        ]
        ```
        """)

# Função para alternar o tema
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()  # Forçar recarregamento da página

# Ocultar apenas o rodapé e controles desnecessários
hide_streamlit_elements = """
<style>
footer {visibility: hidden;}
div[data-testid="collapsedControl"] {display: none;}
/* Oculta o menu de páginas à esquerda */
section[data-testid="stSidebar"] > div:first-child {
    background-color: transparent;
    width: auto !important;
}
.sidebar-content {
    padding: 1rem;
    width: 100%;
}
div.sidebar-content > div:first-child {
    width: 100% !important;
}
/* Oculta o seletor de páginas */
[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_streamlit_elements, unsafe_allow_html=True)

# Agora podemos importar outros módulos que podem usar comandos Streamlit
from streamlit_option_menu import option_menu

# Função para carregar imagens como base64 para incorporar no HTML
def get_image_as_base64(path):
    if not os.path.exists(path):
        return None
    
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded

# Tentar carregar logos
logos = {
    "ufal": get_image_as_base64("data/logos/ufal.png"),
    "ic": get_image_as_base64("data/logos/ic.png"),
    "ppgi": get_image_as_base64("data/logos/ppgi.png")
}

# Carregar CSS personalizado
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("app/styles/custom.css")

# Inicialização do estado da sessão para histórico de buscas (se não existir)
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Menu de navegação na barra lateral
with st.sidebar:
    # Inicializar o estado para os menus suspensos
    if 'show_info' not in st.session_state:
        st.session_state.show_info = False
    if 'show_config' not in st.session_state:
        st.session_state.show_config = False
    
    # Logo da UFAL ampliado e centralizado
    if logos["ufal"]:
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-bottom: 35px; width: 100%;">
            <img src="data:image/png;base64,{logos["ufal"]}" style="width: 100%; max-height: 308px; object-fit: contain;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="height: 338px; width: 100%; margin: 0 auto; display: flex; align-items: center; justify-content: center; 
                    background-color: #2D3748; border-radius: 5px; margin-bottom: 35px;">
            <span style="font-size: 42px;">UFAL</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Logos IC e PPGI lado a lado com distância reduzida
    col1, col2 = st.columns([1, 1], gap="small")
    
    # Estilo de container para aproximar os logos
    st.markdown("""
    <style>
    .logo-container {
        margin: 0 -7px; /* Margem negativa para aproximar mais */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # IC à esquerda
    with col1:
        if logos["ic"]:
            st.markdown(f"""
            <div class="logo-container" style="display: flex; justify-content: flex-end; padding-right: 0px;">
                <img src="data:image/png;base64,{logos["ic"]}" style="width: 95%; height: 95px; object-fit: contain;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="logo-container" style="height: 95px; width: 95%; margin-right: 0px; float: right; display: flex; align-items: center; 
                        justify-content: center; background-color: #2D3748; border-radius: 0px;">
                <span>IC</span>
            </div>
            """, unsafe_allow_html=True)
    
    # PPGI à direita
    with col2:
        if logos["ppgi"]:
            st.markdown(f"""
            <div class="logo-container" style="display: flex; justify-content: flex-start; padding-left: 0px;">
                <img src="data:image/png;base64,{logos["ppgi"]}" style="width: 95%; height: 95px; object-fit: contain;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="logo-container" style="height: 75px; width: 75%; margin-left: 0px; float: left; display: flex; align-items: center;
                        justify-content: center; background-color: #2D3748; border-radius: 0px;">
                <span>PPGI</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Espaço antes do menu de configurações
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Menu suspenso para configurações rápidas
    with st.expander("⚙️ Configurações Rápidas", expanded=st.session_state.show_config):
        st.markdown("#### 📁 Arquivo de Dados")
        
        # Verificar o arquivo de cidades
        if 'cities_file_status' not in st.session_state:
            st.session_state.cities_file_status = check_cities_file()
        
        status, message = st.session_state.cities_file_status
        if status:
            st.success(f"✅ {message}")
            
            # Opção para substituir o arquivo
            st.markdown("##### 🔄 Substituir arquivo de cidades:")
        else:
            st.error(f"❌ {message}")
            st.markdown("##### 📤 Carregar arquivo de cidades:")
            
        # Upload de arquivo com descrição clara
        st.markdown("""
        <small>O arquivo deve conter uma lista de cidades com suas coordenadas geográficas e dados populacionais.</small>
        
        <div class="code-box">
            <h6>Formato esperado do arquivo:</h6>
            <pre class="json-preview">
        <span class="json-bracket">[</span>
            <span class="json-bracket">{</span>
              <span class="json-key">"city"</span><span class="json-colon">:</span> <span class="json-string">"New York"</span>,
              <span class="json-key">"growth_from_2000_to_2013"</span><span class="json-colon">:</span> <span class="json-string">"4.8%"</span>,
              <span class="json-key">"latitude"</span><span class="json-colon">:</span> <span class="json-number">40.7127837</span>,
              <span class="json-key">"longitude"</span><span class="json-colon">:</span> <span class="json-number">-74.0059413</span>,
              <span class="json-key">"population"</span><span class="json-colon">:</span> <span class="json-string">"8405837"</span>,
              <span class="json-key">"rank"</span><span class="json-colon">:</span> <span class="json-string">"1"</span>,
              <span class="json-key">"state"</span><span class="json-colon">:</span> <span class="json-string">"New York"</span>
            <span class="json-bracket">}</span>,
            <span class="json-bracket">{</span>
              <span class="json-key">"city"</span><span class="json-colon">:</span> <span class="json-string">"Los Angeles"</span>,
              <span class="json-key">"growth_from_2000_to_2013"</span><span class="json-colon">:</span> <span class="json-string">"4.8%"</span>,
              <span class="json-key">"latitude"</span><span class="json-colon">:</span> <span class="json-number">34.0522342</span>,
              <span class="json-key">"longitude"</span><span class="json-colon">:</span> <span class="json-number">-118.2436849</span>,
              <span class="json-key">"population"</span><span class="json-colon">:</span> <span class="json-string">"3884307"</span>,
              <span class="json-key">"rank"</span><span class="json-colon">:</span> <span class="json-string">"2"</span>,
              <span class="json-key">"state"</span><span class="json-colon">:</span> <span class="json-string">"California"</span>
            <span class="json-bracket">}</span>,
            ...
        <span class="json-bracket">]</span>
            </pre>
        </div>
        <style>
        .code-box {
            background-color: #121212;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            color: #f8f8f2;
        }
        .json-preview {
            font-size: 0.8em;
            overflow-x: auto;
            white-space: pre;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        .json-key {
            color: #f92672;
        }
        .json-string {
            color: #a6e22e;
        }
        .json-number {
            color: #ae81ff;
        }
        .json-bracket {
            color: #f8f8f2;
        }
        .json-colon {
            color: #f8f8f2;
        }
        </style>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Escolha um arquivo JSON", type=["json"], key="city_file_uploader", 
                                         help="Selecione um arquivo JSON contendo os dados das cidades.")
        
        if uploaded_file is not None:
            if st.button("📤 Carregar arquivo", use_container_width=True):
                success, msg = save_uploaded_cities_file(uploaded_file)
                st.session_state.cities_file_status = (success, msg)
                if success:
                    st.success(f"✅ {msg}")
                    st.balloons()  # Efeito visual para indicar sucesso
                    st.rerun()  # Recarregar a página para aplicar as mudanças
                else:
                    st.error(f"❌ {msg}")
                    # Mostrar informações mais detalhadas sobre o formato esperado
                    show_file_status_message(False, msg)
    
    # Menu principal de navegação
    st.markdown("## 🧭 NAVEGAÇÃO")
    selected = option_menu(
        menu_title=None,
        options=["App", "Algoritmos", "A Fórmula de Haversine", "Relatório", "Sobre"],
        icons=["map", "code-slash", "calculator", "file-text", "info-circle"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "var(--primary-color)", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "var(--primary-color)"},
        }
    )
    
    if selected == "Algoritmos":
        # Submenu para os algoritmos
        algorithm_choice = option_menu(
            menu_title=None,
            options=["A*", "BFS", "DFS", "Dijkstra", "Fuzzy"],
            icons=["stars", "diagram-2", "bounding-box", "map-fill", "cloud-fog2"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "var(--primary-color)", "font-size": "16px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
                "nav-link-selected": {"background-color": "var(--primary-color)"},
            }
        )

# Roteamento das páginas
if selected == "App":
    main_app()
elif selected == "Sobre":
    about_app()
elif selected == "A Fórmula de Haversine":
    haversine_app()
elif selected == "Relatório":
    report_app()
elif selected == "Algoritmos":
    if algorithm_choice == "BFS":
        bfs_page.app()
    elif algorithm_choice == "DFS":
        dfs_page.app()
    elif algorithm_choice == "A*":
        astar_page.app()
    elif algorithm_choice == "Fuzzy":
        fuzzy_page.app()
    elif algorithm_choice == "Dijkstra":
        dijkstra_page.app()