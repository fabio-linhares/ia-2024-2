import streamlit as st
import os

def app():
    st.title("Algoritmo de Busca Fuzzy")
    
    st.markdown(r"""
    ## 1. O que é o algoritmo de Busca Fuzzy?
    
    A Busca Fuzzy é uma abordagem que utiliza lógica fuzzy (difusa) para lidar com incertezas
    e imprecisões em problemas de busca de caminhos. Em contraste com a lógica booleana tradicional,
    onde as conexões entre cidades seriam simplesmente "existe" ou "não existe", na lógica fuzzy
    essas conexões podem ter graus de pertinência entre 0 e 1.
    
    Na busca fuzzy, uma conexão entre dois pontos não é apenas "presente" ou "ausente", mas pode
    ter qualquer valor entre 0 (totalmente ausente) e 1 (totalmente presente). Isso permite representar
    situações como "esta estrada está parcialmente congestionada" ou "esta rota é moderadamente confiável".
    
    A fundamentação matemática da lógica fuzzy foi proposta por Lotfi Zadeh em 1965, revolucionando a abordagem
    para problemas com incerteza. Enquanto a teoria clássica de conjuntos determina se um elemento pertence ou não
    a um conjunto (função característica χA(x) ∈ {0,1}), a teoria dos conjuntos fuzzy permite pertinência parcial
    (função de pertinência μA(x) ∈ [0,1]).
                
    ### Características principais
    
    - **Flexibilidade**: Lida com incertezas e imprecisões nas conexões entre cidades.
    - **Tolerância**: Pode encontrar caminhos alternativos mesmo quando conexões ideais não estão disponíveis.
    - **Adaptabilidade**: Pode ajustar-se a diferentes condições e restrições.
    - **Valor de certeza**: Fornece um índice que indica a confiabilidade do caminho encontrado.
    - **Processamento de informação linguística**: Pode incorporar termos vagos como "perto", "longe", "rápido".
    - **Inferência baseada em regras**: Utiliza regras do tipo "SE-ENTÃO" com variáveis linguísticas.
    """)
    
    # Layout para pseudocódigo e imagem (lado a lado)
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo da Versão Básica")
        st.code("""
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
        """, language="python")

    with cols[1]:
        # Centralizando verticalmente para melhor alinhamento com o pseudocódigo
        st.write("### ")  # Espaço em branco para alinhamento vertical
        
        # Definindo largura fixa para controlar o tamanho
        image_width = 630  # Largura em pixels
        
        # Usando width diretamente no st.image para controlar o tamanho
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Fuzzy_logic_temperature_en.svg/800px-Fuzzy_logic_temperature_en.svg.png",
            caption="Exemplo de funções de pertinência fuzzy",
            width=image_width  # Controle direto da largura
        )
       
    # Funções de pertinência
    st.markdown(r"""
    ### Funções de pertinência na lógica Fuzzy

    No contexto de busca de caminhos entre cidades, as funções de pertinência mais comuns incluem:

    1. **Função Trapezoidal**: Define um intervalo onde a pertinência varia gradualmente.
    
    $$
    \mu(x) =
    \begin{cases}
    0, & \text{se } x \leq a \text{ ou } x \geq d \
    \frac{x-a}{b-a}, & \text{se } a \leq x \leq b \
    1, & \text{se } b \leq x \leq c \
    \frac{d-x}{d-c}, & \text{se } c \leq x \leq d
    \end{cases}
    $$

    2. **Função Triangular**: Caso especial onde o intervalo de certeza máxima é um único ponto.
    
    $$
    \mu(x) =
    \begin{cases}
    0, & \text{se } x \leq a \text{ ou } x \geq c \
    \frac{x-a}{b-a}, & \text{se } a \leq x \leq b \
    \frac{c-x}{c-b}, & \text{se } b \leq x \leq c
    \end{cases}
    $$

    3. **Função Gaussiana**: Oferece transição suave entre pertinência e não-pertinência.
    
    $$
    \mu(x) = e^{-\frac{1}{2}\left(\frac{x-c}{\sigma}\right)^2}
    $$

    Onde $c$ é o centro e $\sigma$ controla a largura da curva.
    
    4. **Função Sigmoide**: Útil para modelar transições graduais em limiares.
    
    $$
    \mu(x) = \frac{1}{1 + e^{-a(x-c)}}
    $$
    
    Onde $c$ é o ponto de inflexão e $a$ controla a inclinação.
    
    5. **Função S-Shape (Curva S)**: Adequada para modelar conceitos como "aproximadamente maior que".
    
    $$
    \mu(x) = 
    \begin{cases}
    0, & \text{se } x \leq a \
    2\left(\frac{x-a}{c-a}\right)^2, & \text{se } a \leq x \leq b \
    1-2\left(\frac{x-c}{c-a}\right)^2, & \text{se } b \leq x \leq c \
    1, & \text{se } x \geq c
    \end{cases}
    $$
    
    Onde $b = \frac{a+c}{2}$
    """)

    # Outra seção (sistemas fuzzy)
    st.markdown(r"""
    ### 1.2 Sistema de Inferência Fuzzy para Roteamento
    
    O processo de tomada de decisão em um sistema fuzzy para encontrar caminhos entre cidades geralmente segue estas etapas:
    
    1. **Fuzzificação**: Converter valores precisos de entrada (como distância, tráfego, condições climáticas) em graus de pertinência a conjuntos fuzzy.
    
    2. **Inferência**: Aplicar regras fuzzy do tipo "SE-ENTÃO" para determinar a adequação de cada conexão:
       - SE distância é curta E tráfego é leve, ENTÃO adequação é alta
       - SE distância é média E tráfego é moderado, ENTÃO adequação é média
       - SE distância é longa OU tráfego é intenso, ENTÃO adequação é baixa
    
    3. **Agregação**: Combinar os resultados de todas as regras ativadas usando operadores de agregação (geralmente máximo).
    
    4. **Defuzzificação**: Converter o conjunto fuzzy resultante em um valor preciso de adequação para cada conexão.
    
    A complexidade computacional desse processo é compensada pela capacidade de modelar incertezas e imprecisões de forma mais realista.
    
    **Operadores Fuzzy Avançados**
    
    Além dos operadores básicos (T-norm, T-conorm), sistemas fuzzy avançados podem utilizar:
    
    - **Operadores de média ponderada**: $\mu_A(x) = \sum_{i=1}^{n} w_i \mu_i(x)$, onde $w_i$ são pesos.
    - **Operadores OWA (Ordered Weighted Averaging)**: Combinam valores ordenados por magnitude.
    - **Integrais Fuzzy**: Especialmente a integral de Sugeno e Choquet, para agregação não-aditiva.
    """)

    # Aplicações e casos de uso
    st.markdown("""
    ## 2. Aplicações da Busca Fuzzy

    1. **Sistemas de navegação avançados**:
       - Modelagem de congestionamentos variáveis ao longo do dia (alta imprecisão temporal)
       - Sistemas de navegação adaptativa que aprendem com o comportamento do usuário
       - Navegação em condições de emergência com múltiplos critérios conflitantes
    
    2. **Planejamento de rotas com múltiplos critérios**:
       - Otimização multicritério fuzzy considerando distância, tempo, custo, segurança e conforto
       - Roteamento de frotas de veículos com restrições de tempo e capacidade fuzzy
       - Balanceamento entre rotas ecológicas e rápidas (green routing)
    
    3. **Sistemas de recomendação de rotas**:
       - Roteamento turístico considerando preferências vagas ("lugares interessantes", "não muito distante")
       - Sistemas de recomendação baseados em perfis de condução individuais
       - Navegação para pessoas com necessidades especiais com critérios personalizados
       
    4. **Aplicações industriais e logísticas**:
       - Controle de tráfego urbano com semáforos inteligentes baseados em lógica fuzzy
       - Planejamento de rotas para veículos autônomos em ambientes dinâmicos
       - Otimização de cadeias de suprimentos com incertezas (demanda, disponibilidade, tempos)
       
    5. **Aplicações militares e de emergência**:
       - Planejamento de rotas de evacuação considerando múltiplos riscos imprecisos
       - Navegação de drones em ambientes hostis com informações incompletas
       - Coordenação de equipes de resgate em desastres naturais
    """)
    
    # Vantagens e desvantagens
    st.markdown("""
    ## 3. Vantagens e desvantagens no contexto de roteamento de cidades
    
    ### Vantagens
    
    - **Modelagem robusta de incertezas**: Captura nuances e imprecisões impossíveis em modelos booleanos
    - **Incorporação de conhecimento especialista**: Permite codificar conhecimento humano através de regras linguísticas
    - **Degradação suave de desempenho**: Comportamento mais resiliente quando condições se deterioram
    - **Transparência interpretativa**: As regras fuzzy são mais próximas da linguagem natural, facilitando depuração
    - **Adaptabilidade dinâmica**: Pode ajustar-se a mudanças nas condições sem reprogramação completa
    
    ### Desvantagens
    
    - **Complexidade computacional elevada**: Especialmente em sistemas com muitas regras e variáveis
    - **Aumento não-linear da complexidade**: O número de regras cresce exponencialmente com o número de variáveis
    - **Calibração de parâmetros desafiadora**: Definir funções de pertinência adequadas requer experiência ou otimização
    - **Falta de método formal de design**: Não existe procedimento padrão para o design ótimo de sistemas fuzzy
    - **Possível inconsistência entre regras**: Regras definidas por especialistas podem ser contraditórias
    - **Eficiência questionável em casos extremos**: Para situações muito bem definidas, algoritmos clássicos podem ser mais eficientes
    """)
    
    # Comparação com outros algoritmos
    st.markdown("""
    ## 4. Comparação com outros algoritmos
    
    | Critério | Fuzzy | A* | BFS | Dijkstra | DFS |
    |----------|----|----|----|----|----|
    | **Princípio básico** | Graus de pertinência | Heurística + custo real | Exploração em largura | Menor caminho | Exploração em profundidade |
    | **Otimização** | Multiobjetivo com incertezas | Distância total com heurística | Número de paradas | Distância total | Nenhuma garantia |
    | **Capacidade de adaptação** | Alta | Baixa | Nenhuma | Nenhuma | Nenhuma |
    | **Modelagem de incertezas** | Nativa | Impossível sem modificações | Impossível | Impossível sem modificações | Impossível |
    | **Índice de confiabilidade** | Sim | Não | Não | Não | Não |
    | **Complexidade temporal** | O(b^d) com overhead fuzzy | O(b^d) | O(b^d) | O(E + V log V) | O(b^d) |
    | **Complexidade espacial** | Alta | Média-alta | Alta | Média | Baixa |
    | **Garantia de otimalidade** | Não (subjetiva) | Sim (com heurística admissível) | Sim (distância em arestas) | Sim (distância total) | Não |
    | **Aplicação ideal** | Ambientes incertos, multiobjetivo | Rotas mais curtas com boa heurística | Conexões uniformes | Minimização precisa de distância | Exploração com memória limitada |
    | **Utilização de memória** | Alta | Média-alta | Alta | Média | Baixa |
    | **Paralelizável** | Parcialmente | Parcialmente | Facilmente | Dificilmente | Dificilmente |
    """) 

    # Nova seção: Algoritmo de Busca Fuzzy Bidirecional Avançado
    st.markdown("""
    ## 5. Implementação Avançada: Busca Fuzzy Bidirecional com Heurística
    
    ### 5.1 Visão Geral das Melhorias
    
    Nossa implementação atual aprimora o algoritmo de busca fuzzy tradicional com quatro características avançadas:
    
    1. **Busca Bidirecional**: Explora simultaneamente a partir da origem e do destino, reduzindo o espaço de busca.
    2. **Componente Heurístico Geográfico**: Direciona a busca utilizando distância Haversine, similar ao A*.
    3. **Função de Pertinência Parametrizada**: Permite ajuste fino do comportamento fuzzy através de parâmetros configuráveis.
    4. **Priorização por População**: Em caso de empate, prioriza cidades com menor população.
    """)
    
    # Layout para pseudocódigo avançado e diagrama
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo da Versão Avançada")
        st.code("""
FuzzyBidirectionalSearch(grafo, inicio, fim, r, d):
    # Inicialização
    # Estruturas para busca da origem
    certeza_inicio ← {n: 0.0 para cada n em grafo}
    certeza_inicio[inicio] ← 1.0
    dist_inicio ← {n: ∞ para cada n em grafo}
    dist_inicio[inicio] ← 0
    pais_inicio ← {}
    visitados_inicio ← {}
    
    # Estruturas para busca do destino
    certeza_fim ← {n: 0.0 para cada n em grafo}
    certeza_fim[fim] ← 1.0
    dist_fim ← {n: ∞ para cada n em grafo}
    dist_fim[fim] ← 0
    pais_fim ← {}
    visitados_fim ← {}
    
    # Filas de prioridade para ambas as direções
    # (-certeza, f_score, -população, contador, nó)
    fila_inicio ← [(−1.0, h(inicio, fim), −pop[inicio], 0, inicio)]
    fila_fim ← [(−1.0, h(fim, inicio), −pop[fim], 1, fim)]
    
    melhor_encontro ← None
    melhor_certeza ← 0.0
    melhor_dist ← ∞
    
    enquanto fila_inicio não-vazia E fila_fim não-vazia:
        # Decidir qual direção expandir (balanceando fronteiras)
        expandir_inicio ← (tamanho(visitados_fim) > tamanho(visitados_inicio))
        
        se expandir_inicio:
            # Expandir da origem
            _, f_score, _, _, atual ← pop_min(fila_inicio)
            
            se atual em visitados_inicio: continuar
            visitados_inicio.adicionar(atual)
            
            # Verificar interseção com busca reversa
            se atual em visitados_fim:
                certeza ← min(certeza_inicio[atual], certeza_fim[atual])
                dist_total ← dist_inicio[atual] + dist_fim[atual]
                
                se certeza > melhor_certeza OU 
                  (certeza == melhor_certeza E dist_total < melhor_dist):
                    melhor_encontro ← atual
                    melhor_certeza ← certeza
                    melhor_dist ← dist_total
            
            # Explorar vizinhos
            para cada vizinho de atual no grafo:
                se vizinho em visitados_inicio: continuar
                dist ← distancia(atual, vizinho)
                nova_dist ← dist_inicio[atual] + dist
                
                # Calcular certeza fuzzy
                certeza_aresta ← funcao_pertinencia_parametrizada(dist)
                nova_certeza ← min(certeza_inicio[atual], certeza_aresta)
                
                se nova_certeza > certeza_inicio[vizinho] OU
                  (nova_certeza == certeza_inicio[vizinho] E 
                   nova_dist < dist_inicio[vizinho]):
                    certeza_inicio[vizinho] ← nova_certeza
                    dist_inicio[vizinho] ← nova_dist
                    pais_inicio[vizinho] ← atual
                    
                    # Calcular f_score (A*) e inserir na fila
                    h_valor ← heuristica(vizinho, fim)
                    f_score ← nova_dist + h_valor
                    fila_inicio.push((−nova_certeza, f_score,
                                    −populacao[vizinho], contador++, vizinho))
        senão:
            # Expandir do destino (processo similar)
            # ...código de expansão do destino...
    
    # Reconstruir caminho a partir do ponto de encontro
    se melhor_encontro é None:
        return None, ∞, 0.0
    
    caminho_inicio ← reconstruir_caminho(pais_inicio, inicio, melhor_encontro)
    caminho_fim ← reconstruir_caminho(pais_fim, fim, melhor_encontro, reverso=True)
    
    return caminho_inicio + caminho_fim[1:], melhor_dist, melhor_certeza
        """, language="python")

    with cols[1]:
        st.markdown("### Função de Pertinência Parametrizada")
        st.code("""
# Parâmetros configuráveis
fuzzy_params = {
    'alpha': 3.0,        # Limiar para certeza máxima
    'min_certainty': 0.1, # Certeza mínima
    'decay_factor': 0.9  # Velocidade de decaimento
}

def membership_function(distance, max_distance, params=fuzzy_params):
    if distance <= max_distance / params['alpha']:
        return 1.0
    elif distance >= max_distance:
        return params['min_certainty']
    else:
        return 1.0 - (distance / max_distance) * params['decay_factor']
""", language="python")
        
        st.markdown("### Componente Heurístico")
        st.code("""
# Direciona a busca para o destino
def heuristic(node, target):
    node_attrs = {
        'latitude': graph.nodes[node]['latitude'], 
        'longitude': graph.nodes[node]['longitude']
    }
    target_attrs = {
        'latitude': graph.nodes[target]['latitude'], 
        'longitude': graph.nodes[target]['longitude']
    }
    # Distância Haversine (geodésica) em linha reta
    return calculate_haversine_distance(node_attrs, target_attrs)
""", language="python")

    # Continuar com a explicação da busca fuzzy bidirecional
    st.markdown("""
    ### 5.2 Busca Bidirecional
    
    A abordagem bidirecional inicia explorações simultâneas a partir dos nós de origem e destino:
    
    - **Fronteira da origem**: Expande da origem em direção ao destino 
    - **Fronteira do destino**: Expande do destino em direção à origem
    - **Ponto de encontro**: Quando um nó é visitado por ambas as fronteiras, um caminho completo é formado
    - **Caminho ótimo**: Seleciona o ponto de encontro que maximiza a certeza e minimiza a distância
    
    Esta técnica reduz drasticamente o espaço de busca, acelerando a convergência em até uma ordem de magnitude, especialmente em grafos grandes.
    
    ### 5.3 Componente Heurístico Geográfico
    
    Inspirado no algoritmo A*, incorporamos uma heurística baseada na distância Haversine (geodésica) para guiar a busca de forma mais eficiente:
    
    - Estima a distância em linha reta entre cada nó e o destino
    - Prioriza nós mais próximos do destino (quando a certeza é equivalente)
    - Reduz significativamente o número de nós explorados
    
    A priorização multi-nível dos nós é baseada em:
    1. **Certeza** (primário): Maximiza a confiabilidade do caminho
    2. **f_score = g + h** (secundário): Combina distância percorrida e estimativa até o destino
    3. **População negativa** (terciário): Favorece cidades menores em caso de empate
    
    ### 5.4 Função de Pertinência Parametrizada
    
    Aprimoramos a função de pertinência fuzzy tornando-a configurável através de parâmetros ajustáveis:
    
    - **alpha**: Controla o limite do platô de certeza máxima (valores maiores = platô menor)
    - **min_certainty**: Define o piso de certeza para conexões longas
    - **decay_factor**: Determina a inclinação da curva de decaimento da certeza
    
    Esta parametrização permite calibrar o comportamento fuzzy para diferentes contextos (urbano denso, rural esparso, topografia variável) sem alterar o código.
    
    ### 5.5 Priorização por População
    
    Introduzimos um critério de desempate socialmente consciente que favorece cidades menores:
    
    - Utiliza o valor negativo da população (`-population`) na fila de prioridade
    - Em caso de empate na certeza e distância, cidades com menor população têm prioridade
    - Benefícios: rotas por cidades menos congestionadas, distribuição de tráfego mais equitativa, descoberta de caminhos alternativos
    
    ### 5.6 Comparação de Desempenho
    
    | Métrica | Busca Fuzzy Original | Busca Fuzzy Bidirecional + Heurística |
    |---------|----------------------|---------------------------------------|
    | **Nós explorados** | O(n) | O(√n) em média |
    | **Tempo de execução** | Base | 2-10× mais rápido |
    | **Capacidade heurística** | Não | Sim |
    | **Adaptação a parâmetros** | Limitada | Configurável |
    | **Priorização geográfica** | Distância | Distância + Direção |
    | **Memória utilizada** | O(n) | O(n) mas com constante maior |
    | **Qualidade dos caminhos** | Sensível a dados | Mais consistente |
    | **Priorização social** | Não | Sim (cidades menores) |
    """)
    
    # Aplicações específicas da versão avançada
    st.markdown("""
    ### 5.7 Aplicações Específicas da Versão Avançada
    
    Esta implementação bidirecional com heurística é particularmente eficaz para:
    
    1. **Roteamento em tempo real**: A velocidade de processamento torna-a viável para navegação interativa
    
    2. **Roteamento turístico personalizado**: 
       - Favorece cidades menores que podem oferecer experiências turísticas mais autênticas
       - Permite balancear a confiabilidade das rotas com a descoberta de locais menos conhecidos
    
    3. **Planejamento de evacuação e emergência**:
       - Alta certeza do caminho reflete maior confiabilidade em situações críticas
       - A convergência rápida permite replanejar rotas em resposta a mudanças nas condições
    
    4. **Distribuição logística socialmente consciente**:
       - Equilibra a confiabilidade das conexões com o atendimento a comunidades menores
       - Evita concentrar o tráfego apenas em grandes centros urbanos
    
    5. **Análise de resiliência de redes de transporte**:
       - Permite identificar caminhos alternativos confiáveis quando rotas principais estão comprometidas
       - Facilita a comparação de múltiplos caminhos com diferentes balanceamentos de certeza/distância
    """)

    st.markdown("""
    ### Notas

    [1] A abordagem fuzzy para roteamento utiliza o conceito de "grau de pertinência" que define o quanto
    uma conexão entre dois pontos existe ou é adequada. Em vez de uma conexão simplesmente existir ou não,
    ela pode existir parcialmente. Por exemplo, uma estrada pode estar parcialmente bloqueada ou ter um fluxo
    variável dependendo de condições temporais.
    
    [2] Os operadores fuzzy mais comuns incluem:
      - T-norm (AND lógico): min(a,b), produto algébrico (a*b), produto de Hamacher, produto drástico
      - T-conorm (OR lógico): max(a,b), soma algébrica (a+b-a*b), soma de Hamacher, soma drástica
      - Negação (NOT lógico): complemento padrão (1-a), complemento de Sugeno, complemento de Yager
      
    [3] A teoria de possibilidade, estreitamente relacionada à teoria fuzzy, fornece uma estrutura teórica para modelar 
    incertezas epistêmicas (falta de conhecimento) em contraste com incertezas aleatórias (variabilidade), sendo 
    particularmente útil em sistemas com informações incompletas sobre conexões entre cidades.
    
    [4] No contexto de Controle Fuzzy aplicado à navegação autônoma, métodos como Mamdani e Takagi-Sugeno são amplamente 
    utilizados, com o último oferecendo mais eficiência computacional à custa de menor interpretabilidade.
    """)

    # Explicação da implementação real
    st.markdown("""
    [5] Implementação real da função de pertinência fuzzy. Na implementação básica do algoritmo de busca fuzzy, 
    a função de pertinência fuzzy empregada para avaliar a confiabilidade de cada aresta (ligação entre cidades) foi definida como:


    ```python
    def membership_function(distance, max_distance):
        if distance <= max_distance / 3:
            return 1.0
        elif distance >= max_distance:
            return 0.1
        else:
            return 1 - (distance / max_distance) * 0.9
    ```

    **Interpretação e características:**
    
    - Para distâncias curtas (até um terço da distância máxima), a pertinência/confiança é máxima ($1.0$), refletindo uma conexão considerada totalmente confiável.
    - Para distâncias próximas ou superiores à máxima admitida, a pertinência é mínima ($0.1$), evitando a exclusão total, mas indicando conexão de baixa confiança.
    - Para distâncias intermediárias, o grau de pertinência decresce linearmente de $1.0$ até $0.1$ conforme a distância aumenta.

    **Tipo de função:**  
    Esta função é um caso particular de uma função fuzzy trapezoidal degenerada ou peça-linear, sendo semelhante a uma "trapezoidal" onde há apenas um platô superior (máxima certeza) seguido de uma rampa decrescente de pertinência, até um piso de pertinência mínima.   
    Isso simplifica o cálculo, mantendo a interpretação intuitiva: conexões curtas são sempre altamente confiáveis, conexões longas são cada vez menos confiáveis.

    **Por que usar essa abordagem?**
    - **Vantagens:** Fácil de calibrar, computacionalmente eficiente, intuitiva para operadores e facilmente adaptável a diferentes domínios (basta ajustar os parâmetros de distância máxima e os limites do platô).
    - **Comparação:** Diferente da clássica função triangular ou gaussiana, esta função é mais adequada para contextos onde se quer garantir a máxima confiança para conexões "curtas o suficiente" e decrescer rapidamente a confiança ao se afastar desse ideal.
    
    **Resumo:**  
    A busca fuzzy aqui implementada utiliza esta função para penalizar caminhos com conexões muito longas e premiar caminhos formados idealmente por sequências de arestas seguras/curtas, entregando automaticamente um valor de certeza associado ao caminho calculado pelo algoritmo.
    
    [6] **Algoritmos Fuzzy Avançados**
    
    Além da implementação básica apresentada, existem variantes avançadas dos algoritmos fuzzy para roteamento:
    
    - **Algoritmos Fuzzy-genéticos**: Combinam a capacidade de modelagem de incerteza dos sistemas fuzzy com a otimização evolucionária dos algoritmos genéticos.
    - **Sistemas Fuzzy Adaptativos**: Ajustam automaticamente as funções de pertinência e as regras com base nos dados observados.
    - **Algoritmos Neuro-fuzzy (ANFIS)**: Combinam redes neurais e lógica fuzzy, permitindo aprendizado a partir de dados históricos de roteamento.
    - **Busca Fuzzy Possibilística**: Diferencia incerteza (possibilidade de um evento) da imprecisão (grau de pertinência), resultando em roteamento mais robusto.
    - **Sistemas Fuzzy tipo-2**: Utilizam funções de pertinência que são, elas próprias, fuzzy, modelando meta-incertezas (incerteza sobre a incerteza).
    
    Essas variantes têm mostrado resultados particularmente promissores em cenários urbanos complexos com alta variabilidade temporal e espacial nas condições de tráfego.
    """)