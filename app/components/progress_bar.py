import streamlit as st

progress_bar = st.progress(0)

def update_progress(value, text=""):
    """Atualiza a barra de progresso."""
    progress_bar.progress(value, text=text)