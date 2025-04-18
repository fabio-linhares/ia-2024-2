import streamlit as st
import os

def app():
    st.title("Algoritmo A* (A-Estrela)")
    
    st.markdown(r"""
    ## 1. O que é o algoritmo A*?
    
    O algoritmo A* (A-Estrela) é um algoritmo clássico de busca informada que combina as vantagens da busca 
    gulosa[1] (que busca o caminho que parece ser o melhor) e da busca de custo uniforme[2] (que encontra
    o caminho de menor custo). Foi desenvolvido em 1968 por Peter Hart, Nils Nilsson e Bertram Raphael no SRI International
    como uma extensão do algoritmo de Dijkstra, incorporando heurísticas para melhorar o desempenho.
    
    O A* utiliza a seguinte função de avaliação para determinar a prioridade de exploração de cada nó:
    
    $$f(n) = g(n) + h(n)$$
    
    Onde:
    
    - $g(n)$ é o custo do caminho do nó inicial até o nó atual $n$ (o caminho já percorrido)
    - $h(n)$ é uma heurística que estima o custo do caminho do nó $n$ até o objetivo (uma estimativa do que ainda falta)
    
    **Consequentemente**: o algoritmo prioriza sempre explorar o nó com menor valor de $f(n)$, equilibrando eficientemente
    o custo real já acumulado com uma estimativa informada do que falta para alcançar o destino.
                
    ### Características principais
    
    - **Completo**: Sempre encontra uma solução se ela existir, desde que o grafo seja finito.
    - **Ótimo**: Encontra o caminho de menor custo se a heurística for admissível (não superestimar o custo real).
    - **Eficiente**: Usa a heurística para guiar a busca e reduzir significativamente o espaço explorado.
    - **Consistência**: Se a heurística for consistente (ou monótona), o algoritmo não precisará reabrir nós já explorados.
    - **Complexidade**: No pior caso, O(b^d) onde b é o fator de ramificação e d é a profundidade da solução.
    """)
    
    # Layout para pseudocódigo e imagem (lado a lado)
    # st.subheader("Implementação e Visualização")
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo")
        st.code("""
A*(grafo, inicio, fim, h):
    abertos ← PriorityQueue()  # nós a serem explorados
    fechados ← {}               # nós já explorados
    g[inicio] ← 0               # custo do caminho do início até o nó
    f[inicio] ← h(inicio, fim)  # estimativa de custo total
    abertos.adicionar(inicio, prioridade=f[inicio])
    pai ← dicionário vazio
    
    enquanto abertos não estiver vazia:
        atual ← abertos.remover()  # nó com menor valor de f
        
        se atual == fim:
            return reconstruir_caminho(pai, inicio, fim)
        
        adicionar atual a fechados
        
        para cada vizinho de atual no grafo:
            se vizinho estiver em fechados:
                continuar
                
            custo_g ← g[atual] + custo(atual, vizinho)
            
            se vizinho não estiver em abertos:
                g[vizinho] ← custo_g
                f[vizinho] ← g[vizinho] + h(vizinho, fim)
                pai[vizinho] ← atual
                abertos.adicionar(vizinho, prioridade=f[vizinho])
            senão se custo_g < g[vizinho]:  # encontramos um caminho melhor
                g[vizinho] ← custo_g
                f[vizinho] ← g[vizinho] + h(vizinho, fim)
                pai[vizinho] ← atual
                # Atualiza a prioridade do vizinho na fila
                abertos.atualizar(vizinho, prioridade=f[vizinho])
            
    return "Caminho não encontrado"
        """, language="python")

    with cols[1]:
        # Centralizando verticalmente para melhor alinhamento com o pseudocódigo
        st.write("### ")  # Espaço em branco para alinhamento vertical
        
        # Definindo largura fixa para controlar o tamanho
        image_width = 630  # Largura em pixels
        
        # Usando width diretamente no st.image para controlar o tamanho
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/9/98/AstarExampleEn.gif",
            caption="Visualização do algoritmo A*",
            width=image_width  # Controle direto da largura
        )
       
    # Heurísticas
    st.markdown(r"""
    ### 1.1 Heurísticas comuns para o algoritmo A*
    
    No contexto de busca de caminhos entre cidades, as heurísticas mais comuns incluem:
    
    1. **Distância Euclidiana**: Linha reta entre dois pontos no plano.
       $$h(n) = \sqrt{(n_x - destino_x)^2 + (n_y - destino_y)^2}$$
    
    2. **Distância de Manhattan**: Soma dos valores absolutos das diferenças das coordenadas, útil em malhas urbanas com ruas em grade.
       $$h(n) = |n_x - destino_x| + |n_y - destino_y|$$
    
    3. **Distância de Haversine**: Para calcular distâncias geodésicas em uma esfera (como o planeta Terra).
       $$h(n) = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{lat_2-lat_1}{2}\right) + \cos(lat_1) \cdot \cos(lat_2) \cdot \sin^2\left(\frac{lon_2-lon_1}{2}\right)}\right)$$
       onde R é o raio da Terra (aproximadamente 6371 km)
    
    4. **Distância de Chebyshev**: Máximo das diferenças absolutas das coordenadas (útil para movimento em 8 direções em grades).
       $$h(n) = \max(|n_x - destino_x|, |n_y - destino_y|)$$
    
    5. **Distância Octil**: Combinação ponderada de movimentos diagonais e retos (útil em grades com movimento diagonal).
       $$h(n) = \max(|n_x - destino_x|, |n_y - destino_y|) + (sqrt(2)-1) \cdot \min(|n_x - destino_x|, |n_y - destino_y|)$$
    """)
    
    # Propriedades da heurística
    st.markdown(r"""
    ### 1.2 Propriedades importantes das heurísticas
    
    **Admissibilidade**: Uma heurística é admissível se nunca superestima o custo real para atingir o objetivo.
    Formalmente, para todo nó n:
    
    $$h(n) \leq h^*(n)$$
    
    Onde $h^*(n)$ é o custo real do caminho ótimo de n até o objetivo.
    
    **Consistência (ou Monotonicidade)**: Uma heurística é consistente se satisfaz a desigualdade triangular:
    
    $$h(n) \leq d(n, n') + h(n')$$
    
    Para todo nó n e seu sucessor n', onde d(n, n') é o custo para ir de n a n'.
    
    **Dominância**: Uma heurística h₁ domina outra heurística h₂ se:
    
    $$h_1(n) \geq h_2(n)$$
    
    Para todo nó n. Heurísticas dominantes resultam em menos expansões de nós.
    
    **Observação**: Toda heurística consistente é também admissível, mas nem toda heurística admissível é consistente.
    """)
    
    # Variantes especializadas do A*
    st.markdown(r"""
    ### 1.3 Variantes e otimizações do A*
    
    1. **IDA* (Iterative Deepening A*)**: Usa menos memória que o A* tradicional, realizando buscas com aprofundamento iterativo e limite de custo crescente.
    
    2. **SMA* (Simplified Memory-Bounded A*)**: Limita o uso de memória descartando estrategicamente os nós menos promissores quando a memória se esgota.
    
    3. **Weighted A* (A* Ponderado)**: Modifica a função f(n) para:
       $$f(n) = g(n) + w \cdot h(n)$$
       onde w > 1 é um peso que favorece a heurística, acelerando a busca à custa de potencialmente perder a otimalidade.
    
    4. **Anytime Weighted A*** (AWA*): Começa com um alto valor de w e o reduz gradualmente, produzindo soluções progressivamente melhores.
    
    5. **Bidirectional A***: Conduz duas buscas simultaneamente: uma do início ao destino e outra do destino ao início, encontrando-se no meio.
    
    6. **Jump Point Search (JPS)**: Otimização específica para grades, identifica "pontos de salto" para pular nós intermediários simétricos.
    
    7. **Hierarchical A***: Utiliza abstrações hierárquicas do espaço de busca, resolvendo primeiro uma versão simplificada do problema.
    """)
    
    # Aplicações e casos de uso
    st.markdown("""
    ## 2. Aplicações do A*
    
    1. **Sistemas de navegação GPS e serviços de mapeamento**:
       - Encontrar rotas mais curtas entre cidades com restrições reais (pedágios, congestionamentos)
       - Algoritmo fundamental no Google Maps, Waze, Apple Maps e outros serviços de navegação
       - Roteamento dinâmico com atualização de tráfego em tempo real
    
    2. **Planejamento de rotas logísticas e otimização**:
       - Entregas em múltiplos pontos com minimização de distância e tempo
       - Roteamento de veículos com restrições de capacidade, janelas de tempo e custos variáveis
       - Sistemas de gerenciamento de frotas para empresas de transporte
    
    3. **Jogos e simulações**:
       - Sistemas de pathfinding para NPCs em jogos (desde Age of Empires até jogos modernos como Civilization)
       - Movimento de personagens evitando obstáculos em ambientes dinâmicos
       - Simulações militares e modelagem de comportamento tático
    
    4. **Robótica e veículos autônomos**:
       - Planejamento de trajetórias para robôs e drones
       - Navegação em tempo real em ambientes desconhecidos ou parcialmente conhecidos
       - Sistemas SLAM (Simultaneous Localization and Mapping) em carros autônomos
    
    5. **Redes de comunicação e internet**:
       - Roteamento de pacotes de dados com múltiplas restrições (latência, largura de banda)
       - Planejamento de topologia de rede
       - Balanceamento de carga em datacenters distribuídos
    """)
    
    # Vantagens e desvantagens
    st.markdown("""
    ## 3. Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    
    - **Eficiência superior**: Explora significativamente menos nós que algoritmos não informados como Dijkstra
    - **Otimalidade garantida**: Encontra o caminho mais curto se a heurística for admissível
    - **Flexibilidade**: Pode incorporar várias restrições e preferências através de funções de custo personalizadas
    - **Balanceamento ajustável**: Pode favorecer exploração (menor peso na heurística) ou velocidade (maior peso)
    - **Adaptabilidade a diferentes domínios**: Funciona bem tanto em espaços contínuos quanto discretos
    - **Paralelizável**: Pode ser implementado em versões paralelas para maior desempenho
    
    ### Desvantagens
    
    - **Dependência da qualidade da heurística**: O desempenho degrada significativamente com heurísticas ruins
    - **Consumo de memória**: Pode armazenar um grande número de nós para grafos complexos
    - **Complexidade de implementação**: Requer estruturas de dados eficientes como filas de prioridade
    - **Sensibilidade ao fator de ramificação**: Performance pode deteriorar em grafos muito densos
    - **Limitações em ambientes muito dinâmicos**: Pode requerer recálculos frequentes se o ambiente muda rapidamente
    - **Dificuldade com restrições complexas**: Algoritmos especializados podem ser melhores para certos tipos de restrições
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## 4. Comparação com outros algoritmos
    
    | Critério | A* | Dijkstra | BFS | DFS | Fuzzy |
    |----------|----|----------|-----|-----|-------|
    | **Princípio básico** | Heurística + custo real | Menor caminho | Exploração em largura | Exploração em profundidade | Graus de pertinência |
    | **Otimização** | Distância total com heurística | Distância total | Número de paradas | Nenhuma garantia | Multiobjetivo com incertezas |
    | **Capacidade de adaptação** | Média | Baixa | Nenhuma | Nenhuma | Alta |
    | **Considera domínio específico** | Sim, via heurística | Não | Não | Não | Sim, via funções de pertinência |
    | **Garantia de otimalidade** | Sim (com heurística admissível) | Sim (pesos positivos) | Sim (distância em arestas) | Não | Não (subjetiva) |
    | **Complexidade temporal** | O(b^d) - depende da heurística | O(E + V log V) | O(b^d) | O(b^d) | O(b^d) com overhead fuzzy |
    | **Complexidade espacial** | Média-alta | Média | Alta | Baixa | Alta |
    | **Consumo de memória** | Médio-alto | Médio | Alto | Baixo | Alto |
    | **Aplicação ideal** | Rotas mais curtas com boa heurística | Minimização precisa de distância | Conexões uniformes | Exploração com memória limitada | Ambientes incertos, multiobjetivo |
    | **Performance em grafos densos** | Boa | Média | Ruim | Boa em profundidade | Média |
    | **Performance em grafos esparsos** | Excelente | Boa | Boa | Variável | Boa |
    | **Paralelizável** | Parcialmente | Dificilmente | Facilmente | Dificilmente | Parcialmente |
    """) 

    # # Carregar conteúdo adicional do arquivo markdown se existir
    # report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    #                           "reports", "a_star_report.md")
    
    # if os.path.exists(report_path):
    #     with open(report_path, 'r', encoding='utf-8') as f:
    #         report_content = f.read()
            
    #     st.markdown("## 5. Relatório detalhado sobre A*")
    #     st.markdown(report_content)
    # else:
    #     st.warning("Relatório detalhado sobre A* não encontrado.")

    st.markdown("""
    ### Notas

    [1] A busca gulosa (greedy search) é um algoritmo que sempre toma a decisão que parece ser a melhor 
    naquele exato momento, baseando-se apenas na heurística, sem considerar o custo real acumulado.
    Formalmente, usa a função f(n) = h(n), ignorando completamente g(n). Isso frequentemente leva a 
    caminhos subótimos, mas pode ser computacionalmente mais rápida. É análoga a uma pessoa que sempre 
    caminha na direção que parece visualmente mais próxima do destino, independentemente do caminho já percorrido.
    
    [2] O algoritmo de custo uniforme (Dijkstra) é um método que, ao contrário da busca gulosa, considera apenas 
    o custo acumulado desde o início, ignorando qualquer estimativa sobre o que falta para chegar ao destino.
    Formalmente, usa a função f(n) = g(n), sem considerar h(n). É garantido encontrar o caminho de menor custo, 
    mas pode explorar desnecessariamente muitos nós em direções afastadas do objetivo. Equivale a um viajante que 
    sempre escolhe o caminho de menor custo acumulado, mesmo que o leve temporariamente para longe do destino.

    [3] A eficiência do A* depende crucialmente da qualidade da heurística. O fator de eficiência ε de uma 
    heurística h em relação à heurística perfeita h* é dado por:
    
    $$\varepsilon = \frac{h}{h^*}$$
    
    Quanto mais próximo ε estiver de 1, menos nós serão expandidos. Se ε = 0 (heurística nula), A* degenera 
    para o algoritmo de Dijkstra; se ε > 1, a heurística é inadmissível e a otimalidade não é garantida.
    
    [4] A implementação eficiente do A* geralmente utiliza uma fila de prioridade (heap) para selecionar o próximo 
    nó a ser explorado. O tempo de execução pode ser melhorado significativamente com estruturas de dados 
    especializadas como Fibonacci heaps, que oferecem operações de atualização de chave em O(1).
    
    [5] O A* é um caso especial do algoritmo Best-First Search, diferenciando-se pela específica função de avaliação
    f(n) = g(n) + h(n). Outras variantes desse framework incluem Greedy Best-First Search (f(n) = h(n)) e 
    Uniform-Cost Search (f(n) = g(n)).
    
    [6] Técnicas de melhoria de heurísticas incluem a combinação de múltiplas heurísticas admissíveis:
    
    $$h(n) = \max(h_1(n), h_2(n), ..., h_k(n))$$
    
    Esta abordagem, conhecida como "máximo de heurísticas admissíveis", mantém a admissibilidade
    enquanto potencialmente melhora a estimativa, resultando em menos expansões de nós.
    """)

