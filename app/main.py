import streamlit as st
import os
import base64

# Inicialização do estado da sessão para o tema (se não existir)
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

# Função para alternar o tema
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    # Não usar st.rerun() aqui, pois causará erro quando chamado dentro de um callback

# Configuração da página - DEVE ser o primeiro comando Streamlit
st.set_page_config(
    page_title="City Router - UFAL",
    page_icon=":cityscape:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "City Router - Projeto de Inteligência Artificial - PPGI-UFAL"
    }
)

# Aplicar tema escuro via JavaScript se o tema for "dark"
if st.session_state.theme == "dark":
    dark_mode_js = """
    <script>
        const doc = window.parent.document;
        doc.querySelector('body').classList.add('dark');
        
        // Código para forçar recarga da página para aplicar o tema
        if (window.name != 'themeSwitched') {
            window.name = 'themeSwitched';
            window.location.reload();
        } else {
            window.name = '';
        }
    </script>
    """
    st.markdown(dark_mode_js, unsafe_allow_html=True)
else:
    # Resetar flag quando estiver no tema claro
    light_mode_js = """
    <script>
        const doc = window.parent.document;
        doc.querySelector('body').classList.remove('dark');
        
        // Código para forçar recarga da página para aplicar o tema
        if (window.name != 'themeSwitched') {
            window.name = 'themeSwitched';
            window.location.reload();
        } else {
            window.name = '';
        }
    </script>
    """
    st.markdown(light_mode_js, unsafe_allow_html=True)

# Ocultar o menu de navegação padrão do Streamlit e o botão de colapso da sidebar
hide_streamlit_elements = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
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
from app.pages import main_app, about, haversine_page
from app.pages.algorithms import bfs_page, astar_page, fuzzy_page

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
    
    # Logo da UFAL ampliado e centralizado - aumentado em mais 30%
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
    
    # Logos IC e PPGI lado a lado com distância ainda mais reduzida
    col1, col2 = st.columns([1, 1], gap="small")  # gap="small" para aproximar as colunas
    
    # Estilo de container para aproximar ainda mais os logos
    st.markdown("""
    <style>
    .logo-container {
        margin: 0 -7px; /* Margem negativa para aproximar mais */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # IC agora à esquerda
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
    
    # PPGI agora à direita
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
    
    # Espaço de 15 pixels antes do menu de configurações
    st.markdown("<div style='height: 15x;'></div>", unsafe_allow_html=True)
    
    # Menu suspenso para configurações rápidas (incluindo o botão de tema)
    with st.expander("Configurações Rápidas", expanded=st.session_state.show_config):
        theme_icon = "moon" if st.session_state.theme == "light" else "sun"
        theme_label = "Ativar tema escuro" if st.session_state.theme == "light" else "Ativar tema claro"
        st.button(f"{theme_label} ::{theme_icon}::", on_click=toggle_theme)
    
    # Menu principal de navegação
    st.markdown("## NAVEGAÇÃO")
    selected = option_menu(
        menu_title=None,
        options=["Rotas entre Cidades", "Algoritmos", "A Fórmula de Haversine", "Sobre"],
        icons=["map", "code-slash", "calculator", "info-circle"],
        default_index=0,
    )
    

    
    if selected == "Algoritmos":
        # Submenu para os algoritmos
        algorithm_choice = option_menu(
            menu_title=None,
            options=["BFS", "A*", "Fuzzy"],
            icons=["diagram-2", "stars", "cloud-fog2"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )

# Roteamento das páginas
if selected == "Rotas entre Cidades":
    main_app.app()
elif selected == "Sobre":
    about.app()
elif selected == "A Fórmula de Haversine":
    haversine_page.app()
elif selected == "Algoritmos":
    if algorithm_choice == "BFS":
        bfs_page.app()
    elif algorithm_choice == "A*":
        astar_page.app()
    elif algorithm_choice == "Fuzzy":
        fuzzy_page.app()