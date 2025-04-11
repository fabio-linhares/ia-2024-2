# Problem Solving: City Route Finder

Este repositório contém a solução para a atividade avaliativa de *Problem Solving* do PPGI008 – Inteligência Artificial, da UFAL. A proposta consiste em encontrar a rota com menor distância acumulada entre duas cidades, considerando que a existência de uma estrada é definida pela distância euclidiana entre elas (dentro de um parâmetro "r"). Em caso de empate entre rotas, é utilizada a regra de priorizar cidades com menor população.

## Sumário
- [Introdução](#introdução)
- [Modelagem](#modelagem)
- [Implementação](#implementação)
  - [Algoritmos de Busca](#algoritmos-de-busca)
  - [Estrutura do Projeto](#estrutura-do-projeto)
- [Resultados](#resultados)
- [Conclusão e Limitações](#conclusão-e-limitações)
- [Instruções de Uso](#instruções-de-uso)
- [Dependências](#dependências)
- [Relatórios](#relatórios)
- [Anexos](#anexos)

## Introdução

Este projeto tem como objetivo implementar uma solução para o problema de roteamento entre cidades. O desafio consiste em:
- Determinar a rota com a menor distância total entre uma cidade inicial e uma cidade final;
- Considerar uma conexão entre cidades se a distância euclidiana entre elas for menor ou igual ao parâmetro **r**;
- Em situações de empate, priorizar a visitação de cidades com menor população.

Além disso, o projeto contempla a modelagem do ambiente, que envolve a definição do espaço de estados, conjunto de ações, modelo de transição e a função de custo (ação-custo).

## Modelagem

### PEAS
- **Performance:** Obter a rota de menor distância (acumulada) entre as duas cidades de forma eficiente.
- **Environment (Ambiente):** Conjunto de cidades dos Estados Unidos extraídas de um arquivo JSON e interconectadas segundo a distância euclidiana.
- **Actuators (Atuadores):** Exibição dos resultados em uma interface interativa, incluindo um mapa com a rota e relatórios detalhados.
- **Sensors (Sensores):** Entrada dos dados via arquivo JSON e os parâmetros informados pelo usuário (cidades de partida e chegada, valor de **r**).

### Espaço de Estados, Ações e Função de Transição
- **Espaço de Estados:** Cada estado representa uma cidade.
- **Conjunto de Ações:** Mover-se de uma cidade para outra, desde que a distância entre elas seja menor ou igual a **r**.
- **Modelo de Transição:** A cada ação, o estado atual transita para a cidade adjacente se a estrada (definida pela restrição de distância) existir.
- **Função Ação-Custo:** O custo de mover-se de uma cidade para a outra é a distância euclidiana entre elas. Em caso de empate, cidades com menor população são priorizadas.

## Implementação

A solução foi implementada utilizando **Python 3.12** e a biblioteca **Streamlit** para construir uma interface interativa. Duas abordagens de busca foram empregadas:
- **Busca em Largura (BFS):** Algoritmo clássico, explorando os nós por nível.
- **Busca A\* (A-Star):** Algoritmo informada que utiliza uma função heurística baseada na distância euclidiana.

Além destes, foi incluída também uma abordagem de **Fuzzy Search** para explorar possibilidades alternativas quando a conexão direta não for identificada de maneira clara.

### Estrutura do Projeto

```
city_router/
├── app/
│   ├── components/
│   │   ├── city_selector.py       # Componente para seleção de cidades
│   │   ├── map_display.py         # Exibição do mapa interativo
│   │   ├── progress_bar.py        # Barra de progresso para monitoramento
│   │   └── report_viewer.py       # Visualização dos relatórios em Markdown
│   ├── pages/
│   │   ├── about.py               # Página "Sobre"
│   │   └── main_app.py            # Página principal (interface de busca)
│   ├── styles/
│   │   └── custom.css             # CSS customizado para estilização
│   ├── utils/
│   │   ├── algorithms.py          # Implementação dos algoritmos de busca
│   │   ├── data_loader.py         # Carregamento dos dados do arquivo JSON
│   │   └── graph_utils.py         # Construção e manipulação do grafo
│   ├── __init__.py
│   └── main.py                    # Ponto de entrada do aplicativo Streamlit
├── reports/                       # Relatórios detalhados dos algoritmos (Markdown)
│   ├── bfs_report.md
│   ├── a_star_report.md
│   └── fuzzy_report.md
├── data/
│   └── cities.json              # Dados das cidades mais populosas dos EUA
├── .streamlit/
│   └── config.toml              # Configurações do tema para o Streamlit
├── requirements.txt             # Dependências Python (pip)
├── environment.yml              # Dependências para ambiente Conda
└── README.md                    # Este arquivo
```

## Resultados

Para validar a implementação, foram especificados três cenários de uso:
- **Cenário 1 (Solução Existe):**  
  - *Valor de r:* 5.0  
  - *Cidade Inicial:* New York  
  - *Cidade Final:* Los Angeles  

- **Cenário 2 (Solução Existe):**  
  - *Valor de r:* 5.0  
  - *Cidade Inicial:* Chicago  
  - *Cidade Final:* San Francisco  

- **Cenário 3 (Solução Não Existe):**  
  - *Valor de r:* 1.0  
  - *Cidade Inicial:* New York  
  - *Cidade Final:* Los Angeles  

Cada cenário foi testado e os resultados (rota, distância e, para a abordagem fuzzy, a certeza do resultado) estão documentados nos arquivos de relatório.

## Conclusão e Limitações

A implementação demonstrou a aplicação prática dos conceitos de modelagem, busca e otimização de rotas. Entre os pontos positivos, destacam-se:
- Facilidade de visualização e interação com a interface Streamlit.
- Comparação qualitativa e quantitativa (tempo de execução e consumo de memória) entre os algoritmos de busca utilizados.

Limitações e desafios:
- **Escalabilidade:** Em cenários com um número elevado de cidades (ou conexões muito densas), a exigência de memória e tempo de processamento pode aumentar consideravelmente.
- **Realismo:** O modelo utiliza distância euclidiana em um espaço 2D, o que é uma simplificação da geografia real. Para uma aplicação mais realista, seriam necessários dados geográficos mais precisos e a consideração de fatores como topografia e redes viárias reais.

## Instruções de Uso

1. **Clone o repositório:**

   ```bash
   git clone [repository_url]
   cd city_router
   ```

2. **Crie e ative o ambiente Conda:**

   ```bash
   conda env create -f environment.yml
   conda activate city_router
   ```

3. **Instale as dependências (caso necessário):**

   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação com Streamlit:**

   ```bash
   streamlit run app/main.py
   ```

5. **Interaja com o aplicativo:**  
   Utilize os menus e selecione as cidades e o valor de **r**. Explore os resultados e os relatórios gerados.

## Dependências

- **Python 3.12**
- **Streamlit** para a interface gráfica
- **Pandas**, **NumPy** e **Matplotlib** para manipulação de dados e gráficos
- **NetworkX** para a construção e análise do grafo
- **Folium** e **streamlit-folium** para a renderização do mapa
- **Tqdm** para a visualização da barra de progresso
- **Streamlit Option Menu** para a navegação interativa

## Relatórios

Os relatórios detalhando os algoritmos de **BFS**, **A\*** e **Fuzzy Search** estão disponíveis na pasta `reports/`:
- **bfs_report.md**
- **a_star_report.md**
- **fuzzy_report.md**

---

*Agradeço pela atenção e espero que essa solução inspire novas ideias e melhorias. Qualquer feedback ou sugestão será muito bem-vindo!*
