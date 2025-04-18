import streamlit as st
import os

def app():
    st.title("Algoritmo de Dijkstra - Caminho de Menor Distância")
    
    st.markdown(r"""
    ## 1. O que é o algoritmo de Dijkstra?
    
    O algoritmo de Dijkstra é um método para encontrar o caminho mais curto entre nós em um grafo com pesos 
    não-negativos. Este algoritmo, criado pelo cientista da computação holandês Edsger W. Dijkstra em 1956, 
    é amplamente utilizado em problemas de roteamento.
    
    Dijkstra resolve o problema do caminho mais curto de origem única para grafos com pesos de arestas não-negativos,
    produzindo uma árvore de caminhos mais curtos. O algoritmo funciona iterativamente, selecionando sempre o vértice
    não visitado com a estimativa de distância mínima, calculando as distâncias através dele a cada vizinho, e atualizando
    as estimativas de distância dos vizinhos se um caminho mais curto for encontrado.
    
    Em termos formais, para um grafo G = (V, E) com função de peso w: E → [0, ∞), o algoritmo encontra os caminhos
    mais curtos de um vértice de origem s ∈ V para todos os outros vértices do grafo.
                
    ### Características principais
    
    - **Completo**: Sempre encontra uma solução se ela existir.
    - **Ótimo**: Garante encontrar o caminho de menor distância total.
    - **Eficiente com heurística de prioridade**: Usando heaps binários, alcança complexidade O(E log V).
    - **Aplicável apenas a grafos com pesos não-negativos**.
    - **Base para vários outros algoritmos**: Incluindo algoritmos de roteamento em redes, planejamento de viagens e GPS.
    """)
    
    # Layout para pseudocódigo e imagem (lado a lado)
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo")
        st.code("""
Dijkstra(grafo, inicio, fim):
    # Inicialização
    dist[v] ← INFINITO para cada vértice v
    dist[inicio] ← 0
    visitados ← conjunto vazio
    pq ← fila de prioridade com (0, inicio)
    
    enquanto pq não estiver vazia:
        # Pegar vértice com menor distância
        (d, u) ← extrair mínimo de pq
        
        # Se já processamos este vértice ou chegamos ao destino
        se u em visitados ou u == fim:
            continuar
        
        # Marcar como visitado
        adicionar u a visitados
        
        # Processo de relaxamento das arestas
        para cada aresta (u, v) com peso w:
            se dist[u] + w < dist[v]:
                dist[v] ← dist[u] + w
                pai[v] ← u
                inserir (dist[v], v) em pq
                
    # Reconstruir caminho do fim ao início
    se fim em pai:
        return reconstruir_caminho(pai, inicio, fim)
    senão:
        return "Caminho não encontrado"
        """, language="python")

    with cols[1]:
        st.markdown("##### ")
        # Definindo largura fixa para controlar o tamanho
        image_width = 630  # Largura em pixels para padronizar com outros algoritmos
        
        # Usando width diretamente no st.image para controlar o tamanho
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/5/57/Dijkstra_Animation.gif",
            caption="Visualização do algoritmo de Dijkstra",
            width=image_width  # Controle direto da largura
        )
      
    # Fundamentos teóricos de Dijkstra
    st.markdown(r"""
    ### 1.1 Fundamentos teóricos do algoritmo de Dijkstra
    
    O algoritmo de Dijkstra baseia-se em alguns conceitos fundamentais:
    
    1. **Princípio de otimalidade de Bellman**: Estabelece que os subcaminhos de caminhos de custo mínimo também são caminhos 
    de custo mínimo. Formalmente, se p* é um caminho ótimo de s a t, e se p* passa por v, então a parte de p* de s a v é um 
    caminho ótimo de s a v, e a parte de v a t é um caminho ótimo de v a t.
    
    2. **Invariante do algoritmo**: Em qualquer iteração do algoritmo, para cada vértice v ∈ V, o valor d[v] é o custo do 
    caminho mais curto encontrado até agora de s a v. Após o algoritmo terminar, d[v] = δ(s,v) para cada v ∈ V, onde δ(s,v) 
    é o custo do caminho mínimo de s a v.
    
    3. **Relaxação de arestas**: A operação de relaxação tenta melhorar o melhor caminho conhecido para v usando a aresta (u,v):
    
    $$\text{Se } d[v] > d[u] + w(u,v) \text{ então } d[v] = d[u] + w(u,v)$$
    
    4. **Prova de correção**: A correção do algoritmo de Dijkstra depende criticamente da não-negatividade dos pesos das arestas, 
    pois garante que um vértice, uma vez visitado (i.e., sua aresta de menor peso relaxada), não precisa ser revisitado.
    
    5. **Critério de parada ótima**: Uma otimização comum é interromper o algoritmo quando o vértice de destino é visitado, 
    pois nesse momento o caminho mais curto até esse vértice já foi encontrado.
    """)
    
    # Implementações e variantes
    st.markdown(r"""
    ### 1.2 Implementações eficientes e variantes de Dijkstra
    
    1. **Implementação com fila de prioridade (heap binário)**: Reduz a complexidade para O(E log V) onde E é o número de arestas 
    e V é o número de vértices. Cada operação de fila tem custo O(log V).
    
    2. **Implementação com heap de Fibonacci**: Melhora a complexidade teórica para O(V log V + E), particularmente útil em grafos 
    esparsos onde E é proporcional a V.
    
    3. **Dijkstra bidirecional**: Executa duas buscas simultaneamente - uma a partir da origem e outra a partir do destino. 
    Quando as fronteiras se encontram, um caminho completo é encontrado. Isso pode reduzir significativamente o número de nós explorados.
    
    4. **Delta-stepping**: Uma variante paralela que agrupa vértices em "baldes" baseados nas suas distâncias da origem.
    
    5. **A* com heurística zero**: O algoritmo A* se reduz a Dijkstra quando a função heurística h(v) = 0 para todos os vértices v.
    
    6. **Dijkstra com limite (bounded Dijkstra)**: Limita a busca a vértices dentro de uma certa distância da origem.
    
    7. **Dijkstra hierárquico**: Utiliza uma representação hierárquica do grafo para acelerar o cálculo em redes grandes como mapas rodoviários.
    """)
    
    # Aplicações e casos de uso
    st.markdown("""
    ## 2. Aplicações do Dijkstra
    
    1. **Roteamento em redes de computadores**:
       - Protocolos de roteamento como OSPF (Open Shortest Path First) 
       - Cálculo de caminhos de menor latência entre nós de rede
       - Balanceamento de carga em infraestruturas de rede distribuídas
    
    2. **Sistemas de navegação e GPS**:
       - Cálculo de rotas de menor distância ou tempo entre localizações
       - Roteamento em tempo real considerando condições de tráfego atuais
       - Planejamento de rotas multimodais (combinando diferentes meios de transporte)
    
    3. **Telecomunicações**:
       - Planejamento de redes de fibra óptica otimizando custo e tempo de transmissão
       - Roteamento de chamadas em redes telefônicas
       - Otimização de redes sem fio e posicionamento de torres
    
    4. **Logística e planejamento urbano**:
       - Otimização de rotas para frotas de veículos
       - Análise de acessibilidade em planejamento urbano
       - Simulação de fluxo de transporte para mitigação de congestionamentos
    
    5. **Aplicações em robótica**:
       - Planejamento de trajetórias para robôs em ambientes conhecidos
       - Navegação autônoma com consideração de obstáculos
       - Mapeamento e exploração de ambientes
    
    6. **Sistemas biológicos e ciência da computação**:
       - Análise de redes metabólicas e vias de sinalização celular
       - Sequenciamento de DNA e alinhamento de sequências
       - Modelagem de propagação de doenças em redes sociais
    """)
    
    # Vantagens e desvantagens
    st.markdown("""
    ## 3. Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    
    - **Otimalidade garantida**: Encontra sempre o caminho de menor distância total
    - **Flexibilidade na definição de custos**: Pode considerar distância, tempo, dinheiro ou combinações destes
    - **Base matemática sólida**: Algoritmo bem estudado com provas formais de correção
    - **Eficiência prática**: Com as estruturas de dados apropriadas, é suficientemente rápido para aplicações reais
    - **Adaptabilidade**: Pode ser facilmente modificado para calcular caminhos alternativos ou considerar restrições adicionais
    - **Ampla aplicabilidade**: Funciona em qualquer grafo com pesos não-negativos
    
    ### Desvantagens
    
    - **Incapacidade de lidar com pesos negativos**: Falha em grafos com arestas de peso negativo
    - **Exploração excessiva em algumas situações**: Explora em todas as direções, mesmo que o destino esteja em uma direção específica
    - **Consumo de memória**: Requer armazenamento de distâncias para todos os vértices
    - **Dificuldade com critérios múltiplos**: Não é naturalmente adaptado para otimização multiobjetivo
    - **Sensibilidade a mudanças dinâmicas**: Precisa ser recalculado completamente se os pesos das arestas mudarem
    - **Limitação para grandes redes**: Pode ter desempenho degradado em grafos extremamente grandes sem otimizações adicionais
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## 4. Comparação com outros algoritmos
    
    | Critério | Dijkstra | BFS | DFS | A* | Fuzzy |
    |----------|----------|-----|-----|----|----|
    | **Princípio básico** | Menor caminho | Exploração em largura | Exploração em profundidade | Heurística + custo real | Graus de pertinência |
    | **Otimização** | Distância total | Número de paradas | Nenhuma garantia | Distância com heurística | Multiobjetivo com incertezas |
    | **Completude** | Sim | Sim (espaço finito) | Sim (com controle de ciclos) | Sim | Depende da implementação |
    | **Otimalidade** | Sim (pesos positivos) | Sim (em arestas) | Não | Sim (com heurística admissível) | Não (subjetiva) |
    | **Considera pesos das arestas** | Sim | Não | Não | Sim | Sim, como graus de pertinência |
    | **Funciona com pesos negativos** | Não | N/A | N/A | Não | Sim |
    | **Complexidade temporal** | O(E + V log V) | O(V + E) | O(V + E) | O(E log V) - varia com heurística | O(E log V) com overhead fuzzy |
    | **Complexidade espacial** | O(V) | O(V) | O(V) | O(V) | O(V) |
    | **Eficiência em grafos densos** | Boa | Ruim | Variável | Média | Média |
    | **Eficiência em grafos esparsos** | Excelente | Boa | Boa | Excelente | Boa |
    | **Adequação para routing em tempo real** | Boa | Limitada | Inadequada | Excelente | Moderada |
    | **Paralelizável** | Dificilmente | Facilmente | Dificilmente | Parcialmente | Parcialmente |
    | **Aplicação típica** | Minimização precisa de distância | Menor número de etapas | Exploração com memória limitada | Rotas com boa heurística | Ambientes incertos, multiobjetivo |
    """)

    # # Carregar conteúdo adicional do arquivo markdown se existir
    # report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    #                           "reports", "dijkstra_report.md")
    
    # if os.path.exists(report_path):
    #     with open(report_path, 'r', encoding='utf-8') as f:
    #         report_content = f.read()
            
    #     st.markdown("## 5. Relatório detalhado sobre Dijkstra")
    #     st.markdown(report_content)
    # else:
    #     st.info("Um relatório detalhado sobre o algoritmo de Dijkstra ainda não foi criado. Aqui está mais informação:")
        
    st.markdown(r"""
    ## 5. Otimizações e implementações avançadas
    
    ### 5.1 Otimizações no algoritmo Dijkstra
    
    1. **Otimização de entrada/saída da fila de prioridade**: Uma implementação cuidadosa pode reduzir o número de operações de 
    atualização da fila de prioridade, que são tipicamente as operações mais custosas.
    
    2. **Dijkstra com relaxamento adaptativo**: Atualizações em lote das distâncias, reduzindo o número de operações de reorganização na fila de prioridade.
    
    3. **Goal-directed search (busca direcionada ao objetivo)**: Usando potenciais (semelhante à heurística do A*, mas preservando a otimalidade), pode-se
    direcionar a busca para o destino, reduzindo o número de nós explorados.
    
    4. **ALT (A*, Landmarks, and Triangle inequality)**: Usa pontos de referência (landmarks) e a desigualdade triangular para criar heurísticas admissíveis.
    
    5. **Contraction Hierarchies**: Pré-processamento que contrai o grafo hierarquicamente, permitindo buscas muito mais rápidas em tempo de execução.
    
    6. **Arc Flags**: Divide o grafo em regiões e marca cada aresta com as regiões para as quais ela pode estar em um caminho mais curto.
    
    7. **Transit Node Routing**: Identifica "nós de trânsito" que estão em muitos caminhos de longa distância e pré-calcula caminhos entre eles.
    
    ### 5.2 A implementação em nosso projeto
    
    O algoritmo `shortest_path_min_distance` implementado neste projeto é uma versão otimizada do Dijkstra com duas melhorias importantes:
    
    1. **Desempate por população**: Quando dois caminhos têm a mesma distância, o algoritmo prefere passar por cidades com menor população acumulada.
    Isso é implementado através de uma tupla de prioridade (distância, população_acumulada) na fila de prioridade.
    
    2. **Rastreamento de caminho embutido**: Em vez de apenas calcular distâncias e depois reconstruir o caminho, nossa implementação mantém o caminho completo 
    durante a execução, facilitando a obtenção do resultado final e permitindo análises intermediárias.
    
    Matematicamente, a função de prioridade pode ser expressa como:
    
    $$\text{prioridade}(v) = (d[v], \sum_{u \in \text{caminho até } v} \text{população}(u))$$
    
    Onde a comparação é lexicográfica: primeiro por distância e, em caso de empate, por população acumulada.
    """)
    
    # Notas técnicas adicionais
    st.markdown(r"""
    ### Notas
    
    [1] **Prova de correção do algoritmo de Dijkstra**: A prova se baseia na propriedade de que, quando um vértice v é adicionado 
    ao conjunto de vértices visitados, temos d[v] = δ(s,v), ou seja, já encontramos o caminho mais curto até v. Isso é verdade porque:
    
    a) Inicialmente, d[s] = 0 = δ(s,s)
    
    b) Para qualquer vértice v adicionado ao conjunto de visitados, se houvesse um caminho mais curto, este teria que passar por 
    algum vértice w que ainda não foi visitado. Mas se w ainda não foi visitado, então δ(s,w) ≥ d[v] (pela propriedade de seleção 
    do vértice com menor distância). E como todos os pesos são não-negativos, o caminho de s para v passando por w teria um custo 
    δ(s,w) + peso(w,v) ≥ d[v], contradizendo nossa suposição.
    
    [2] **Complexidade em diferentes estruturas de dados**:
    
    - Busca linear na lista de vértices não visitados: O(V²)
    - Heap binário: O(E log V)
    - Heap de Fibonacci: O(V log V + E)
    - Heap de van Emde Boas para grafos com pesos inteiros pequenos: O(E log log C), onde C é o maior peso
    
    [3] **Extensão para caminhos de k-ésimo menor custo**: O algoritmo pode ser adaptado para encontrar não apenas o caminho mais curto, 
    mas também o segundo, terceiro, ..., k-ésimo caminho mais curto, usando variantes como o algoritmo de Yen ou o algoritmo de 
    Eppstein.
    
    [4] **Relação com outros algoritmos**: Dijkstra é um caso especial do algoritmo de Ford-Bellman quando não há arestas negativas, 
    e do algoritmo A* quando a heurística é nula. Também está intimamente relacionado ao algoritmo de Prim para árvores de extensão mínima.
    
    [5] **Aplicação prática em roteamento de rede**: Em protocolos como OSPF e IS-IS, cada roteador executa uma variante do algoritmo de Dijkstra 
    para construir sua tabela de roteamento, considerando métricas como capacidade do link, latência, e carga atual.
    
    [6] **Limitações em ambientes dinâmicos**: Em redes onde os pesos das arestas mudam frequentemente (ex: tráfego urbano), 
    são necessárias adaptações como recálculo parcial ou algoritmos incrementais que atualizam apenas as partes afetadas da solução.
    """)