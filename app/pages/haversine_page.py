import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np
import math

def app():
    st.title("A Fórmula de Haversine")
    
    st.markdown("""
    A fórmula de Haversine é uma das ferramentas matemáticas essenciais para calcular a distância entre dois pontos na superfície da Terra, 
    levando em conta a sua curvatura. Ela é amplamente usada em sistemas de navegação, GPS, geolocalização e aplicações de 
    Sistemas de Informação Geográfica (SIG). Seu maior destaque é possibilitar a determinação da chamada "distância do arco máximo" 
    (ou "distância em linha reta", como o voo de um pássaro), conhecida no meio técnico como "great-circle distance".
    """)
    
    st.header("Como a fórmula funciona")
    
    st.markdown("""
    A base matemática da fórmula usa trigonometria esférica, considerando latitudes e longitudes em radianos. 
    O cálculo é feito a partir das coordenadas de dois pontos na esfera (geralmente, a superfície da Terra), 
    dadas como latitude (φ) e longitude (λ) para ambos os pontos. Seu enunciado clássico é:
    """)
    
    st.latex(r"d = 2r \arcsin \left( \sqrt{ \sin^2 \left( \frac{\varphi_2 - \varphi_1}{2} \right) + \cos(\varphi_1) \cos(\varphi_2) \sin^2 \left( \frac{\lambda_2 - \lambda_1}{2} \right) } \right)")
    
    st.markdown("""
    Onde:
    
    - d = distância entre os pontos (em km, usando o raio da Terra em km)
    - r = raio da Terra (padrão: 6.371 km)
    - φ₁, φ₂ = latitudes dos dois pontos, em radianos
    - λ₁, λ₂ = longitudes dos dois pontos, em radianos
    """)
    
    st.markdown("""
    O nome "haversine" decorre da função matemática haversin, definida como:
    """)
    
    st.latex(r"\operatorname{hav}(\theta) = \sin^2\left(\frac{\theta}{2}\right)")
    
    st.header("Implementação prática")
    
    st.markdown("""
    A partir dessas fórmulas, é possível automatizar o cálculo em linguagens de programação como Python. Por exemplo:
    """)
    
    code = '''
import math

def haversine(lat1, lon1, lat2, lon2):
    # Converte graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Raio médio da Terra em km
    return c * r

# Exemplo prático: São Paulo (-23.5505, -46.6333) e Rio de Janeiro (-22.9068, -43.1729)
distancia = haversine(-23.5505, -46.6333, -22.9068, -43.1729)
print(f"A distância é de {distancia:.2f} km")  # Aproximadamente 360 km
    '''
    
    st.code(code, language="python")
    
    st.markdown("""
    Confira o exemplo direto nas referências:
    
    [O que é a fórmula de Haversine e como funciona](https://tecnologia.credited.com.br/glossario/o-que-e-formula-de-haversine-como-funciona/?utm_source=openai)
    """)
    
    st.header("Considerações de precisão")
    
    st.markdown("""
    Embora bastante precisa para a maioria das aplicações, a fórmula de Haversine assume que a Terra é uma esfera perfeita, 
    quando na realidade o planeta é um esferoide oblato (ligeiramente achatado nos polos). Por isso, para distâncias muito longas 
    ou aplicações científicas detalhadas, recomenda-se o uso de métodos mais sofisticados como a fórmula de Vincenty.
    
    Saiba mais sobre a teoria e exemplos de uso:
    
    - O que é Haversine e como funciona
    - Explicação detalhada na Wikipedia
    - Código e explicações em português
    """)
    
    st.header("Resumo final")
    
    st.markdown("""
    A fórmula de Haversine é uma das formas mais eficientes e amplamente adotadas para obter distâncias geodésicas com precisão 
    suficiente para rotas, navegação urbana, cálculo de logística e outros usos técnicos, principalmente quando comparada a 
    métodos que ignoram a curvatura da Terra.
    
    Fontes completas para consulta e aprofundamento:
    
    - [O que é Haversine? - Codidata](https://codidata.com.br/o-que-e-formula-haversine/)
    - [Fórmula de Haversine - Wikipedia PT](https://pt.wikipedia.org/wiki/F%C3%B3rmula_de_haversine)
    - [Fórmula de Haversine: exemplos práticos em Python - Credited Tecnologia](https://tecnologia.credited.com.br/glossario/o-que-e-formula-de-haversine-como-funciona/)
    """)
    
    # Visualização da fórmula em um gráfico esférico
    st.header("Visualização")
    
    st.markdown("Representação visual da distância entre dois pontos em uma esfera, calculada pela fórmula de Haversine:")
    
    # Criar um botão para mostrar a visualização
    if st.button("Mostrar visualização 3D"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Função para criar a visualização
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Criar uma esfera
            u = np.linspace(0, 2 * np.pi, 100)
            v = np.linspace(0, np.pi, 100)
            x = np.outer(np.cos(u), np.sin(v))
            y = np.outer(np.sin(u), np.sin(v))
            z = np.outer(np.ones(np.size(u)), np.cos(v))
            
            # Plotar a esfera
            ax.plot_surface(x, y, z, color='lightblue', alpha=0.3)
            
            # Definir dois pontos (convertendo de lat/long para coordenadas cartesianas)
            lat1, lon1 = -23.5505, -46.6333  # São Paulo
            lat2, lon2 = -22.9068, -43.1729  # Rio de Janeiro
            
            # Converter para radianos
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Converter para coordenadas cartesianas (x, y, z) em uma esfera unitária
            x1 = math.cos(lat1) * math.cos(lon1)
            y1 = math.cos(lat1) * math.sin(lon1)
            z1 = math.sin(lat1)
            
            x2 = math.cos(lat2) * math.cos(lon2)
            y2 = math.cos(lat2) * math.sin(lon2)
            z2 = math.sin(lat2)
            
            # Plotar os pontos
            ax.scatter([x1], [y1], [z1], color='red', s=100, label='São Paulo')
            ax.scatter([x2], [y2], [z2], color='blue', s=100, label='Rio de Janeiro')
            
            # Plotar a linha reta (em 3D) entre os pontos
            ax.plot([x1, x2], [y1, y2], [z1, z2], 'g--', label='Distância Euclidiana')
            
            # Calcular e plotar o grande círculo entre os pontos
            t = np.linspace(0, 1, 100)
            # Interpolação esférica
            sin_t = np.sin(t * math.acos(x1*x2 + y1*y2 + z1*z2))
            sin_1_t = np.sin((1-t) * math.acos(x1*x2 + y1*y2 + z1*z2))
            
            if sin_t[0] != 0:  # Evitar divisão por zero
                x_gc = (sin_1_t * x1 + sin_t * x2) / np.sin(math.acos(x1*x2 + y1*y2 + z1*z2))
                y_gc = (sin_1_t * y1 + sin_t * y2) / np.sin(math.acos(x1*x2 + y1*y2 + z1*z2))
                z_gc = (sin_1_t * z1 + sin_t * z2) / np.sin(math.acos(x1*x2 + y1*y2 + z1*z2))
                ax.plot(x_gc, y_gc, z_gc, 'r-', linewidth=2, label='Distância Haversine')
            
            ax.set_title('Haversine vs. Distância Euclidiana')
            ax.legend()
            
            st.pyplot(fig)
        
        with col2:
            # Calcular a distância real usando Haversine
            lat1, lon1 = -23.5505, -46.6333  # São Paulo
            lat2, lon2 = -22.9068, -43.1729  # Rio de Janeiro
            
            def haversine(lat1, lon1, lat2, lon2):
                # Converte graus para radianos
                lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                c = 2 * math.asin(math.sqrt(a))
                r = 6371  # Raio médio da Terra em km
                return c * r
            
            distancia = haversine(lat1, lon1, lat2, lon2)
            
            st.metric("Distância Haversine", f"{distancia:.2f} km")
            st.markdown("""
            **Pontos:**
            - São Paulo: -23.5505, -46.6333
            - Rio de Janeiro: -22.9068, -43.1729
            
            A linha vermelha mostra a rota real sobre a superfície da Terra, enquanto a linha verde tracejada mostra a distância euclidiana através da Terra.
            """)