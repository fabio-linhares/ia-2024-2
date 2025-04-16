import streamlit as st
import os

def app():
    st.title("Algoritmo A* (A-Estrela)")
    
    st.markdown(r"""
    ## 1. O que é o algoritmo A*?
    
    O algoritmo A* (A-Estrela) é um algoritmo clássico de busca informada que combina as vantagens da busca 
    gulosa[1] (que busca o caminho que parece ser o melhor) e da busca de custo uniforme[2] (que encontra
    o caminho de menor custo). Parece que esse algoritmo é muito utilizado em GPS, jogos, softwares de navegação
    e inteligência artificial. Por que será? Ele utiliza esta função de avaliação:
    
    $$f(n) = g(n) + h(n)$$
    
    Onde:
    
    - $g(n)$ é o custo do caminho do nó inicial até o nó atual $n$ (o caminho já percorrido)
    - $h(n)$ é uma heurística que estima o custo do caminho do nó $n$ até o objetivo (um chute do qua ainda falta)
    
    **Consequentemente**: ele escolhe sempre ir para o próximo ponto que tem o menor valor de f(n). 
    Ou seja: tenta achar a rota que, somando o que já andou + o melhor palpite para o que falta, parece ser a solução 
    mais rápida/barata.
                
    ### Características principais
    
    - **Completo**: Sempre encontra uma solução se ela existir (com certas condições).
    - **Ótimo**: Encontra o caminho de menor custo se a heurística for admissível (não superestimar).
    - **Eficiente**: Usa a heurística para guiar a busca e reduzir o espaço explorado.
    - **Complexidade**: Depende da qualidade da heurística, podendo ser exponencial no pior caso.
    """)
    
    # Layout para pseudocódigo e imagem (lado a lado)
    # st.subheader("Implementação e Visualização")
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("### Pseudocódigo")
        st.code("""
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
    ### Heurísticas comuns para o algoritmo A*
    
    No contexto de busca de caminhos entre cidades, creio que as heurísticas msis comuns incluem:
    
    1. **Distância Euclidiana**: Linha reta entre dois pontos no plano.
       $$h(n) = \sqrt{(n_x - destino_x)^2 + (n_y - destino_y)^2}$$
    
    2. **Distância de Manhattan**: Soma dos valores absolutos das diferenças das coordenadas.
       $$h(n) = |n_x - destino_x| + |n_y - destino_y|$$
    
    3. **Distância de Haversine**: Para calcular distâncias em uma esfera (como o planeta Terra).
       $$h(n) = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{lat_2-lat_1}{2}\right) + \cos(lat_1) \cdot \cos(lat_2) \cdot \sin^2\left(\frac{lon_2-lon_1}{2}\right)}\right)$$
       onde R é o raio da Terra
    """)
    
    # Aplicações e casos de uso
    st.markdown("""
    ## 2. Aplicações do A*
    
    1. **Sistemas de navegação GPS**:
       - Encontrar rotas mais curtas entre cidades
       - Otimizar percursos considerando distância real
    
    2. **Planejamento de rotas logísticas**:
       - Entregas em múltiplos pontos com menor distância total
       - Roteamento de veículos com restrições de distância
    
    3. **Jogos e simulações**:
       - Determinação de caminhos para personagens em ambientes virtuais
       - Simuladores de tráfego e deslocamento urbano
    
    ## 3. Vantagens e desvantagens no contexto de roteamento de cidades
    
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
    ## 4. Comparação com outros algoritmos
    
    | Critério | A* | BFS | Fuzzy |
    |----------|----|----|-------|
    | Otimização | Distância total | Número de paradas | Considera incertezas |
    | Uso de heurística | Sim | Não | Parcial |
    | Eficiência computacional | Média-Alta | Média | Baixa |
    | Precisão | Alta | Baixa | Média |
    | Aplicação ideal | Rotas mais curtas | Conexões uniformes | Ambientes incertos |
    """) 

    # Carregar conteúdo adicional do arquivo markdown se existir
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                              "reports", "a_star_report.md")
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        st.markdown("## 5. Relatório detalhado sobre A*")
        st.markdown(report_content)
    else:
        st.warning("Relatório detalhado sobre A* não encontrado.")

    st.markdown("""
    ### Notas

    [1] A busca gulosa é um tipo de algoritmo que sempre toma a decisão que parece ser a melhor 
    naquele exato momento, sem se preocupar com o restante do caminho. Imagine alguém caminhando 
    sempre para o lado que parece mais perto do objetivo olhando “a olho”. Pode funcionar bem em 
    muitos casos, mas pode acabar em caminhos ruins. Por exemplo: você está num labirinto e sempre
    vira à esquerda porque a saída parecesse estar lá naquele instante, sem olhar o labirinto inteiro.
    
    [2] O Algoritmo de custo mínimo é um algoritmo que como no nome sugere, sempre escolhe o caminho 
    com menor custo já acumulado desde o começo. Ou seja, ele ignora qualquer estimativa sobre a distância
    ou custo que ainda falta para chegar ao final. Pense em uma estrada. Pensou? Então, o algoritmo 
    vai andando pelas estradas mais baratas já percorridas, mesmo que ainda falte muito para chegar.
    
                """)

