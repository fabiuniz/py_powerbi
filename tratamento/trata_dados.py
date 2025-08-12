import pandas as pd
import re
from rules import categorization_rules

def preprocess_raw_statement(file_path):
    """
    Lê o arquivo de extrato bruto, trata a codificação e faz a limpeza inicial.
    Retorna uma lista de strings, onde cada string é uma linha limpa.
    """
    try:
        # Tenta ler o arquivo com codificação UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # Se falhar, tenta ler com a codificação ISO-8859-1 (latin1)
        with open(file_path, 'r', encoding='latin1') as f:
            lines = f.readlines()
    
    # Remove espaços extras no início e fim de cada linha e filtra linhas vazias
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    return cleaned_lines

def parse_statement_lines(lines):
    """
    Extrai Data, Descrição e Valor de cada linha do extrato.
    Retorna um DataFrame do Pandas com os dados brutos.
    """
    data = []
    # Expressão regular para capturar Data, Descrição e Valor
    # A descrição é um grupo não-guloso (.*?) para evitar capturar a data ou o valor
    # O valor pode ser negativo e ter vírgula
    pattern = re.compile(r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(-?\d+,\d{2})')
    
    for line in lines:
        match = pattern.search(line)
        if match:
            # Captura os grupos da expressão regular
            date, description, value = match.groups()
            data.append({
                'Data': date,
                'Descricao': description.strip(),
                'Valor': value
            })
            
    return pd.DataFrame(data)

def categorize_transactions(df, regex_rules):
    """
    Categoriza as transações com base em um dicionário de regras de regex.
    Retorna o DataFrame categorizado e uma lista de descrições não categorizadas.
    """
    df['Categoria'] = 'Nao_Categorizado'
    
    # Itera sobre as regras e aplica a categorização
    for category, patterns in regex_rules.items():
        for pattern in patterns:
            # Use 'str.contains' para encontrar o padrão na coluna 'Descricao'
            mask = df['Descricao'].str.contains(pattern, case=False, na=False)
            df.loc[mask, 'Categoria'] = category
            
    # Identifica e coleta as descrições não categorizadas
    uncategorized_descriptions = df[df['Categoria'] == 'Nao_Categorizado']['Descricao'].unique().tolist()
    
    return df, uncategorized_descriptions

# --- Nova função para remover duplicatas e ordenar ---
def clean_and_sort_dataframe(df):
    """
    Remove linhas duplicadas e ordena o DataFrame por data.
    """
    # Remove duplicatas considerando as colunas de Data e Descricao.
    df_cleaned = df.drop_duplicates(subset=['Data', 'Descricao'], keep='first')
    
    # Converte a coluna 'Data' para o tipo datetime, que permite a ordenação correta.
    df_cleaned['Data'] = pd.to_datetime(df_cleaned['Data'], format='%d/%m/%Y')
    
    # Ordena o DataFrame pela coluna 'Data' em ordem crescente.
    df_sorted = df_cleaned.sort_values(by='Data')
    
    return df_sorted

def process_full_statement(file_path, categorization_rules):
    """
    Executa o ciclo completo de processamento para um único arquivo:
    1. Lê e limpa o extrato.
    2. Extrai os campos.
    3. Retorna um DataFrame com os dados brutos e um DataFrame categorizado.
    """
    print(f"--- 1. Lendo e limpando o arquivo bruto: {file_path}")
    lines = preprocess_raw_statement(file_path)
    if not lines:
        return None, None

    print("--- 2. Extraindo campos (Data, Descrição, Valor)...")
    df_raw = parse_statement_lines(lines)
    if df_raw.empty:
        print(f"Nenhuma linha válida encontrada no arquivo {file_path}. O processo foi encerrado.")
        return None, None

    return df_raw, None # Retorna o DataFrame bruto e None para o categorizado, pois a categorização será feita no final.

# --- Bloco principal de execução ---
if __name__ == '__main__':
    categorization_rules = {
        'MERCADO': [r'ATACADAO',r'MERCADINHO',r'PANIF',r'PADARIA',r'CARREFOUR', r'RSHOP BIG BOM', r'RSHOP MERCADO ', r'RSHOP MARCO', r'RSHOP MUFFATO', r'SUPERMERCADO', r'RSHOP-MERCADO'],
        'FARMACIA': [r'DROGA',r'FARMACIA', r'DROGARIA'],
        'SAQUE': [r'SAQUE', r'CXE'],
        'RESTAURANTE': [r'DOGAO',r'Feijoada',r'PASTEL',r'Espeto',r'Bacio di',r'VIVENDA DO',r'FRANGO', r'Restaura', r'RSHOP-DOGAO DO', r'RSHOP-SANTA GULA', r'RSHOP-VIVENDA DO', r'RSHOP ESPETO', r'RESTAURANTE', r'PIZZARIA', r'RSHOP-ESPETO'],
        'TELEFONE': [r'MOBILE PAG TIT BANC',r'TIM', r'VIVO', r'CLARO'],
        'INTERNET': [r'INTERNET', r'NET', r'CLARO'],
        'OUTROS': [r'EDUARDODIAS', r'MARIVANLIMA'],
        'GASOLINA': [r'AUTOSUL', r'RSHOP AUTO POSTO', r'RSHOP-AUTO POSTO'],
        'LUZ': [r'ELETROPAULO'],
        'GAS': [r' GAS ',r'INT COMGAS'],
        'ESTACIONAMENTO': [r'ESTAPAR',r'RSHOP-SP MARKET'],
        'IGREJA': [r'ADS',r'SOCIEDADE B', r'ADSA'],
        'HOTEL': [r'FOZ PLAZA',r'RSHOP PANORAMA '],
        'BANCO': [r'SEGURO CARTAO'],
        'SHOPPING': [r'CELLSHOP',r'SHOPPING',r'SP MARKET',r'LOJAS RENNE',r'RSHOP-RIACHUELO'],
        'HOTFRUIT': [r'FRUTAO',r'CHACARA DO',r'Hortifruti'],
        'AEROPORTO':[r'GRU '],
        'PAPELARIA': [r'LAN HOUSE',r'KALUNGA'],
        'ACOUGUE': [r'WEST BOI'],
        'TRANSFERENCIAS' :[r' TRANSF '],
        'MECANICO' :[r'PREMYER',r'CENTRO AUTO',r'CLIMATOA'],
        'TARIFA':[r'ITAU']
        
    }

    file_paths = [
        '../../../../Doc/Docs/Extratos/extrato_012025_250811_181326.txt',
        '../../../../Doc/Docs/Extratos/extrato_072024_250326_201254.txt',
        '../../../../Doc/Docs/Extratos/extrato_052025_250811_181400.txt',
        '../../../../Doc/Docs/Extratos/extrato_112023.txt',
        '../../../../Doc/Docs/Extratos/banco_extrato.txt',
        '../../../../Doc/Docs/Extratos/extrato_012025_250530_222908.txt'
    ]
    
    all_dataframes = []
    
    # Itera sobre a lista de arquivos e processa cada um, acumulando os DataFrames.
    for path in file_paths:
        df_raw, _ = process_full_statement(path, categorization_rules)
        if df_raw is not None and not df_raw.empty:
            all_dataframes.append(df_raw)
    
    # Se houver DataFrames para concatenar, continua o processamento.
    if all_dataframes:
        # Concatena todos os DataFrames em um único DataFrame grande.
        print("\n--- 3. Unindo todos os arquivos processados em um único DataFrame...")
        df_combined = pd.concat(all_dataframes, ignore_index=True)
        
        print("--- 4. Categorizando todas as transações...")
        df_categorized, uncategorized_list = categorize_transactions(df_combined.copy(), categorization_rules)

        print("--- 4. Categorizando todas as transações...")
        df_categorized, uncategorized_list = categorize_transactions(df_combined.copy(), categorization_rules)

        #if uncategorized_list:
        #    print("\n--- ATENÇÃO: Descrições não categorizadas encontradas! ---")
        #    print("Por favor, adicione regras para as seguintes descrições e execute novamente:")
        #    for desc in uncategorized_list:
        #        print(f"- {desc}")
        #    print("-" * 50)            
        #    final_df = df_categorized[df_categorized['Categoria'] != 'Nao_Categorizado'].copy()
        #else:
        #    print("\n--- Todas as descrições foram categorizadas com sucesso! ---")
        #    final_df = df_categorized.copy()

        if uncategorized_list:
            print("\n--- ATENÇÃO: Descrições não categorizadas encontradas! ---")
            print("As seguintes descrições serão salvas com a categoria 'Nao_Categorizado':")
            for desc in uncategorized_list:
                print(f"- {desc}")
            print("-" * 50)
            #Descomentar para Adicionar filtro eliminando Nao_Categorizado e .... logo abaixo ....
            #final_df = df_categorized[df_categorized['Categoria'] != 'Nao_Categorizado'].copy()
        else:
            print("\n--- Todas as descrições foram categorizadas com sucesso! ---")
        
        # O DataFrame 'df_categorized' já contém todas as transações,
        # incluindo as que foram marcadas como 'Nao_Categorizado'.
        # Não é mais necessário filtrar, então podemos atribuir diretamente.
        #E Identrar essa linha para Adicionar filtro eliminando Nao_Categorizado
        final_df = df_categorized.copy()

        # --- Passo 5: Chamada da função de limpeza e ordenação ---
        print("--- 5. Removendo duplicatas e ordenando o DataFrame...")
        final_df = clean_and_sort_dataframe(final_df)
        
        # Remove a coluna de Descricao para ficar com o formato final
        final_df = final_df.drop(columns=['Descricao'])
        
        # Renomeia as colunas para o padrão final
        final_df.rename(columns={'Data': 'Data', 'Categoria': 'Categoria', 'Valor': 'Valor'}, inplace=True)
        
        # A coluna 'Data' já é do tipo datetime, então podemos formatá-la
        final_df['Data'] = final_df['Data'].dt.strftime('%d/%m/%Y')

        # Reordena as colunas para o padrão final: Data, Categoria, Valor
        final_df = final_df[['Data', 'Categoria', 'Valor']]

        # Define o caminho e o nome do arquivo de saída
        output_csv_path = '../csv/despesas_processadas.csv'
        
        # Salva o DataFrame em um arquivo CSV
        final_df.to_csv(output_csv_path, sep=';', index=False)
        
        print(f"\nDados processados e salvos em: {output_csv_path}")
        print("\nPrimeiras 5 linhas do arquivo gerado:")
        print(final_df.head())
    else:
        print("\nNenhum dado válido para processar.")