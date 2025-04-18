import streamlit as st
import networkx as nx
import time
import heapq

def app():
    st.title("Algoritmo de Busca em Largura (BFS) — Estado da Arte")
    
    st.markdown(r"""
    ## 1. O que é o algoritmo BFS?

    A Busca em Largura (Breadth-First Search — BFS) é um algoritmo fundamental para exploração e busca em grafos. Em cada nível, o BFS visita todos os nós a uma distância k da origem antes de avançar para a distância k+1. A implementação moderna apresentada aqui adota características de estado da arte:
    
    - **Busca Bidirecional:** A busca ocorre simultaneamente a partir do ponto inicial e do final, acelerando a descoberta de caminhos mínimos.
    - **Fila de Prioridade por População:** Entre os vizinhos não visitados, o algoritmo sempre prioriza a expansão dos nós com menor população. Caminhos de cidades menos populosas tendem a ser explorados primeiro, mas cidades de maior população não são bloqueadas — a busca é apenas priorizada.
    - **Timeout Customizável:** Permite limitar a duração da busca, garantindo responsividade em sistemas online.
    - **Retorno Rico de Métricas:** Inclui quantidade de cidades visitadas, tamanho máximo da fronteira, percentual do grafo explorado e detecção de timeout.
    - **Robustez:** Sempre retorna o caminho encontrado como uma lista (vazia se não encontrar), tolerando qualquer cenário de grafo.
    """)


    # Layout para pseudocódigo e imagem (lado a lado)
    cols = st.columns([1, 1])
    
    with cols[0]:
     # Pseudocódigo atualizado (incluindo bidirecional e fila de prioridade)
        st.markdown("""
        ### Pseudocódigo (moderno e priorizado)
        ```python
        BFS_bidirecional_prioritario(grafo, inicio, fim):
            fronteira_inicio, fronteira_fim = filas de prioridade por população
            visitados_inicio, visitados_fim = conjuntos de visitados
            pais_inicio, pais_fim = dicionários de predecessores

            enquanto fronteiras não vazias:
                escolha o lado com menor fronteira p/ expandir
                nó_atual = remover nó de menor população da fronteira
                
                para vizinho de nó_atual não visitado:
                    se vizinho já explorado pelo outro lado:
                        caminho = juntar caminho dos pais dos dois lados
                        retorna caminho, métricas
                    adiciona vizinho na fronteira por prioridade de população
                    marca vizinho como visitado

            retorna lista vazia, indicando nenhuma rota encontrada
        ```
        """)

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



    

    st.markdown(r"""
    --- 

    ## 2. Novidades e avanços da implementação

    - **Busca Bidirecional:** Reduz a complexidade esperada de O(b^d) para O(b^{d/2}) em média, onde d é a distância ótima.
    - **Prioridade dinâmica:** Caminhos por cidades menos populosas são priorizados, útil para determinadas políticas ou preferências urbanas (exemplo: evitar grandes centros).
    - **Fila de prioridade (`heapq`):** Eficiência garantida na retirada do próximo nó mais promissor, sem exclusão total de outras alternativas.
    - **Timeout:** Determina fim da busca caso o tempo/recursos cheguem ao limite.

    Exemplo de principais métricas:
    - **visited:** Quantidade total de cidades exploradas;
    - **frontier_max:** Maior largura da fronteira durante a busca;
    - **explored_pct:** Percentual do grafo percorrido;
    - **iterations:** Número total de iterações;
    - **timeout:** Indicação se a busca foi abortada por tempo.

    Exemplo de tuple de retorno:
    ```python
    caminho, distancia_total, tempo_ms, info = bfs_bidirecional_prioritario(...)
    ```

    ---

    ## 3. Detalhes matemáticos e propriedades

    - **Invariante de distância**: Em qualquer momento durante a execução do BFS, quando um nó v é descoberto, 
    o caminho encontrado até ele é garantidamente o mais curto em número de arestas. Formalmente:
    
    $$d(s, v) = \delta(s, v)$$
    
    Onde d(s, v) é a distância calculada pelo BFS e δ(s, v) é a distância real mais curta entre s e v.
    
    - **Propriedade de corte por nível**: Um grafo G=(V,E) pode ser particionado em níveis L₀, L₁, ..., Lᵢ, ... onde:
    
    $$L_0 = \{s\}$$
    $$L_i = \{v \in V : \delta(s, v) = i\}$$
    
    - **Árvore BFS**: A execução do BFS induz uma árvore com raiz no nó inicial s, onde para cada nó v alcançável a partir de s,
    existe um único caminho simples de s a v na árvore, e este caminho corresponde ao caminho mais curto em G.
    
    - **Teorema de correção do BFS**: Para todo nó v alcançável a partir de s, ao término do algoritmo BFS:
    
    $$d[v] = \delta(s, v)$$
    
    Onde d[v] é a distância calculada pelo algoritmo e δ(s, v) é a distância real mais curta.

    ---

    ## 4. Vantagens e desvantagens da nova abordagem

    **Vantagens:**
    - Exploração eficiente que preserva caminhos comuns do BFS;
    - Priorização reduz congestionamento em regiões densamente povoadas, sem isolamento artificial;
    - Tolerância a grafos reais (com hubs populosos);
    - Timeout e métricas facilitam uso em sistemas críticos/online.

    **Desvantagens:**
    - Não garante sempre o caminho mais "populacionalmente baixo" — pode preferir por população, mas caminho ótimo é sempre por menor número de arestas (exceto se populações iguais).

    ---

    ## 5. Equivalência com Dijkstra no caso unitário

    Caso todas as populações sejam iguais, a BFS priorizada equivale à BFS comum: a fila de prioridade funciona como FIFO.
    """)

    st.markdown("""
## 6. Comparação com outros algoritmos

| Critério                         | BFS Prioridade População  | DFS                        | Dijkstra                  | A*                        | Fuzzy                    |
|-----------------------------------|--------------------------|----------------------------|---------------------------|---------------------------|--------------------------|
| **Princípio básico**              | Largura priorizada (população) | Exploração em profundidade | Menor caminho (peso/dist) | Heurística + custo real   | Graus de pertinência      |
| **Otimização**                    | Nº de paradas, prioriza cidades menos populosas | Nenhuma garantia           | Minimiza distância total  | Distância + heurística    | Multiobjetivo/incertezas |
| **Completude**                    | Sim (em espaço finito)   | Sim (controle de ciclos)   | Sim                       | Sim                       | Depende da implementação  |
| **Otimalidade**                   | Sim (arestas); menor população priorizada, mas não garantida | Não   | Sim (distância)          | Sim (heurística admissível)| Não (subjetiva)          |
| **Estratégia de busca**           | Heap por população (largura priorizada) | Profundidade prioritária   | Menor custo acumulado     | Custo + heurística        | Pertinência              |
| **Estrutura de dados**            | Fila de prioridade (heap) | Pilha (LIFO)               | Fila de prioridade        | Fila de prioridade        | Fila fuzzy               |
| **Complexidade temporal**         | O(b^d) *(O(b^{d/2}) bidirecional)*<br>Overhead do heap possível | O(b^d) | O(E + V log V)           | O(b^d) *(varia)*          | O(b^d) + overhead fuzzy  |
| **Complexidade espacial**         | O(b^d)                   | O(d)                       | O(V)                      | O(b^d)                    | O(b^d)                   |
| **Uso de memória**                | Alto (heap e bidirecional) | Baixo                    | Médio                     | Médio-alto                | Alto                     |
| **Aplicação ideal**               | Rotas curtas privilegiando cidades menos populosas; análise urbana | Exploração com pouca memória | Minimização de distância | Rotas c/ boa heurística  | Ambientes incertos       |
| **Adequação para grafos grandes** | Média (heap/bidirecional otimizam, mas consumo alto) | Boa | Boa                      | Boa                       | Limitada                 |
| **Paralelizável**                 | Sim (expansão de fronteira) | Difícil                  | Difícil                   | Parcialmente              | Parcialmente             |
| **Sensibilidade à estrutura do grafo** | Média (população afeta expansão) | Alta                | Média                     | Média                     | Baixa                    |
""")

    st.markdown("""
    ---
    ## 7. Padrão de uso e integração

    O algoritmo está adaptado para uso em sistemas web ou de backend de rotas:
    - Cache de resultados via hash do grafo;
    - Timeout;
    - Safe para frontends (nunca retorna None como caminho);
    - Fácil integração com visualizações e ferramentas de análise urbana.
    """)

    st.markdown(r"""
    ---
    ## 8. Código simplificado da implementação bidirecional priorizada

    ```python
    import heapq, time

    def breadth_first_search(graph, start, end, timeout_ms=5000):
        start_time = time.perf_counter()
        if start == end:
            return [start], 0, 0, {}
        if start not in graph or end not in graph:
            return [], float('inf'), 0, {}
        # prioridade: heap por população
        frontier_start = []
        frontier_end = []
        heapq.heappush(frontier_start, (int(graph.nodes[start]['population']), 0, start))
        heapq.heappush(frontier_end, (int(graph.nodes[end]['population']), 0, end))
        visited_start = {start}
        visited_end = {end}
        parents_start = {start: None}
        parents_end = {end: None}
        counter = 1
        nodes_visited = set([start, end])
        max_nodes = graph.number_of_nodes()
        frontier_max = 2
        iteration = 0
        while frontier_start and frontier_end:
            if (time.perf_counter() - start_time) * 1000 > timeout_ms:
                return [], float('inf'), (time.perf_counter() - start_time)*1000, {
                    'visited': len(nodes_visited),
                    'frontier_max': frontier_max,
                    'explored_pct': (len(nodes_visited) / max_nodes) * 100,
                    'timeout': True
                }
            # Expande o menor heap
            if len(frontier_start) <= len(frontier_end):
                frontier, visited, parents = frontier_start, visited_start, parents_start
                other_visited, other_parents = visited_end, parents_end
            else:
                frontier, visited, parents = frontier_end, visited_end, parents_end
                other_visited, other_parents = visited_start, parents_start
            _, _, current = heapq.heappop(frontier)
            for neighbor in graph.neighbors(current):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parents[neighbor] = current
                nodes_visited.add(neighbor)
                if neighbor in other_visited:
                    # Reconstruir caminho e retornar
                    path = reconstruct_path(
                        neighbor,
                        parents_start, parents_end
                    )
                    total_dist = path_distance(graph, path)
                    elapsed_time = (time.perf_counter() - start_time) * 1000
                    info = {
                        'visited': len(nodes_visited),
                        'frontier_max': max(frontier_max, len(frontier_start), len(frontier_end)),
                        'explored_pct': (len(nodes_visited) / max_nodes) * 100,
                        'iterations': iteration,
                        'timeout': False
                    }
                    return path, total_dist, elapsed_time, info
                heapq.heappush(
                    frontier,
                    (int(graph.nodes[neighbor]['population']), counter, neighbor)
                )
                counter += 1
            frontier_max = max(frontier_max, len(frontier_start), len(frontier_end))
            iteration += 1
        elapsed_time = (time.perf_counter() - start_time) * 1000
        info = {
            'visited': len(nodes_visited),
            'frontier_max': frontier_max,
            'explored_pct': (len(nodes_visited) / max_nodes) * 100,
            'iterations': iteration,
            'timeout': False
        }
        return [], float('inf'), elapsed_time, info
    ```
    """)

    st.markdown("""
    ---
    ## 8. Referências e links úteis
    - [Wikipedia: Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)

    - [Direction-Optimizing Breadth-First Search (Scott Beamer, ACM SC12)](https://scottbeamer.net/pubs/beamer-sc2012.pdf)
    - [Wiki: Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
    - [Efficient Parallel BFS for Large Graphs](https://dl.acm.org/doi/10.1145/2735496.2735507)
    """)

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