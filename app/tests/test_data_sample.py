import sys
import os
import pandas as pd

# Adiciona o diretório raiz do projeto ao caminho do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(project_root)

# Importa a função load_data
from app.utils.data_loader import load_data

def test_data_visualization():
    """
    Função para visualizar uma amostra dos dados carregados.
    Exibe informações detalhadas sobre a estrutura e conteúdo dos dados.
    """
    # Caminhos dos arquivos disponíveis
    cities_path = os.path.join(project_root, 'data', 'cities.json')
    test_cities_path = os.path.join(project_root, 'data', 'test_cities.json')
    
    # Tenta carregar o arquivo principal, se não existir, tenta o arquivo de teste
    if os.path.exists(cities_path):
        file_path = cities_path
        print(f"Usando arquivo principal: {cities_path}")
    elif os.path.exists(test_cities_path):
        file_path = test_cities_path
        print(f"Usando arquivo de teste: {test_cities_path}")
    else:
        print("Erro: Nenhum arquivo de dados encontrado.")
        return
    
    # Carrega os dados
    result = load_data(file_path)
    
    # Desempacotar a tupla retornada pela função load_data
    if isinstance(result, tuple) and len(result) == 3:
        df, name_to_id, id_to_name = result
    else:
        # Se por algum motivo não for uma tupla de 3 elementos, usar o resultado diretamente
        df = result
        name_to_id = {}
        id_to_name = {}
    
    # Exibe informações básicas
    print("\n===== INFORMAÇÕES BÁSICAS =====")
    print(f"Total de cidades: {len(df)}")
    print(f"Colunas: {', '.join(df.columns.tolist())}")
    print(f"Tipos de dados:\n{df.dtypes}")
    
    # Exibe uma amostra das primeiras cidades (top 5)
    print("\n===== AMOSTRA DAS 5 MAIORES CIDADES =====")
    pd.set_option('display.max_columns', None)  # Mostra todas as colunas
    pd.set_option('display.width', 1000)  # Aumenta a largura de exibição
    print(df.head(5).to_string(index=False))
    
    # Exibe estatísticas da população
    print("\n===== ESTATÍSTICAS DE POPULAÇÃO =====")
    if 'population' in df.columns:
        pop_stats = df['population'].describe()
        print(f"Média: {pop_stats['mean']:.2f}")
        print(f"Mediana: {pop_stats['50%']:.2f}")
        print(f"Mínimo: {pop_stats['min']:.2f}")
        print(f"Máximo: {pop_stats['max']:.2f}")
    
    # Exibe exemplos de cidades com o mesmo nome (se houver)
    print("\n===== EXEMPLOS DE CIDADES COM NOMES DUPLICADOS =====")
    dupe_cities = df['city'].value_counts()
    dupes = dupe_cities[dupe_cities > 1].index.tolist()
    
    if dupes:
        print(f"Existem {len(dupes)} cidades com nomes duplicados")
        # Mostra exemplos das 3 primeiras cidades duplicadas
        for city in dupes[:3]:
            city_examples = df[df['city'] == city].head(3)
            print(f"\nCidade: {city}")
            for idx, row in city_examples.iterrows():
                print(f"  ID: {row['city_id']} (inteiro)")
                print(f"  Estado: {row.get('state', 'N/A')}")
                print(f"  Coordenadas: ({row['latitude']}, {row['longitude']})")
                print(f"  População: {row['population']}")
                print("-" * 40)
    else:
        print("Não há cidades com nomes duplicados no conjunto de dados.")

if __name__ == "__main__":
    test_data_visualization()