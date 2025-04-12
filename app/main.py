import streamlit as st
import os
import base64

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

# Agora podemos importar outros módulos que podem usar comandos Streamlit
from streamlit_option_menu import option_menu
from app.pages import main_app, about
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
    # Seção de logotipos no topo
    logo_html = """<div style="display: flex; justify-content: space-between; margin-bottom: 20px;">"""
    
    for logo_name, logo_data in logos.items():
        if logo_data:
            logo_html += f'<img src="data:image/png;base64,{logo_data}" style="height: 60px;">'
        else:
            logo_html += f'<div style="height: 60px; width: 60px; display: flex; align-items: center; justify-content: center; background-color: #2D3748; border-radius: 5px;"><span>{logo_name.upper()}</span></div>'
    
    logo_html += """</div>"""
    st.markdown(logo_html, unsafe_allow_html=True)
    
    st.markdown("## PPGI-UFAL")
    st.markdown("**Mestrado em Informática - UFAL**")
    st.markdown("**Disciplina: Inteligência Artificial**")
    st.markdown("**Atividade Avaliativa B1**")
    st.markdown("## Professores")
    st.markdown("**Dr. Glauber Rocha**")
    st.markdown("**Dr. Evandro Mesquitaa**")
    st.markdown("## Alunos")
    st.markdown("**Fábio Linhares**")
    st.markdown("**Hans Ponfick de Aragão**")
    st.markdown("**Lurian Delevati**")

    st.markdown("---")
    
    selected = option_menu(
        menu_title="Navegação",
        options=["Rotas entre Cidades", "Algoritmos", "Sobre"],
        icons=["map", "code-slash", "info-circle"],
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
elif selected == "Algoritmos":
    if algorithm_choice == "BFS":
        bfs_page.app()
    elif algorithm_choice == "A*":
        astar_page.app()
    elif algorithm_choice == "Fuzzy":
        fuzzy_page.app()