import streamlit as st

def city_selector(label, city_names, default_city):
    """Componente para selecionar uma cidade em um menu suspenso."""
    selected_city = st.selectbox(
        label,
        city_names,
        index=city_names.index(default_city) if default_city in city_names else 0
    )
    return selected_city