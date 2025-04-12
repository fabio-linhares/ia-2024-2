import streamlit as st
import os

def app():
    st.title("Algoritmo de Busca Fuzzy")
    
    st.markdown("""
    ## O que é o algoritmo de Busca Fuzzy?
    
    A Busca Fuzzy é uma abordagem que utiliza lógica fuzzy (difusa) para lidar com incertezas
    e imprecisões em problemas de busca de caminhos. Em contraste com a lógica booleana tradicional,
    onde as conexões entre cidades seriam simplesmente "existe" ou "não existe", na lógica fuzzy
    essas conexões podem ter graus de pertinência entre 0 e 1.
    
    ### Características principais
    
    - **Flexibilidade**: Lida com incertezas e imprecisões nas conexões entre cidades.
    - **Tolerância**: Pode encontrar caminhos alternativos mesmo quando conexões ideais não estão disponíveis.
    - **Adaptabilidade**: Pode ajustar-se a diferentes condições e restrições.
    - **Valor de certeza**: Fornece um índice que indica a confiabilidade do caminho encontrado.
    """)
    
    # Dividir a tela em duas colunas
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Abordagem Fuzzy para roteamento
        
        O algoritmo de busca fuzzy para roteamento de cidades utiliza:
        
        1. **Funções de pertinência**: Determinam o grau de conectividade entre cidades baseado em distância
        2. **Regras fuzzy**: Definem como calcular o valor de certeza do caminho
        3. **Mecanismo de inferência**: Avalia as regras e determina o melhor caminho considerando incertezas
        
        Por exemplo, uma função de pertinência para a distância entre cidades poderia ser:
        
        ```
        μ(distância) = {
            1,                  se distância ≤ distância_mínima
            (max_dist - dist) / (max_dist - min_dist),  se dist entre min_dist e max_dist
            0,                  se distância > distância_máxima
        }
        ```
        
        Onde:
        - μ é o grau de pertinência (entre 0 e 1)
        - distância_mínima e distância_máxima são limites configuráveis
        """)

    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Fuzzy_logic_temperature_en.svg/800px-Fuzzy_logic_temperature_en.svg.png", 
                 caption="Exemplo de funções de pertinência fuzzy", use_column_width=True)
    
    # Carregar conteúdo adicional do arquivo markdown se existir
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                              "reports", "fuzzy_report.md")
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        st.markdown("## Relatório detalhado sobre Busca Fuzzy")
        st.markdown(report_content)
    else:
        st.warning("Relatório detalhado sobre Busca Fuzzy não encontrado.")
    
    # Pseudocódigo
    st.markdown("""
    ## Pseudocódigo simplificado
    
    ```
    FuzzySearch(grafo, inicio, fim, r, d):
        # Inicialização
        abertos ← PriorityQueue()
        abertos.adicionar(inicio, prioridade=1.0)  # Certeza máxima para o nó inicial
        visitados ← {inicio: 1.0}  # Mapa de nós visitados e seus valores de certeza
        pai ← dicionário vazio
        certeza_atual ← dicionário vazio com valor padrão 0.0
        certeza_atual[inicio] ← 1.0
        
        enquanto abertos não estiver vazio:
            atual, certeza ← abertos.remover()
            
            # Se encontramos o destino
            se atual == fim:
                caminho ← reconstruir_caminho(pai, inicio, fim)
                return caminho, certeza_atual[fim]
            
            para cada vizinho de atual no grafo:
                # Calcular grau de pertinência para esta conexão
                dist ← distancia(atual, vizinho)
                pertinencia ← calcular_pertinencia(dist, r, d)
                
                # Calcular nova certeza (usando operador T-norm, por exemplo, min)
                nova_certeza ← min(certeza_atual[atual], pertinencia)
                
                # Atualizar se encontramos um caminho melhor
                se vizinho não está em visitados OU nova_certeza > certeza_atual[vizinho]:
                    certeza_atual[vizinho] ← nova_certeza
                    pai[vizinho] ← atual
                    visitados[vizinho] ← nova_certeza
                    abertos.adicionar(vizinho, prioridade=nova_certeza)
        
        return "Caminho não encontrado", 0.0
    ```
    """)
    
    # Aplicações e casos de uso
    st.markdown("""
    ## Aplicações da Busca Fuzzy
    
    1. **Sistemas de navegação avançados**:
       - Lidar com rotas onde existem incertezas (como condições de tráfego variáveis)
       - Encontrar caminhos alternativos quando o caminho ideal não está disponível
    
    2. **Planejamento de rotas com múltiplos critérios**:
       - Balancear distância, tempo, custo e outras variáveis
       - Situações onde a conectividade entre locais pode variar (ex: transporte público com horários variáveis)
    
    3. **Sistemas de recomendação de rotas**:
       - Sugerir alternativas quando o caminho direto está congestionado
       - Considerar preferências subjetivas dos usuários
    
    ## Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    - Lida com incertezas e imprecisões nos dados
    - Pode encontrar caminhos alternativos quando o caminho ideal não está disponível
    - Fornece um valor de confiança para o caminho encontrado
    
    ### Desvantagens
    - Complexidade computacional mais elevada
    - Requer definição cuidadosa das funções de pertinência
    - Mais difícil de implementar e entender que algoritmos tradicionais
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## Comparação com outros algoritmos
    
    | Critério | Fuzzy | A* | BFS |
    |----------|----|----|----|
    | Otimização | Considera incertezas | Distância total | Número de paradas |
    | Capacidade de adaptação | Alta | Baixa | Nenhuma |
    | Índice de confiabilidade | Sim | Não | Não |
    | Complexidade | Alta | Média | Baixa |
    | Aplicação ideal | Ambientes incertos | Rotas mais curtas | Conexões uniformes |
    """)