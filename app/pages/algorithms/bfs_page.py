import streamlit as st
import os

def app():
    st.title("Algoritmo de Busca em Largura (BFS)")
    
    st.markdown("""
    ## O que é o algoritmo BFS?
    
    A Busca em Largura (Breadth-First Search) é um algoritmo de busca em grafos que explora todos os vértices
    de um grafo a uma distância k do ponto de origem antes de explorar os vértices a uma distância k+1.
    
    ### Características principais
    
    - **Completo**: Sempre encontra uma solução se ela existir, desde que o grafo seja finito.
    - **Ótimo para custos unitários**: Garante encontrar o caminho de menor número de arestas.
    - **Complexidade espacial**: O(b^d), onde b é o fator de ramificação e d é a profundidade da solução.
    - **Complexidade temporal**: O(b^d), mesma ordem da complexidade espacial.
    """)
    
    # Dividir a tela em duas colunas
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Pseudocódigo
        ```
        BFS(grafo, inicio, fim):
            fila ← [inicio]
            visitados ← {inicio}
            pai ← dicionário vazio
            
            enquanto fila não estiver vazia:
                no_atual ← remover primeiro elemento da fila
                
                se no_atual == fim:
                    return reconstruir_caminho(pai, inicio, fim)
                
                para cada vizinho de no_atual no grafo:
                    se vizinho não estiver em visitados:
                        adicionar vizinho aos visitados
                        adicionar vizinho ao final da fila
                        pai[vizinho] ← no_atual
                        
            return "Caminho não encontrado"
        ```
        """)

    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/5/5d/Breadth-First-Search-Algorithm.gif", 
                 caption="Visualização do algoritmo BFS", use_column_width=True)
    
    # Carregar conteúdo adicional do arquivo markdown se existir
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                              "reports", "bfs_report.md")
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        st.markdown("## Relatório detalhado sobre BFS")
        st.markdown(report_content)
    else:
        st.warning("Relatório detalhado sobre BFS não encontrado.")
    
    # Aplicações e casos de uso
    st.markdown("""
    ## Aplicações do BFS
    
    1. **Encontrar o caminho mais curto em grafos não ponderados**:
       - Útil para encontrar o caminho com o menor número de conexões entre cidades
       - Ideal para casos onde todas as arestas têm o mesmo custo ou importância
    
    2. **Teste de conectividade em grafos**:
       - Verificar se existe um caminho entre duas cidades
       - Identificar componentes conectados no grafo
    
    3. **Sistemas de navegação básicos**:
       - Rotas que minimizam o número de paradas ou trocas
       - Planejamento de viagens com o menor número de conexões
    
    ## Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    - Encontra o caminho com o menor número de cidades intermediárias
    - Implementação simples e eficiente
    - Garantia de encontrar o caminho com o menor número de "saltos"
    
    ### Desvantagens
    - Não considera a distância real entre as cidades
    - Pode resultar em caminhos mais longos em termos de distância total percorrida
    - Não é apropriado quando as conexões têm custos diferentes
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## Comparação com outros algoritmos
    
    | Critério | BFS | A* | Fuzzy |
    |----------|-----|----|----|
    | Otimização | Número de paradas | Distância total | Considera incertezas |
    | Complexidade | Menor | Média | Maior |
    | Uso de memória | Alto | Médio | Médio |
    | Aplicação ideal | Conexões uniformes | Rotas mais curtas | Ambientes incertos |
    """)