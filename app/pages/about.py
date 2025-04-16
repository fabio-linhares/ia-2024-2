import streamlit as st
import os
import base64

def app():
    st.title("Sobre o City Router")
    
    # Informações do projeto
    st.markdown("""
    ## Projeto: Localizador de Rotas entre Cidades
    
    Este aplicativo foi desenvolvido como atividade avaliativa B1 para a disciplina de Inteligência 
    Artificial do Programa de Pós-Graduação em Informática (PPGI) da Universidade Federal de Alagoas (UFAL).
    
    ### Objetivo
    
    O objetivo principal deste projeto é implementar e comparar diferentes algoritmos de busca para 
    encontrar rotas entre cidades, demonstrando conceitos de Inteligência Artificial aprendidos na disciplina.
    
    ### Algoritmos implementados
    
    - **BFS (Busca em Largura)**: Encontra o caminho com menor número de cidades intermediárias
    - **A* (A-Estrela)**: Encontra o caminho mais curto em termos de distância
    - **Busca Fuzzy**: Lida com incertezas nas conexões e pode encontrar rotas alternativas
    """)
    
    # Informações técnicas
    with st.expander("Informações técnicas"):
        st.markdown("""
        ### Tecnologias utilizadas
        
        - **Python**: Linguagem de programação principal
        - **Streamlit**: Framework para criar aplicativos web interativos
        - **NetworkX**: Biblioteca para criação e análise de grafos e redes
        - **Folium**: Biblioteca para visualização de mapas interativos
        - **Pandas**: Manipulação e análise de dados
        - **Matplotlib**: Visualizações e gráficos
        
        ### Dados
        
        Os dados das cidades americanas são carregados a partir de um arquivo JSON contendo informações como:
        - Nome e estado da cidade
        - População
        - Coordenadas geográficas (latitude e longitude)
        - Crescimento populacional entre 2000 e 2013
        - Ranking populacional
        
        ### Conversão entre coordenadas e distâncias
        
        **Importante**: A relação entre coordenadas geográficas (graus) e distâncias reais (quilômetros) é:
        
        - 1° de latitude ≈ 111 km
        - 1° de longitude ≈ 111 km × cos(latitude)
        
        Para cálculos precisos, utilizamos a fórmula de Haversine que considera a curvatura da Terra.
        """)
    
    # Informações institucionais
    st.markdown("## Informações Institucionais")
    
    col1 = st.columns(1)[0] 
    
    with col1:
        # Tentar carregar logos se existirem
        logos_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "logos")
        
        # Função para carregar e exibir logo
        def display_logo(logo_name):
            logo_path = os.path.join(logos_path, f"{logo_name}.png")
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")
                st.markdown(f'<img src="data:image/png;base64,{img_data}" width="150">', unsafe_allow_html=True)
                return True
            return False
        
        # Exibir os logos disponíveis
        #display_logo("ufal") or st.markdown("### UFAL")
        #display_logo("ic") or st.markdown("### Instituto de Computação")
        #display_logo("ppgi") or st.markdown("### PPGI-UFAL")

        st.markdown("""
        ### Universidade Federal de Alagoas (UFAL)
        Programa de Pós-Graduação em Informática (PPGI)
        Instituto de Computação (IC)
                    
        ### Atividade Avaliativa B1
        
        **Disciplina**: Inteligência Artificial  
        **Professores**: 
        - Dr. Glauber Rodrigues Leite
        - Dr. Evandro De Barros Costa
        
        ### Aluno
        Fábio Linhares  
        """)
    
    
    # Referências
    st.markdown("""
    ## Referências
    
    1. Russell, S. J., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach (4th ed.)*. Pearson.
    
    2. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms (3rd ed.)*. MIT Press.
    
    3. Zadeh, L. A. (1965). *Fuzzy sets*. Information and control, 8(3), 338-353.
    
    4. NetworkX documentation: https://networkx.org/
    
    5. Streamlit documentation: https://docs.streamlit.io/

    ## Repositório
    
    1. https://github.com/fabio-linhares/ia-2024-2.git   

    """)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Fábio Linhares | PPGI-UFAL | City Router | v1.0")




