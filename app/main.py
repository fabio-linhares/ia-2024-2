import streamlit as st

# Configuração da página - DEVE ser o primeiro comando Streamlit
st.set_page_config(
    page_title="City Router",
    page_icon=":cityscape:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Agora podemos importar outros módulos que podem usar comandos Streamlit
from streamlit_option_menu import option_menu
from app.pages import main_app, about

# Carregar CSS personalizado
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("app/styles/custom.css")

# Menu de navegação
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["City Router", "About"],
        icons=["map", "info-circle"],
        default_index=0,
    )

# Roteamento das páginas
if selected == "City Router":
    main_app.app()
elif selected == "About":
    about.app()