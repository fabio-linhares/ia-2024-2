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
                
    ### Características principais
    
    - **Flexibilidade**: Lida com incertezas e imprecisões nas conexões entre cidades.
    - **Tolerância**: Pode encontrar caminhos alternativos mesmo quando conexões ideais não estão disponíveis.
    - **Adaptabilidade**: Pode ajustar-se a diferentes condições e restrições.
    - **Valor de certeza**: Fornece um índice que indica a confiabilidade do caminho encontrado.
    """)
    
    # Layout para pseudocódigo e imagem (lado a lado)
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo")
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
    """)

    # Outra seção (aplicações como exemplo)
    st.markdown(r"""
    ### 2. Aplicações da Busca Fuzzy

    1. **Sistemas de navegação avançados**:
    - Lidar com rotas onde existem incertezas (como engarrafamentos ou condições climáticas).
    - Priorizar caminhos com maior probabilidade de sucesso.
    2. **Logística e transporte**:
    - Planejamento de rotas para entregas em cidades diferentes.
    """)
    
    # Aplicações e casos de uso
    st.markdown("""
    ## 2. Aplicações da Busca Fuzzy
    
    1. **Sistemas de navegação avançados**:
       - Lidar com rotas onde existem incertezas (como condições de tráfego variáveis)
       - Encontrar caminhos alternativos quando o caminho ideal não está disponível
    
    2. **Planejamento de rotas com múltiplos critérios**:
       - Balancear distância, tempo, custo e outras variáveis
       - Situações onde a conectividade entre locais pode variar (ex: transporte público com horários variáveis)
    
    3. **Sistemas de recomendação de rotas**:
       - Sugerir alternativas quando o caminho direto está congestionado
       - Considerar preferências subjetivas dos usuários
    
    ## 3. Vantagens e desvantagens no contexto de roteamento de cidades
    
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
    ## 4. Comparação com outros algoritmos
    
    | Critério | Fuzzy | A* | BFS |
    |----------|----|----|----|
    | Otimização | Considera incertezas | Distância total | Número de paradas |
    | Capacidade de adaptação | Alta | Baixa | Nenhuma |
    | Índice de confiabilidade | Sim | Não | Não |
    | Complexidade | Alta | Média | Baixa |
    | Aplicação ideal | Ambientes incertos | Rotas mais curtas | Conexões uniformes |
    """) 

    # Carregar conteúdo adicional do arquivo markdown se existir
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                              "reports", "fuzzy_report.md")
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        st.markdown("## 5. Relatório detalhado sobre Busca Fuzzy")
        st.markdown(report_content)
    else:
        st.warning("Relatório detalhado sobre Busca Fuzzy não encontrado.")

    st.markdown("""
    ### Notas

    [1] A abordagem fuzzy para roteamento utiliza o conceito de "grau de pertinência" que define o quanto
    uma conexão entre dois pontos existe ou é adequada. Em vez de uma conexão simplesmente existir ou não,
    ela pode existir parcialmente. Por exemplo, uma estrada pode estar parcialmente bloqueada ou ter um fluxo
    variável dependendo de condições temporais.
    
    [2] Os operadores fuzzy mais comuns incluem:
      - T-norm (AND lógico): frequentemente implementado como min(a,b)
      - T-conorm (OR lógico): frequentemente implementado como max(a,b)
      - Negação (NOT lógico): frequentemente implementado como 1-a
    """)

    # Novo capítulo: explicação da implementação real
    st.markdown("""
    [3] Implementação real da função de pertinência fuzzy. Na implementação prática do algoritmo de busca fuzzy utilizada neste projeto (ver código fonte), 
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
    - **Comparação:** Diferente da clássica função triangular ou gaussiana, esta função é mais adequada para contextos onde se quer garantir a máxima confiança para conexões "curtas o suficiente” e decrescer rapidamente a confiança ao se afastar desse ideal.
    
    **Resumo:**  
    A busca fuzzy aqui implementada utiliza esta função para penalizar caminhos com conexões muito longas e premiar caminhos formados idealmente por sequências de arestas seguras/curtas, entregando automaticamente um valor de certeza associado ao caminho calculado pelo algoritmo.
    """)