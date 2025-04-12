import streamlit as st
import os

def app():
    st.title("Algoritmo A* (A-Estrela)")
    
    st.markdown("""
    ## O que é o algoritmo A*?
    
    O algoritmo A* (A-Estrela) é um algoritmo de busca informada que combina as vantagens da busca 
    gulosa (que busca o caminho que parece ser o melhor) e da busca de custo uniforme (que encontra
    o caminho de menor custo). Ele utiliza uma função de avaliação f(n) = g(n) + h(n), onde:
    
    - g(n) é o custo do caminho do nó inicial até o nó atual n
    - h(n) é uma heurística que estima o custo do caminho do nó n até o objetivo
    
    ### Características principais
    
    - **Completo**: Sempre encontra uma solução se ela existir (com certas condições).
    - **Ótimo**: Encontra o caminho de menor custo se a heurística for admissível (não superestimar).
    - **Eficiente**: Usa a heurística para guiar a busca e reduzir o espaço explorado.
    - **Complexidade**: Depende da qualidade da heurística, podendo ser exponencial no pior caso.
    """)
    
    # Dividir a tela em duas colunas
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Pseudocódigo
        ```
        A*(grafo, inicio, fim, h):
            abertos ← {inicio}  # nós a serem explorados
            fechados ← {}       # nós já explorados
            g[inicio] ← 0       # custo do caminho do início até o nó
            f[inicio] ← h(inicio, fim)  # estimativa de custo total
            pai ← dicionário vazio
            
            enquanto abertos não estiver vazio:
                atual ← nó em abertos com menor valor de f
                
                se atual == fim:
                    return reconstruir_caminho(pai, inicio, fim)
                
                remover atual de abertos
                adicionar atual a fechados
                
                para cada vizinho de atual no grafo:
                    se vizinho estiver em fechados:
                        continuar
                        
                    custo_g ← g[atual] + custo(atual, vizinho)
                    
                    se vizinho não estiver em abertos:
                        adicionar vizinho a abertos
                    senão se custo_g >= g[vizinho]:
                        continuar
                        
                    pai[vizinho] ← atual
                    g[vizinho] ← custo_g
                    f[vizinho] ← g[vizinho] + h(vizinho, fim)
                    
            return "Caminho não encontrado"
        ```
        """)

    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/98/AstarExampleEn.gif", 
                 caption="Visualização do algoritmo A*", use_column_width=True)
    
    # Carregar conteúdo adicional do arquivo markdown se existir
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                              "reports", "a_star_report.md")
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        st.markdown("## Relatório detalhado sobre A*")
        st.markdown(report_content)
    else:
        st.warning("Relatório detalhado sobre A* não encontrado.")
    
    # Heurísticas
    st.markdown("""
    ## Heurísticas comuns para o algoritmo A*
    
    No contexto de busca de caminhos entre cidades, algumas heurísticas comuns incluem:
    
    1. **Distância Euclidiana**: Linha reta entre dois pontos no plano.
       ```
       h(n) = sqrt((n.x - destino.x)² + (n.y - destino.y)²)
       ```
    
    2. **Distância de Manhattan**: Soma dos valores absolutos das diferenças das coordenadas.
       ```
       h(n) = |n.x - destino.x| + |n.y - destino.y|
       ```
    
    3. **Distância de Haversine**: Para calcular distâncias em uma esfera (como o planeta Terra).
       ```
       h(n) = 2 * R * arcsin(sqrt(sin²((lat2-lat1)/2) + cos(lat1) * cos(lat2) * sin²((lon2-lon1)/2)))
       ```
       onde R é o raio da Terra
    """)
    
    # Aplicações e casos de uso
    st.markdown("""
    ## Aplicações do A*
    
    1. **Sistemas de navegação GPS**:
       - Encontrar rotas mais curtas entre cidades
       - Otimizar percursos considerando distância real
    
    2. **Planejamento de rotas logísticas**:
       - Entregas em múltiplos pontos com menor distância total
       - Roteamento de veículos com restrições de distância
    
    3. **Jogos e simulações**:
       - Determinação de caminhos para personagens em ambientes virtuais
       - Simuladores de tráfego e deslocamento urbano
    
    ## Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    - Encontra o caminho mais curto em termos de distância real
    - Explora menos nós que algoritmos não informados como Dijkstra
    - Balanceia eficiência e otimalidade
    
    ### Desvantagens
    - Requer uma boa função heurística para ser eficiente
    - Mais complexo de implementar que BFS ou Dijkstra
    - Pode requerer mais memória para armazenar informações de estados
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## Comparação com outros algoritmos
    
    | Critério | A* | BFS | Fuzzy |
    |----------|----|----|-------|
    | Otimização | Distância total | Número de paradas | Considera incertezas |
    | Uso de heurística | Sim | Não | Parcial |
    | Eficiência computacional | Média-Alta | Média | Baixa |
    | Precisão | Alta | Baixa | Média |
    | Aplicação ideal | Rotas mais curtas | Conexões uniformes | Ambientes incertos |
    """)