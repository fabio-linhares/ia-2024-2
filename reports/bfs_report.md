### I) Análise de Desempenho

#### - Completude
O BFS é **completo**, ou seja, encontrará uma solução, se ela existir, em grafos finitos e totalmente acessíveis.

#### - Optimalidade
O algoritmo encontra sempre o **menor caminho em termos de passos (arestas)**, mas não considera custos ponderados, como distâncias reais ou tempo.

#### - Complexidade

- **Tempo**: O(V + E), onde:  
  - *V* = número de vértices (cidades)  
  - *E* = número de arestas (conexões)

- **Espaço**: O(V), devido ao armazenamento das cidades visitadas durante a execução.

#### - Limitações

O algoritmo pode não ser eficiente para grafos altamente conectados ou onde o fator determinante para o caminho mais curto seja baseado em **pesos das conexões**.

---

### II) Resultados (New York --> Los Angeles [1]

#### a) Caminhos Encontrados: **raio de 4.0 graus**  

| Cenário | Cidade Inicial | Cidade Final | Conexões Utilizadas | Caminho Encontrado | Distância |
|--------|----------------|--------------|----------------------|--------------------|-----------|
| 1      | New York       | Los Angeles  | Raio de 4.0 graus    | New York → Springfield (MO) → Springfield (MA) → Tulsa → Dallas → Pasadena → Los Angeles | 11,96 graus (aprox. 4.957 km) |

---

#### b) Detalhes das Cidades no Caminho [2]

| Cidade        | Estado         | População | Crescimento (2000–2013) | Latitude  | Longitude   |
|---------------|----------------|-----------|--------------------------|-----------|-------------|
| New York      | New York       | 8.405.837 | 4,8%                     | 40.7128   | -74.0059    |
| Springfield   | Missouri       | 164.122   | 7,8%                     | 37.2090   | -93.2923    |
| Springfield   | Massachusetts  | 153.703   | 1,1%                     | 42.1015   | -72.5898    |
| Tulsa         | Oklahoma       | 398.121   | 1,3%                     | 36.1540   | -95.9928    |
| Dallas        | Texas          | 1.257.676 | 5,6%                     | 32.7767   | -96.7970    |
| Pasadena      | Texas          | 152.735   | 7,5%                     | 29.6911   | -95.2091    |
| Pasadena      | Califórnia     | 139.731   | 3,1%                     | 34.1478   | -118.1440   |
| Los Angeles   | Califórnia     | 3.884.307 | 4,8%                     | 34.0522   | -118.2437   |


#### c) Rede de Conexões

- **Total de cidades (nós):** 194  
- **Número de conexões (arestas):** 1.452
  
---

#### d) Densidade

A densidade da rede mede o quão conectado está o grafo de cidades, ou seja, representa a proporção entre **o número real de conexões existentes**  e **o número máximo possível de conexões**. Para nosso grafo não direcionado com **N** nós, o número máximo de conexões possíveis é:

$$
\text{Máximo de Conexões} = \frac{N \times (N-1)}{2}
$$

Portanto, a densidade (**D**) é calculada como:

$$
D = \frac{\text{Número de Conexões Reais}}{\frac{N \times (N-1)}{2}}
$$

- **Densidade da rede:** 0,0776
---

#### e) Interpretação

Considerando os 194 nós desse grafo, o número máximo teórico de conexões seria de 18.721, mas como apenas 1.452 conexões estão presentes (7,76%), isso evidencia uma rede de baixa densidade, o que parece ser uma característica comum em sistemas de transporte reais (segundo o google). A partir disso podemos concluir então que:

- A rede é **relativamente esparsa** – menos de 8% das conexões possíveis entre cidades se realizam.
- Essa baixa densidade afeta diretamente a eficiência do algoritmo **BFS** (Busca em Largura), uma vez que:
  - Redes esparsas tendem a apresentar **menos rotas alternativas**.
  - Podem ser necessários caminhos mais longos para conectar cidades distantes.
  - A busca é geralmente mais rápida devido ao **menor número de conexões a explorar**.

---

### III) Estatísticas Detalhadas

- **População total no caminho**: 14.556.232 habitantes  
- **População média por cidade**: 1.819.529 habitantes  
- **Cidade mais populosa no caminho**: *New York* (8.405.837 habitantes)  
- **Crescimento populacional médio**: 4,6%
- **Número de cidades no caminho:** 6  

---

### IV) Conclusão

O algoritmo **BFS** atendeu ao objetivo de encontrar o caminho com o **menor número de conexões** entre Nova York e Los Angeles.  
O trajeto identificado considera **6 cidades intermediárias** e cobre uma distância de aproximadamente **4.957 km**.

De forma geral:

- O BFS é eficiente para grafos em que o foco é **o menor número de conexões**.
- Porém, **não leva em conta distâncias reais ou custos** (como combustível ou tempo), o que limita seu uso em cenários mais complexos.

---

### Fontes

- [Breadth-first Search - Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [The breadth-first search algorithm (BFS) - Khan Academy](https://www.khanacademy.org/)
- [Extended Breadth-First Search Algorithm (PDF, arXiv)](https://arxiv.org/)
- [Determination of The Shortest Route Based on BFS Algorithm for Purpose to Disaster Evacuation Shelter (PDF)](https://arxiv.org/)

### Notas (do relatório)

[1] Foram utilizadas apenas 200 das 1000 cidades disponíveis para facilitar a visualização dos dados no gráfico. E acelarar o processo. Quem nunca?

[2] Em um primeiro momento a apresentação de 2 cidades (Springfield e Pasadena) com o mesmo nome em Estados difentes pareceu um possível erro no algoritmo, mas parece que realmente existem duas cidades com o nome Pasadena, uma no Texas e a outra na Califórnia. Assim como existem 2 cidades chamadas Springfield. Uma no Missouri e a outra em Massachusetts. Para confirmar fizemos o que todo universitário médio faz: **goglamos**. Para nossa surpresa (e felicidade), de fato existem duas cidades com o nome **Pasadena** e **Springfield**, cada uma com sua própria identidade, contexto histórico e características marcantes. 

##### Pasadena, Califórnia

- **Localização:** Condado de Los Angeles, Califórnia.
- **Características marcantes:**
    - Famosa pelo **Rose Parade** (desfile das rosas) e pelo **Rose Bowl**, eventos que ocorrem anualmente no dia 1º de janeiro.
    - Abriga importantes instituições culturais e científicas, como o **California Institute of Technology (Caltech)** e o **Jet Propulsion Laboratory (JPL)**.
    - Conhecida por seu patrimônio arquitetônico e pela vibrante cena artística e gastronômica.
    
Mais detalhes podem ser encontrados na [página da Wikipedia sobre Pasadena, Califórnia](https://en.wikipedia.org/wiki/Pasadena,_California).

##### Pasadena, Texas

- **Localização:** Condado de Harris, Texas – parte da área metropolitana de Houston.
- **Características marcantes:**
    - Foi fundada em **1893** por John H. Burnett, que se inspirou na vegetação exuberante local (similar à vista em Pasadena, Califórnia) para nomear a cidade.
    - Conhecida historicamente como a "Strawberry Capital" (Capital do Mundo das Fresas) devido à influência das culturas de morango, impulsionada, por exemplo, pela ajuda de Clara Barton da Cruz Vermelha após o furacão de Galveston em 1900.
    - Destaca-se pela ligação com a **indústria petroquímica**, dado seu acesso ao Houston Ship Channel, e pelo **maior departamento de bombeiros voluntários** dos Estados Unidos.
    - Próxima a marcos importantes como o **NASA Lyndon B. Johnson Space Center** (na área de Clear Lake).
    
Mais informações sobre Pasadena, Texas, estão disponíveis no [Handbook of Texas](https://www.tshaonline.org/handbook/entries/pasadena-tx).

##### 📍 Springfield, Missouri

- **Localização**: Sudoeste do estado de Missouri, no planalto dos Ozarks.
- **População**: 169.176 habitantes (Censo de 2020)
- **Importância**: Terceira cidade mais populosa do estado e sede do Condado de Greene
- **Destaques**:
    - Conhecida como o "Berço da Rota 66"
    - Famosa pelo prato local "Springfield-style cashew chicken", criado em 1963 por David Leong
    - Possui o "Cashew Chicken Trail", uma rota gastronômica com mais de 20 restaurantes que servem variações do prato
    
Mais detalhes podem ser encontrados na [página da Wikipedia sobre Springfield, Missouri](https://en.wikipedia.org/wiki/Springfield%2C_Missouri).

##### 📍 Springfield, Massachusetts

- **Localização**: Oeste do estado de Massachusetts, na margem leste do rio Connecticut
- **População**: 153.606 habitantes (Censo de 2020)
- **Fundação**: 1636, sendo uma das cidades mais antigas dos Estados Unidos
- **Destaques**:
    - Local de nascimento do basquetebol, inventado por James Naismith em 1891
    - Sede do Basketball Hall of Fame
    - Centro educacional com várias universidades, incluindo Springfield College e Western New England University
    - Conhecida como "Cidade das Primeiras" por suas muitas inovações históricas

Mais detalhes podem ser encontrados na [página da Wikipedia sobre Springfield, Massachusetts](https://en.wikipedia.org/wiki/Springfield%2C_Massachusetts).


---