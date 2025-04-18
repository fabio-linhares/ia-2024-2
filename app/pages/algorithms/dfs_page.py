import streamlit as st
import time
import os
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

from app.utils.algorithms import depth_first_search
from app.utils.data_loader import load_data
from app.utils.graph_utils import build_graph, calculate_haversine_distance
from app.components.city_selector import city_selector
from app.components.map_display import display_path_on_map
from app.components.progress_bar import update_progress, animated_progress
from app.components.report_viewer import display_report_viewer

def app():
    st.title("Algoritmo de Busca em Profundidade (DFS)")
    
    st.markdown(r"""
    ## 1. O que é o algoritmo de Busca em Profundidade (DFS)?
    
    A Busca em Profundidade (Depth-First Search ou DFS) é um algoritmo clássico para percorrer estruturas 
    de dados em grafos ou árvores, explorando o máximo possível ao longo de cada ramo antes de retroceder.
    Desenvolvido formalmente pelo matemático francês Charles Pierre Trémaux como uma estratégia para resolver labirintos
    no século XIX, o DFS tornou-se um dos algoritmos fundamentais em ciência da computação.
    
    No DFS, quando um nó é visitado, exploramos recursivamente todos os seus vizinhos não visitados antes de prosseguir,
    seguindo um princípio de "ir o mais fundo possível". Esta estratégia é implementada usando uma estrutura de dados 
    LIFO (Last-In-First-Out), tipicamente uma pilha, que pode ser explícita ou implícita através de chamadas recursivas.
    
    Formalmente, para um grafo G = (V, E), onde V é o conjunto de vértices e E o conjunto de arestas, o DFS constrói 
    uma árvore (ou floresta) de busca em profundidade que categoriza as arestas do grafo em quatro tipos: arestas de árvore,
    arestas de retorno, arestas diretas e arestas cruzadas.
                
    ### Características principais
    
    - **Exploração profunda**: Avança o máximo possível antes de retroceder.
    - **Uso eficiente de memória**: Típicamente requer O(h) de memória, onde h é a altura máxima do grafo.
    - **Completude**: Encontra uma solução se ela existir em um grafo finito.
    - **Não-otimalidade**: Não garante o caminho mais curto ou ótimo.
    - **Detecção de ciclos**: É eficaz para identificar ciclos em grafos.
    - **Ordenação topológica**: Base para algoritmos de ordenação topológica em grafos direcionados acíclicos.
    - **Análise de conectividade**: Utilizado para identificar componentes fortemente conectados.
    """)
    
    # Layout para pseudocódigo e imagem (lado a lado)
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo")
        st.code("""
DFS(grafo, inicio, fim):
    # Versão iterativa usando pilha
    pilha ← [inicio]
    visitados ← {inicio}
    pai ← dicionário vazio
    
    enquanto pilha não estiver vazia:
        atual ← pilha.topo()  # Pega o topo sem remover
        
        se atual == fim:
            return reconstruir_caminho(pai, inicio, fim)
            
        # Verificar se há vizinhos não visitados
        todos_vizinhos_visitados ← verdadeiro
        
        para cada vizinho de atual em grafo:
            # Ordem decrescente de prioridade (menor distância primeiro)
            se vizinho não estiver em visitados:
                pilha.push(vizinho)
                visitados.add(vizinho)
                pai[vizinho] ← atual
                todos_vizinhos_visitados ← falso
                break  # Explora este vizinho antes de continuar
        
        # Se todos os vizinhos já foram visitados, retrocede
        se todos_vizinhos_visitados:
            pilha.pop()
    
    return "Caminho não encontrado"
        """, language="python")

    with cols[1]:
        st.markdown("##### ")
        image_width = 630  # Largura em pixels para padronizar com outros algoritmos
        
        # Usando width diretamente no st.image para controlar o tamanho
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/7/7f/Depth-First-Search.gif",
            caption="Visualização do algoritmo DFS",
            width=image_width  # Controle direto da largura
        )
      
    # Propriedades teóricas do DFS
    st.markdown(r"""
    ### 1.1 Propriedades teóricas do DFS
    
    1. **Classificação de arestas**: O DFS categoriza as arestas em quatro tipos, fundamentais para análise de grafos:
    
       - **Arestas de árvore**: Conectam um nó ao próximo nó descoberto (parte da árvore DFS).
       - **Arestas de retorno (back edges)**: Conectam um nó a um ancestral na árvore DFS, indicando ciclos.
       - **Arestas diretas (forward edges)**: Conectam um nó a um descendente não-filho na árvore DFS.
       - **Arestas cruzadas (cross edges)**: Conectam nós que não têm relação ancestral-descendente.

    2. **Tempo de descoberta e finalização**: Cada vértice v recebe dois carimbos de tempo:
    
       - $d[v]$ (tempo de descoberta): Quando v é primeiro encontrado.
       - $f[v]$ (tempo de finalização): Quando a exploração de v é concluída.
       
       A relação entre estes tempos forma a base do "teorema do parêntese", essencial para muitas aplicações avançadas do DFS.
    
    3. **Teorema do parêntese**: Para quaisquer vértices u e v, exatamente uma das seguintes condições se aplica:
    
       - Os intervalos $[d[u], f[u]]$ e $[d[v], f[v]]$ são completamente disjuntos.
       - O intervalo $[d[u], f[u]]$ está contido no intervalo $[d[v], f[v]]$ (u é descendente de v).
       - O intervalo $[d[v], f[v]]$ está contido no intervalo $[d[u], f[u]]$ (v é descendente de u).
    
    4. **Propriedade da aresta de retorno**: Em um grafo não direcionado, existe um ciclo se e somente se o DFS encontra uma aresta de retorno.
    """)
    
    # Variantes e implementações
    st.markdown(r"""
    ### 1.2 Variantes e implementações eficientes do DFS
    
    1. **DFS recursivo vs. iterativo**: 
       - A versão recursiva é elegante e concisa, mas pode causar estouro de pilha em grafos profundos.
       - A versão iterativa usa uma pilha explícita, evitando o limite de recursão do sistema.
    
    2. **DFS com limite de profundidade (Depth-Limited Search)**:
       Limita a exploração a uma profundidade máxima, útil para espaços de busca muito grandes.
    
    3. **Aprofundamento iterativo (Iterative Deepening DFS)**:
       Realiza múltiplas buscas DFS com limites de profundidade crescentes, combinando as vantagens do DFS e BFS.
    
    4. **DFS bidirecional**:
       Executa duas buscas em paralelo, uma a partir da origem e outra do destino, parando quando se encontram.
    
    5. **DFS com heurística de ordenação de vizinhos**:
       Prioriza a exploração de vizinhos baseando-se em alguma heurística, como distância estimada ao objetivo.
    
    6. **DFS com poda (pruning)**:
       Evita explorar ramos que certamente não levam a uma solução, baseando-se em algum critério.
    
    7. **DFS paralelo/distribuído**:
       Divide o espaço de busca entre múltiplos processadores/máquinas para acelerar a busca.
    """)
    
    # Aplicações e casos de uso
    st.markdown("""
    ## 2. Aplicações do DFS
    
    1. **Análise de conectividade em grafos**:
       - Identificação de componentes fortemente conectados (algoritmo de Kosaraju ou Tarjan)
       - Detecção de pontos de articulação e pontes em redes
       - Teste de biconectividade em grafos
    
    2. **Detecção e análise de ciclos**:
       - Verificação de ciclos em grafos dirigidos e não dirigidos
       - Detecção de ciclos negativos em problemas de otimização
       - Análise de deadlocks em sistemas concorrentes
    
    3. **Ordenação topológica**:
       - Sequenciamento de tarefas com dependências (compiladores, gerenciamento de projetos)
       - Agendamento de cursos acadêmicos com pré-requisitos
       - Resolução de dependências em sistemas de pacotes de software
    
    4. **Solução de labirintos e puzzles**:
       - Resolução de labirintos e puzzles de navegação
       - Jogos de exploração e aventura
       - Quebra-cabeças como Sudoku e Torres de Hanói
    
    5. **Árvores de decisão e árvores de jogo**:
       - Implementação de inteligência artificial em jogos (Minimax, Alpha-Beta pruning)
       - Sistemas especialistas baseados em árvores de decisão
       - Análise de jogos combinatórios
    
    6. **Geração de estruturas**:
       - Criação de labirintos através do algoritmo de backtracking
       - Geração procedural de conteúdo em jogos
       - Síntese de moléculas químicas com estruturas específicas
    """)
    
    # Vantagens e desvantagens
    st.markdown("""
    ## 3. Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    
    - **Baixo consumo de memória**: Requer apenas O(h) de espaço, onde h é a profundidade máxima do caminho
    - **Implementação simples**: Tanto recursiva quanto iterativa, é intuitiva e fácil de implementar
    - **Eficaz para exploração completa**: Útil quando é necessário explorar todos os caminhos possíveis
    - **Adequado para grafos esparsos**: Performance boa em grafos onde cada nó tem poucos vizinhos
    - **Bom para caminhos longos**: Encontra rapidamente caminhos que se estendem profundamente no grafo
    - **Paralelizável por subárvores**: Cada ramo da árvore de busca pode ser explorado em paralelo
    
    ### Desvantagens
    
    - **Não garante otimalidade**: Pode encontrar caminhos muito mais longos que o necessário
    - **Tendência a caminhos profundos**: Pode se perder em ramos profundos longe do objetivo
    - **Ineficiente para grafos densos**: Pode explorar muitos caminhos irrelevantes
    - **Sensibilidade à ordem de exploração**: A qualidade da solução depende da ordem dos vizinhos
    - **Possibilidade de loop infinito**: Em grafos com ciclos, requer controle explícito de visitados
    - **Inadequado para minimização de distância**: Sem modificações, não considera o custo das arestas
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## 4. Comparação com outros algoritmos
    
    | Critério | DFS | BFS | Dijkstra | A* | Fuzzy |
    |----------|-----|-----|----------|----|----|
    | **Princípio básico** | Exploração em profundidade | Exploração em largura | Menor caminho | Heurística + custo real | Graus de pertinência |
    | **Otimização** | Nenhuma garantia | Número de paradas | Distância total | Distância com heurística | Multiobjetivo com incertezas |
    | **Completude** | Sim (com controle de ciclos) | Sim (espaço finito) | Sim | Sim | Depende da implementação |
    | **Otimalidade** | Não | Sim (em arestas) | Sim (distância) | Sim (com heurística admissível) | Não (subjetiva) |
    | **Estrutura de dados** | Pilha (LIFO) | Fila (FIFO) | Fila de prioridade | Fila de prioridade | Fila de prioridade fuzzy |
    | **Complexidade temporal** | O(V+E) | O(V+E) | O(E + V log V) | O(E log V) com heurística | O(E log V) com overhead fuzzy |
    | **Complexidade espacial** | O(h) onde h é altura | O(b^d) onde b é ramificação | O(V) | O(b^d) | O(b^d) |
    | **Uso de memória** | Baixo | Alto | Médio | Médio-alto | Alto |
    | **Caso de uso ideal** | Exploração completa | Menor número de etapas | Minimização de distância | Rotas informadas | Ambientes incertos |
    | **Desempenho em grafos cíclicos** | Requer controle explícito | Naturalmente livre de ciclos | Naturalmente livre de ciclos | Naturalmente livre de ciclos | Depende da implementação |
    | **Produz árvore de busca** | Profunda e estreita | Rasa e larga | Forma de estrela a partir da origem | Direcionada ao objetivo | Múltiplas possibilidades |
    | **Adequação para routing em tempo real** | Inadequada | Limitada | Boa | Excelente | Moderada |
    """)

    st.markdown(r"""
    ## 5. DFS otimizado para problemas de roteamento
    
    ### 5.1 Adaptações e otimizações do DFS para navegação entre cidades
    
    Em problemas de roteamento, o DFS padrão é raramente utilizado sem modificações devido à sua natureza não-otimizada.
    Entretanto, várias adaptações podem transformá-lo em um algoritmo mais adequado:
    
    1. **DFS com ordenação heurística de vizinhos**: Prioritiza a exploração de vizinhos baseada em algum critério, como:
       - Distância estimada ao destino (abordagem gulosa)
       - População (menores primeiro, para evitar congestionamentos)
       - Direção geral em relação ao destino
    
    2. **DFS com limite de profundidade adaptativo**: Começa com um limite de profundidade baseado em alguma estimativa (ex: distância euclidiana / velocidade média) e aumenta gradualmente se necessário.
    
    3. **DFS com poda baseada em custo**: Abandona caminhos quando seu custo total excede o melhor caminho já encontrado, transformando-o em um algoritmo tipo branch-and-bound.
    
    4. **DFS com detecção e prevenção de desvios**: Descarta caminhos que se afastam significativamente da direção geral do destino.
    
    5. **DFS com memorização**: Guarda informações sobre subproblemas já resolvidos, evitando recalcular caminhos ótimos para subregiões já exploradas.
    
    ### 5.2 A implementação em nosso projeto
    
    O algoritmo `depth_first_search` implementado neste projeto inclui várias otimizações:
    
    1. **Ordenação de vizinhos por distância**: Os vizinhos são explorados em ordem crescente de distância.
    
    2. **Critério de desempate por população**: Quando duas cidades estão à mesma distância, a de menor população é explorada primeiro.
    
    3. **Detecção e prevenção de ciclos**: Através do conjunto de nós visitados, evitando revisitar cidades.
    
    4. **Poda baseada em limite de distância**: Se um caminho parcial já excede a melhor distância encontrada, é descartado.
    
    Estas modificações transformam o DFS básico em um algoritmo significativamente mais eficiente para roteamento, capaz de encontrar bons caminhos sem explorar todo o espaço de busca.
    
    A função de prioridade implícita pode ser expressa como:
    
    $$\text{prioridade}(v) = (d(u, v), \text{população}(v))$$
    
    Onde a comparação é lexicográfica: primeiro por distância e, em caso de empate, por população.
    """)
    
    # Notas técnicas adicionais
    st.markdown(r"""
    ### Notas
    
    [1] **Complexidade do DFS**: A análise da complexidade do DFS é baseada no fato de que cada vértice e cada aresta são considerados no máximo uma vez.
    Para um grafo G = (V, E), o tempo de execução é O(V + E) usando listas de adjacência, ou O(V²) usando matriz de adjacência.
    A complexidade espacial pode ser tão baixa quanto O(h) para implementações recursivas onde h é a altura máxima da árvore DFS,
    mas o pior caso pode chegar a O(V) se o grafo for essencialmente uma lista ligada.
    
    [2] **O problema do caminho hamiltoniano**: Encontrar um caminho que visite cada vértice exatamente uma vez (caminho hamiltoniano)
    é um problema NP-completo, mas o DFS pode ser adaptado para resolvê-lo através de backtracking com poda eficiente.
    Este é um caso especial do famoso Problema do Caixeiro Viajante quando todas as arestas têm o mesmo peso.
    
    [3] **DFS e programação de retrocesso (backtracking)**: O DFS é a base para algoritmos de backtracking, que são 
    usados para solucionar problemas de satisfação de restrições. A diferença chave é que o backtracking descarta explicitamente 
    caminhos parciais quando detecta que não podem levar a uma solução válida.
    
    [4] **Teorema da floresta DFS**: A execução do DFS em um grafo não direcionado G = (V, E) produz uma floresta (conjunto de árvores)
    onde o número de árvores é igual ao número de componentes conectados de G.
    
    [5] **Relação entre DFS e algoritmos gananciosos (greedy)**: Enquanto o DFS padrão não é ganancioso, suas variantes com 
    ordem de exploração baseada em heurísticas transformam-no em um algoritmo semi-ganancioso, que pode ser mais eficiente 
    em problemas específicos, mas perde a garantia de completude.
    
    [6] **DFS em grafos implícitos**: Em muitos problemas práticos, o grafo não é construído explicitamente, mas gerado à medida 
    que o algoritmo explora. Nestes casos, o DFS é particularmente útil devido ao seu baixo requisito de memória e capacidade de 
    explorar profundamente sem conhecer todo o grafo previamente.
    """)
