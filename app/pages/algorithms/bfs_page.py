import streamlit as st
import os
import networkx as nx
import time
from app.utils.algorithms import IterativeBFS
from app.components.map_display import display_path_on_map
from app.components.progress_bar import animated_progress

def app():
    st.title("Algoritmo de Busca em Largura (BFS)")
    
    st.markdown(r"""
    ## 1. O que é o algoritmo BFS?
    
    A Busca em Largura (Breadth-First Search) é um algoritmo fundamental de busca em grafos que explora todos os vértices
    de um grafo a uma distância k do ponto de origem antes de explorar os vértices a uma distância k+1. Foi desenvolvido
    em 1959 por Edward F. Moore para encontrar o caminho mais curto em labirintos.
    
    O BFS implementa uma estratégia de busca "nível por nível", garantindo que todos os nós em uma certa distância
    do início sejam visitados antes de avançar para os nós mais distantes. Esta abordagem sistemática é conseguida
    utilizando uma estrutura de dados FIFO (First-In-First-Out), tipicamente uma fila.
    
    Do ponto de vista matemático, o BFS realiza uma travessia por níveis na árvore de busca implícita gerada a partir
    do grafo original, onde cada nível i contém todos os nós que estão a i arestas de distância do nó inicial.
                
    ### Características principais
    
    - **Completude**: Sempre encontra uma solução se ela existir, desde que o grafo seja finito.
    - **Ótimo para custos unitários**: Garante encontrar o caminho com menor número de arestas.
    - **Eficiência sistemática**: Visita os nós em ordem crescente de distância do início.
    - **Ausência de ciclos**: Com controle de nós visitados, nunca revisita nós.
    - **Complexidade espacial**: O(b^d), onde b é o fator de ramificação e d é a profundidade da solução.
    - **Complexidade temporal**: O(b^d), mesma ordem da complexidade espacial.
    - **Fronteira progressiva**: Mantém uma "fronteira" de expansão que cresce uniformemente.
    """)
    
    # Layout para pseudocódigo e imagem (lado a lado)
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo")
        st.code("""
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
        """, language="python")

    with cols[1]:
        st.markdown("##### ")
        image_width = 630  # Largura em pixels para padronizar com outros algoritmos
        
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center;">
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/5/5d/Breadth-First-Search-Algorithm.gif",
            caption="Visualização do algoritmo BFS",
            width=image_width  # Controle direto da largura
        )
    
    # Detalhes matemáticos sobre BFS
    st.markdown(r"""
    ### 1.1 Propriedades matemáticas do BFS
    
    1. **Invariante de distância**: Em qualquer momento durante a execução do BFS, quando um nó v é descoberto, 
    o caminho encontrado até ele é garantidamente o mais curto em número de arestas. Formalmente:
    
    $$d(s, v) = \delta(s, v)$$
    
    Onde d(s, v) é a distância calculada pelo BFS e δ(s, v) é a distância real mais curta entre s e v.
    
    2. **Propriedade de corte por nível**: Um grafo G=(V,E) pode ser particionado em níveis L₀, L₁, ..., Lᵢ, ... onde:
    
    $$L_0 = \{s\}$$
    $$L_i = \{v \in V : \delta(s, v) = i\}$$
    
    3. **Árvore BFS**: A execução do BFS induz uma árvore com raiz no nó inicial s, onde para cada nó v alcançável a partir de s,
    existe um único caminho simples de s a v na árvore, e este caminho corresponde ao caminho mais curto em G.
    
    4. **Teorema de correção do BFS**: Para todo nó v alcançável a partir de s, ao término do algoritmo BFS:
    
    $$d[v] = \delta(s, v)$$
    
    Onde d[v] é a distância calculada pelo algoritmo e δ(s, v) é a distância real mais curta.
    """)
    
    # Implementações avançadas e variantes
    st.markdown(r"""
    ### 1.2 Implementações eficientes e variantes do BFS
    
    1. **BFS Bidirecional**: Inicia duas buscas simultaneamente - uma a partir do nó inicial e outra a partir do nó objetivo.
    Quando as duas fronteiras se encontram, um caminho completo é identificado. Pode reduzir a complexidade para O(b^{d/2}).
    
    2. **BFS com múltiplas origens**: Inicia a busca simultaneamente a partir de múltiplos nós iniciais, útil para problemas
    como encontrar a distância mínima de um conjunto de pontos a qualquer ponto em outro conjunto.
    
    3. **BFS com peso uniforme**: Equivalente ao algoritmo de Dijkstra quando todas as arestas têm o mesmo peso.
    
    4. **BFS com corte (Truncated BFS)**: Limita a busca a uma profundidade máxima d, útil para encontrar todos os nós
    dentro de uma certa distância da origem.
    
    5. **BFS iterativo com aprofundamento (Iterative Deepening BFS)**: Realiza múltiplas buscas BFS com profundidade
    crescente, combinando as vantagens de espaço do DFS com a otimalidade do BFS.
    
    6. **BFS paralelo**: Implementações distribuídas que exploram múltiplos nós da fronteira em paralelo,
    particularmente eficazes em grafos muito grandes.
    
    7. **BFS com prioridade (BFSP)**: Atribui pesos às arestas e usa uma fila de prioridade, transformando-se
    efetivamente no algoritmo de Dijkstra.
    """)
      
    # Aplicações e casos de uso
    st.markdown("""
    ## 2. Aplicações do BFS
    
    1. **Análise de redes sociais**:
       - Identificação de graus de separação entre pessoas (problema dos "seis graus de separação")
       - Descoberta de comunidades e análise de influência
       - Propagação de informação e modelagem de difusão viral
    
    2. **Descoberta e exploração em grafos**:
       - Teste de conectividade e identificação de componentes conectados
       - Verificação de bipartição de grafos
       - Detecção de ciclos em grafos não direcionados
    
    3. **Sistemas de navegação e roteamento**:
       - Cálculo de rotas com menor número de transferências em transporte público
       - Planejamento de viagens minimizando número de conexões aéreas
       - Roteamento com prioridade para conexões diretas entre cidades
    
    4. **Algoritmos de web crawling**:
       - Indexação de páginas web por mecanismos de busca
       - Descoberta de novos recursos em uma rede
       - Mapeamento da estrutura da web
    
    5. **Processamento de imagens e visão computacional**:
       - Segmentação de imagens por inundação (flood fill)
       - Extração de regiões conectadas em imagens binárias
       - Algoritmos de rotulação de componentes conectados
    
    6. **Resolução de puzzles e jogos**:
       - Solução de quebra-cabeças como o cubo de Rubik (encontrando a sequência mais curta de movimentos)
       - Solução de jogos como "palavra-ladder" (transformar uma palavra em outra alterando uma letra de cada vez)
       - Geração de labirintos perfeitos (sem ciclos)
    """)
    
    # Vantagens e desvantagens
    st.markdown("""
    ## 3. Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    
    - **Garantia de caminho ótimo em termos de etapas**: Encontra sempre o caminho com menor número de cidades intermediárias
    - **Simplicidade conceitual e implementação**: Fácil de entender, programar e depurar
    - **Previsibilidade**: Comportamento sistemático e bem definido, adequado para sistemas críticos
    - **Adequação para grafos esparsos**: Desempenho eficiente quando o número de conexões por cidade é limitado
    - **Consumo de memória previsível**: O uso de memória é proporcional ao número de nós na fronteira
    - **Útil para análise topológica**: Permite descobrir propriedades estruturais da rede de cidades
    
    ### Desvantagens
    
    - **Ignora distâncias reais**: Não considera os custos variáveis das conexões entre cidades
    - **Pode resultar em rotas ineficientes**: Caminhos com menos cidades podem ter distâncias totais muito maiores
    - **Consumo de memória significativo**: Necessário armazenar todos os nós da fronteira, que pode crescer exponencialmente
    - **Ineficiência para grafos densos**: Performance degrada significativamente em redes com muitas conexões por cidade
    - **Limitações para routing multicriterial**: Não balanceia naturalmente diferentes objetivos de otimização
    - **Inadequado para grafos ponderados**: Não apropriado quando as conexões têm custos diferentes e significativos
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## 4. Comparação com outros algoritmos
    
    | Critério | BFS | DFS | Dijkstra | A* | Fuzzy |
    |----------|-----|-----|----------|----|----|
    | **Princípio básico** | Exploração em largura | Exploração em profundidade | Menor caminho | Heurística + custo real | Graus de pertinência |
    | **Otimização** | Número de paradas | Nenhuma garantia | Distância total | Distância com heurística | Multiobjetivo com incertezas |
    | **Completude** | Sim (espaço finito) | Sim (com controle de ciclos) | Sim | Sim | Depende da implementação |
    | **Otimalidade** | Sim (em arestas) | Não | Sim (distância) | Sim (com heurística admissível) | Não (subjetiva) |
    | **Estratégia de busca** | Uniforme por níveis | Profundidade prioritária | Menor custo acumulado | Custo + heurística | Pertinência |
    | **Estrutura de dados** | Fila (FIFO) | Pilha (LIFO) | Fila de prioridade | Fila de prioridade | Fila de prioridade fuzzy |
    | **Complexidade temporal** | O(b^d) | O(b^d) | O(E + V log V) | O(b^d) - varia com heurística | O(b^d) com overhead fuzzy |
    | **Complexidade espacial** | O(b^d) | O(d) | O(V) | O(b^d) | O(b^d) |
    | **Uso de memória** | Alto | Baixo | Médio | Médio-alto | Alto |
    | **Aplicação ideal** | Conexões uniformes | Exploração com memória limitada | Minimização de distância | Rotas com boa heurística | Ambientes incertos |
    | **Adequação para grafos grandes** | Limitada | Boa | Boa | Média | Limitada |
    | **Paralelizável** | Facilmente | Dificilmente | Dificilmente | Parcialmente | Parcialmente |
    | **Sensibilidade à estrutura do grafo** | Baixa | Alta | Média | Média | Baixa |
    """)

    # Implementação avançada do BFS - conteúdo técnico adicional
    st.markdown(r"""
    ## 5. Análise avançada de desempenho e otimizações

    ### 5.1 Análise assintótica detalhada
    
    Para um grafo G = (V, E) com |V| = n vértices e |E| = m arestas:
    
    - **Inicialização**: O(n) para inicializar as estruturas de dados
    - **Processamento da fila**: Cada nó entra e sai da fila exatamente uma vez, resultando em O(n) operações
    - **Exame de arestas**: Cada aresta (u,v) é examinada quando u é desenfileirado, resultando em O(m) operações
    
    Portanto, a complexidade total é O(n + m), que é linear no tamanho do grafo.
    
    No caso específico de grafos onde m >> n (grafos densos), a complexidade é aproximadamente O(m).
    No caso de grafos esparsos típicos em redes urbanas, onde m ≈ k·n para uma constante k pequena, a complexidade é O(n).
    
    ### 5.2 Otimizações de implementação
    
    1. **Utilização de visitados como conjunto de hash**: Permite verificação de pertinência em O(1), acelerando significativamente o algoritmo.
    
    2. **BFS com lista de adjacência compacta**: Em vez de armazenar explicitamente cada vizinho, usar representações compactas como listas de adjacência reduz o overhead de memória.
    
    3. **Pré-alocação de estruturas de dados**: Alocar memória para a fila e o conjunto de visitados antecipadamente pode reduzir o overhead de realocação.
    
    4. **Bit parallelism**: Para grafos pequenos, usar vetores de bits para representar o conjunto de visitados pode melhorar a eficiência de cache.
    
    5. **Balanceamento de carga em implementações paralelas**: Estratégias de divisão de trabalho adaptativas podem melhorar significativamente o desempenho em sistemas multicore.
    """)

    # Seção de visualização interativa (mantida do código original)
    st.markdown("""
    ## 6. Visualização Interativa do BFS
    
    Nesta seção, você pode visualizar o algoritmo BFS em ação, passo a passo. Selecione as cidades de origem e destino,
    e clique em "Iniciar Busca". Em seguida, use o botão "Continuar a iterar?" para avançar nas iterações do algoritmo
    e observar como ele explora o grafo em busca do caminho.
    """)
    
    # Criando uma sessão state para armazenar o estado do algoritmo entre as iterações
    if 'algorithm_instance' not in st.session_state:
        st.session_state.algorithm_instance = None
    if 'iteration_number' not in st.session_state:
        st.session_state.iteration_number = 0
    if 'path_found' not in st.session_state:
        st.session_state.path_found = False
    if 'started' not in st.session_state:
        st.session_state.started = False
    
    # Carregando o grafo e as cidades (assumindo que estão disponíveis no estado da sessão)
    if 'graph' in st.session_state and 'cities' in st.session_state:
        graph = st.session_state.graph
        cities = st.session_state.cities
        
        # Interface para seleção de cidades
        col1, col2 = st.columns(2)
        with col1:
            start_city = st.selectbox(
                "Cidade de origem", 
                options=list(cities.keys()),
                key="bfs_start_city"
            )
        with col2:
            end_city = st.selectbox(
                "Cidade de destino", 
                options=list(cities.keys()),
                key="bfs_end_city"
            )
        
        # Botão para iniciar a busca
        if st.button("Iniciar Busca", key="start_bfs"):
            # Resetar o estado
            st.session_state.algorithm_instance = IterativeBFS(graph, start_city, end_city)
            st.session_state.iteration_number = 0
            st.session_state.path_found = False
            st.session_state.started = True
            st.experimental_rerun()
        
        # Botão para continuar a iterar (avançar uma iteração)
        if st.session_state.started:
            # Exibir informações da iteração atual
            st.markdown(f"### Iteração: {st.session_state.iteration_number}")
            
            # Informações sobre o estado atual
            if st.session_state.algorithm_instance:
                algo = st.session_state.algorithm_instance
                iteration_data = algo.get_iteration_data()
                
                # Exibir nós visitados e fronteira
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Nós visitados: {len(iteration_data['visited_nodes'])}")
                    st.write(f"Nós na fronteira: {len(iteration_data['frontier_nodes'])}")
                with col2:
                    if iteration_data['current_path']:
                        st.write(f"Caminho atual: {' -> '.join(iteration_data['current_path'])}")
                        st.write(f"Distância atual: {iteration_data['current_dist']:.2f} km")
                
                # Exibir mapa com o caminho atual e nós visitados
                graph_for_display = graph.copy()
                
                # Exibir o caminho atual no mapa
                if iteration_data['current_path']:
                    display_path_on_map(graph_for_display, cities, iteration_data['current_path'], 
                                       highlight_nodes=iteration_data['visited_nodes'],
                                       frontier_nodes=iteration_data['frontier_nodes'])
                
                # Botão para continuar a iteração
                if not st.session_state.path_found:
                    if st.button("Continuar a iterar?", key="continue_iteration"):
                        # Executar mais uma iteração
                        is_complete = algo.step()
                        st.session_state.iteration_number += 1
                        
                        if is_complete:
                            st.session_state.path_found = True
                            st.success(f"Caminho encontrado após {st.session_state.iteration_number} iterações!")
                            # Animação para mostrar a conclusão
                            # Ignorando o valor de retorno da função, pois não é necessário
                            animated_progress()
                            
                        st.experimental_rerun()
                else:
                    st.success(f"Caminho encontrado: {' -> '.join(algo.get_current_path())}")
                    st.info(f"Distância total: {algo.get_current_dist():.2f} km")
                    st.info(f"Tempo de execução: {algo.elapsed_time:.2f} ms")
                    st.info(f"Número de iterações: {st.session_state.iteration_number}")
                    
                    # Botão para reiniciar
                    if st.button("Reiniciar Busca", key="restart_bfs"):
                        st.session_state.started = False
                        st.experimental_rerun()
    else:
        st.warning("Por favor, selecione um conjunto de dados na página principal primeiro.")
    
    # # Carregar conteúdo adicional do arquivo markdown se existir
    # report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    #                           "reports", "bfs_report.md")
    
    # if os.path.exists(report_path):
    #     with open(report_path, 'r', encoding='utf-8') as f:
    #         report_content = f.read()
            
    #     st.markdown("## 6. Relatório detalhado sobre BFS")
    #     st.markdown(report_content)
    # else:
    #     st.warning("Relatório detalhado sobre BFS não encontrado.")

    st.markdown(r"""
    ### Notas
    
    [1] **Prova informal da otimalidade do BFS**: Considere que BFS expande nós em ordem de distância crescente do nó inicial.
    Se um nó v é alcançado pela primeira vez, o caminho encontrado deve ser o mais curto, pois se existisse um caminho mais curto,
    v teria sido descoberto antes através desse caminho mais curto, contradizendo nossa suposição.
    
    [2] **Teorema de distância do BFS**: Para qualquer vértice v acessível a partir do vértice inicial s, o algoritmo BFS calcula
    corretamente a distância d(s,v), sendo que quando v é retirado da fila, temos:
    
    $$d[v] = \delta(s,v)$$
    
    Onde δ(s,v) é a distância real mais curta entre s e v.
    
    [3] **Robustez em redes com falhas**: O BFS pode ser adaptado para encontrar caminhos alternativos em redes com falhas
    de conectividade, mantendo múltiplas rotas candidatas e avaliando sua viabilidade.
    
    [4] **BFS em grafos infinitos**: Embora o BFS seja completo apenas para grafos finitos, existem variantes como o "iterative broadening"
    que permitem sua aplicação a espaços de busca infinitos, limitando progressivamente a largura da busca em cada iteração.
    
    [5] **Aplicação em teoria dos jogos**: O BFS é fundamental para a análise de jogos combinatórios, onde cada estado do jogo
    é um nó e cada movimento legal é uma aresta. A busca em largura pode determinar se um jogo tem solução e qual é o número mínimo
    de movimentos necessários.
    
    [6] **BFS e análise de conectividade**: O algoritmo BFS é a base para muitos algoritmos de análise de conectividade em grafos,
    incluindo a identificação de pontes, articulações e componentes biconexos, que são cruciais para avaliar a robustez de redes
    de transporte e comunicação.
    """)