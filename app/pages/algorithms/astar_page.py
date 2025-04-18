import streamlit as st
import os

def app():
    st.title("Algoritmo A* (A-Estrela) — Estado da Arte")

    st.markdown(r"""
    ## 1. O que é o algoritmo A*?
    
    O algoritmo A* (A-Estrela) é o principal método de busca informada usado para encontrar caminhos ótimos em grafos, combinando as forças da busca gulosa (heurística) e da busca de custo uniforme (Dijkstra). Desenvolvido em 1968 por Hart, Nilsson e Raphael, tornou-se padrão em sistemas de navegação, planejamento de robôs e jogos por sua eficiência e garantias de otimalidade.

    O A* utiliza esta função de avaliação para decidir qual nó expandir:

    $$f(n) = g(n) + h(n)$$

    - $g(n)$: custo real acumulado do início até o nó $n$
    - $h(n)$: heurística — estimativa do custo do nó $n$ até o destino

    O nó com menor $f(n)$ no momento é expandido, promovendo um equilíbrio eficiente entre custo já pago e o restante. A qualidade e a admissibilidade da heurística são fatores críticos para o sucesso do A*.

    ### Características Modernas e Estado da Arte

    - **Completo**: Sempre encontra uma solução, se ela existir em grafos finitos.
    - **Ótimo**: Caminho mais curto garantido se a heurística for admissível e arestas positivas.
    - **Altamente eficiente**: Um conjunto robusto de variantes e otimizações tornou o A* aplicável até mesmo em mapas globais.
    - **Heurística ajustável**: Pode-se incorporar múltiplas heurísticas e até definir mecanismos para escolher a melhor estimativa por contexto.
    - **Tiebreakers avançados**: Critérios compostos (como grau, população, prioridade lexicográfica, randomização controlada) podem ser usados para reduzir empates e acelerar a solução.
    - **Logging e profiling**: Implementações modernas fornecem métricas detalhadas da busca (nós expandidos, profundidade, tempo, memória), essenciais para tuning e análise.
    - **Complexidade**: Pior caso O(b^d), mas na prática frequentemente muito melhor se a heurística for forte.

    ---
    """)

    cols = st.columns([1, 1])
    with cols[0]:
        st.markdown("### Pseudocódigo")
        st.code("""
A*(grafo, inicio, fim, h):
    abertos ← fila de prioridade vazia
    fechados ← conjunto de nós já explorados
    g[inicio] ← 0
    f[inicio] ← h(inicio, fim)
    abertos.inserir(inicio, prioridade=f[inicio])
    pai ← dicionário vazio

    enquanto abertos não estiver vazia:
        atual ← abertos.retirar_nó_de_menor_f

        se atual == fim:
            return reconstruir_caminho(pai, inicio, fim)

        fechados.adicionar(atual)
        
        para vizinho em vizinhos_de(atual):
            se vizinho em fechados:
                continuar

            custo_g ← g[atual] + custo(atual, vizinho)

            se vizinho não em abertos ou custo_g < g[vizinho]:
                g[vizinho] ← custo_g
                f[vizinho] ← g[vizinho] + h(vizinho, fim)
                pai[vizinho] ← atual
                abertos.atualizar(vizinho, prioridade=f[vizinho])
        
    retornar "Caminho não encontrado"
        """, language="python")

    with cols[1]:
        st.write("### ")
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/9/98/AstarExampleEn.gif",
            caption="Visualização do funcionamento do algoritmo A*",
            width=630
        )

    st.markdown(r"""
    ### 1.1 Heurísticas modernas em A*

    - **Distância Euclidiana**: útil em grades ou mapas 2D.
    - **Distância de Manhattan**: para grades com movimentos ortogonais.
    - **Distância de Haversine**: padrão para mapas geográficos (globais).
    - **Landmark/ALT**: usa pontos de referência e desigualdade triangular para obtenção de heurísticas próximas ao ótimo, amplamente utilizado em sistemas de rotas reais (ex: OpenRouteService, OSRM).
    - **Combinação máxima**: combinar múltiplas heurísticas admissíveis com $h(n) = \max(h_1(n), h_2(n), ..., h_k(n))$ potencializa a eficiência.
    - **Chebyshev, Octil e outros**: para domínios específicos de movimentação.

    #### Propriedades fundamentais

    - **Admissibilidade:** Não superestima o custo real. Garante otimalidade.
    - **Consistência/Monotonicidade:** Garante que, ao expandir um nó, todos os seus vizinhos terão $f$ não decrescente. Fundamental para evitar o reprocessamento.
    - **Dominância:** Quanto maior e mais informada a heurística (sem deixar de ser admissível), menos nós serão expandidos.

    ---
    """)

    st.markdown(r"""
    ### 1.2 Variantes e otimizações estado da arte

    - **IDA***: Reduz drasticamente o uso de memória sem perder otimalidade.
    - **SMA***: Garante funcionamento sob limitação extrema de memória.
    - **Weighted A***: Usa $f(n) = g(n) + w*h(n)$ (w>1) para priorizar velocidade sobre otimalidade quando desejado.
    - **Bidirectional A***: Executa A* do início e do fim, encontrando-se no meio — usado em mapas extensos.
    - **ALT/Landmark A***: Usa pré-processamento de pontos-chave do grafo para estimativas rápidas e agressivas.
    - **Anytime A***: rapidamente encontra uma solução subótima e a refina conforme há tempo disponível.
    - **Jump Point Search/JPS**: reduz a expansão redundante em grades.
    - **Tiebreakers compostos**: desempate por múltiplos critérios, reduzindo bifurcações e ciclos.

    ---
    """)

    st.markdown("""
    ## 2. Aplicações modernas do A*

    - **Navegação GPS e trânsito:** Algoritmo base de Google Maps, Waze, Here, Apple Maps.
    - **Sistemas logísticos e transporte:** Otimiza rotas para frota, entregas multi-ponto, previsão de tempo, recursos.
    - **Jogos e entretenimento:** Pathfinding em jogos 2D, 3D, IA de NPCs; movement tático em simulações.
    - **Robótica e drones:** Planejamento de trajeto, navegação dinâmica, SLAM.
    - **Redes e comunicação:** Planejamento e roteamento em redes de computadores e telecomunicações.
    - **Outras áreas:** Design de circuitos, bioinformática, inteligência espacial e militar.
    """)

    st.markdown("""
    ## 3. Vantagens e Desvantagens Estado da Arte

    ### Vantagens

    - **Eficiência superior**: Drástica redução do espaço explorado em relação a buscas não informadas.
    - **Otimalidade garantida**: Desde que heurística seja admissível.
    - **Personalização total**: Fácil adaptação de custos, restrições, multiobjetivo.
    - **Escalabilidade**: Pode ser aplicado a grafos continentais (com variantes ALT).
    - **Logging/profiling avançado**: Diagnóstico detalhado para tuning de performance.
    - **Versões paralelas/concorrentes**: Muitas otimizações paralelas disponíveis para grandes sistemas.

    ### Desvantagens

    - **Dependente da heurística**: Heurística ruim faz com que se aproxime de Dijkstra (pior performance).
    - **Uso potencialmente alto de memória**: Particularmente na versão padrão em grafos densos ou grandes.
    - **Implementação avançada requer expertise**: Tuning e variantes exigem domínio do problema.
    - **Menos robusto em caminhos com restrições complexas/dinâmicas (se comparado a abordagens especializadas).**
    - **Performance sensível ao domínio e estrutura do grafo**.

    ---
    """)

    st.markdown("""
    ## 4. Comparação com outros algoritmos

    | Critério                 | A*                          | Dijkstra                   | BFS                 | DFS              | Busca Fuzzy        |
    |--------------------------|-----------------------------|----------------------------|---------------------|------------------|--------------------|
    | Heurística               | Sim, $h(n)$                 | Não                        | Não                 | Não              | Não tradicional    |
    | Otimalidade              | Sim (c/ heur. admissível)   | Sim (pesos positivos)      | Sim (arestas un)    | Não              | Subjetiva/multiobj |
    | Performance tip. real    | Excelente                   | Boa                        | Baixa               | Baixa            | Moderada           |
    | Performance em grafos exp| Muito boa (boa heurística)  | Média                      | Ruim                | Variável         | Moderada/Alta      |
    | Uso de memória           | Médio                       | Médio                      | Alto                | Baixo            | Variável           |
    | Aplicação ideal          | Grafos grandes, navegação   | Grafos ponderados gerais   | Grafos não ponderados| Exploração rápida| Multiobjetivo      |
    | Adaptabilidade           | Alta                        | Média                      | Baixa               | Baixa            | Alta               |
    | Logging/Profile disponível| Sim                        | Sim                        | Sim                 | Sim              | Depende            |

    """)

    st.markdown("""
    ### Notas e Prática Avançada

    [1] A busca gulosa (greedy) foca apenas em h(n), podendo ser ágil mas subótima.
    [2] Dijkstra foca apenas em g(n), garantido porém pode ser lento.
    [3] Performance do A* depende drasticamente de heurística — a escolha ou combinação de heurísticas pode ser o divisor de águas (combinação máxima, landmarks).
    [4] Tiebreakers compostos podem evitar a expansão irracional quando múltiplos caminhos têm custo similar.
    [5] O uso de logs detalhados e benchmarking ajuda no tuning prático e comparativo do A* frente a outros algoritmos.
    [6] O A* pode ser implementado com filas de prioridade altamente otimizadas, e pode ser paralelizado.
    [7] Estatísticas detalhadas (nós expandidos, tempo, memória) são práticas comuns para pesquisa e produção.

    *Estado de junho de 2024 – este relatório reflete as melhores práticas e tendências reportadas em Wikipedia, literatura recente e sistemas industriais modernos utilizados em larga escala.*
    """)