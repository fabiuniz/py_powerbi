import pandas as pd
import re
from rules import categorization_rules, descricoes_para_remover, file_paths
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    pattern = re.compile(r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(-?[\d.]*,\d{2})')
    
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

def categorize_transactions(df, categorization_rules):
    """
    Categoriza as transações com base em um dicionário de regras.
    Aceita regras simples (regex string) e regras complexas (dict com descricao e valor).
    """
    df['Categoria'] = 'Nao_Categorizado'
    # Converte o valor para float, substituindo a vírgula por ponto
    # Primeiro remove o ponto de milhar, depois troca a vírgula por ponto decimal
    df['Valor_num'] = (
        df['Valor']
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    # Isso remove depósitos, transferências recebidas e saldos positivos
    # 1. Filtra para manter apenas o que é saída
    df = df[df['Valor_num'] < 0].copy()

    # 2. CONVERTE PARA POSITIVO PARA FACILITAR A SOMA NOS RELATÓRIOS
    df['Valor_num'] = -df['Valor_num'].abs()
    
    # Se você quiser que a coluna 'Valor' (texto com vírgula) também fique positiva:
    df['Valor'] = df['Valor'].apply(lambda x: x if x.startswith('-') else '-' + x)
    
    # Cria uma cópia para evitar o SettingWithCopyWarning
    df_categorized = df.copy()
    
    for category, rules in categorization_rules.items():
        for rule in rules:
            
            # --- Inicia a máscara de categorização ---
            combined_mask = pd.Series([True] * len(df_categorized))

            # Se o item da lista for uma string, é uma regra simples
            if isinstance(rule, str):
                descricao_pattern = rule
                
            # Se o item da lista for um dicionário, é uma regra complexa
            elif isinstance(rule, dict):
                descricao_pattern = rule.get('descricao')
                valor_exato = rule.get('valor_exato')
                valor_maior_que = rule.get('valor_maior_que')
                valor_menor_que = rule.get('valor_menor_que')
                valor_entre = rule.get('valor_entre')
                
                if valor_exato is not None:
                    valor_mask = df_categorized['Valor_num'] == valor_exato
                    combined_mask = combined_mask & valor_mask
                
                if valor_maior_que is not None:
                    valor_mask = df_categorized['Valor_num'] > valor_maior_que
                    combined_mask = combined_mask & valor_mask
                
                if valor_menor_que is not None:
                    valor_mask = df_categorized['Valor_num'] < valor_menor_que
                    combined_mask = combined_mask & valor_mask
                
                if valor_entre is not None and len(valor_entre) == 2:
                    valor_min, valor_max = valor_entre
                    valor_mask = (df_categorized['Valor_num'] >= valor_min) & (df_categorized['Valor_num'] <= valor_max)
                    combined_mask = combined_mask & valor_mask
            
            # Se houver um padrão de descrição, aplica a máscara.
            if descricao_pattern:
                descricao_mask = df_categorized['Descricao'].str.contains(descricao_pattern, case=False, na=False)
                combined_mask = combined_mask & descricao_mask

            # Aplica a categoria APENAS se a categoria atual for 'Nao_Categorizado'.
            # Isso impede a sobrescrita.
            # O `loc` agora é usado em `df_categorized`
            mask_to_apply = combined_mask & (df_categorized['Categoria'] == 'Nao_Categorizado')
            df_categorized.loc[mask_to_apply, 'Categoria'] = category
            
    # Identifica e coleta as descrições não categorizadas
    uncategorized_descriptions = df_categorized[df_categorized['Categoria'] == 'Nao_Categorizado']['Descricao'].unique().tolist()
    
    return df_categorized, uncategorized_descriptions

# --- Nova função para remover duplicatas e ordenar ---
def clean_and_sort_dataframe(df):
    """
    Remove linhas duplicadas e ordena o DataFrame por data.
    """
    # Remove duplicatas e cria uma cópia explícita para evitar o SettingWithCopyWarning
    df_cleaned = df.drop_duplicates(subset=['Data', 'Descricao'], keep='first').copy()
    
    # Converte a coluna 'Data' para o tipo datetime.
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

        if uncategorized_list:
            print("\n--- ATENÇÃO: Descrições não categorizadas encontradas! ---")
            print("As seguintes descrições serão salvas com a categoria 'Nao_Categorizado':")
            for desc in uncategorized_list:
                print(f"- {desc}")
            print("-" * 50)
        else:
            print("\n--- Todas as descrições foram categorizadas com sucesso! ---")
        
        # O DataFrame 'df_categorized' já contém todas as transações,
        # incluindo as que foram marcadas como 'Nao_Categorizado'.
        final_df = df_categorized.copy()

        # --- Passo 5: Chamada da função de limpeza e ordenação ---
        print("--- 5. Removendo duplicatas e ordenando o DataFrame...")
        final_df = clean_and_sort_dataframe(final_df)
        
        
        # --- NOVO BLOCO: JSON EXPORT ---
        print("--- 5a. Formatando e exportando JSON...")
        # Cria uma cópia do DataFrame ANTES de remover colunas e reformatar para CSV.
        df_json_export = final_df.copy()
        
        # 1. Adiciona as colunas extras e formata/renomeia conforme o JSON desejado
        df_json_export['id'] = df_json_export.reset_index().index + 1
        df_json_export['timestamp'] = (df_json_export['Data'].astype('int64') // 10**6) 
        df_json_export['date'] = df_json_export['Data'].dt.strftime('%Y-%m-%d')
        df_json_export['payment_method'] = 'Não Informado' # Valor fixo
        df_json_export['notes'] = '' # Valor fixo

        # 2. Renomeia e seleciona colunas
        df_json_export.rename(columns={
            'Descricao': 'description',
            'Valor_num': 'value', # Usa a coluna numérica
            'Categoria': 'category'
        }, inplace=True)
        
        # Seleciona e reordena as colunas do JSON no formato desejado
        df_json_export = df_json_export[['id', 'timestamp', 'description', 'value', 'payment_method', 'date', 'notes', 'category']]
        
        # 3. Agrupa por 'category' e transforma em um dicionário de listas para o JSON
        # O to_json(orient='records') converte cada sub-dataframe em uma lista de objetos
        json_grouped = df_json_export.groupby('category').apply(lambda x: x.to_dict('records')).to_dict()
        
        # Exportação JSON
        output_json_path = '../csv/despesas_processadas.json' 
        with open(output_json_path, 'w', encoding='utf-8') as f:
            # Escreve o dicionário no arquivo, usando indentação para legibilidade
            import json
            json.dump(json_grouped, f, indent=4, ensure_ascii=False)
            
        print(f"Cópia do arquivo salva em: {output_json_path}")
        # --- FIM DO BLOCO JSON EXPORT ---
        
        
        # Continua a rotina de CSV original:
        
        # Remove as colunas desnecessárias para o CSV final (mantendo o Valor original com vírgula)
        final_df = final_df.drop(columns=['Descricao', 'Valor_num']) 
        
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
        print("\nPrimeiras 5 linhas do arquivo CSV gerado:")
        print(final_df.head())
        print("\nPrimeira linha do arquivo JSON gerado (Amostra):")
        
        # Imprime uma amostra do JSON agrupado
        import json
        sample_output = {k: v[:1] for k, v in json_grouped.items()} # Pega o primeiro item de cada categoria
        print(json.dumps(sample_output, indent=4, ensure_ascii=False))
    else:
        print("\nNenhum dado válido para processar.")

# --- Bloco principal de execução ---
if __name__ == '__main__':

    all_dataframes = []
    
    for path in file_paths:
        df_raw, _ = process_full_statement(path, categorization_rules)
        if df_raw is not None and not df_raw.empty:
            all_dataframes.append(df_raw)
    
    if all_dataframes:
        # ... (seu código de união e categorização anterior) ...
        df_combined = pd.concat(all_dataframes, ignore_index=True)
        df_categorized, uncategorized_list = categorize_transactions(df_combined.copy(), categorization_rules)

        # 1. Garante que a data seja reconhecida para extrair o ano
        df_categorized['Data'] = pd.to_datetime(df_categorized['Data'], format='%d/%m/%Y')
        df_categorized['Ano'] = df_categorized['Data'].dt.year

        # 1. Primeiro limpamos os dados (Duplicatas e Datas)
        final_df = clean_and_sort_dataframe(df_categorized)
        
        # 2. Garantimos que o Ano seja extraído corretamente
        final_df['Ano'] = final_df['Data'].dt.year
        
        # 3. Calculamos o resumo ANTES de imprimir o total
        resumo_anual = final_df.groupby('Ano')['Valor_num'].sum()
        total_real = resumo_anual.sum() # Soma apenas o que está nos anos acima

        print("\n" + "="*40)
        print("CONCILIAÇÃO FINANCEIRA FINAL")
        print("="*40)

        for ano, soma in resumo_anual.items():
            # Formatação para o padrão brasileiro R$ 0.000,00
            soma_formatada = f"R$ {soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            print(f"ANO {ano}: {soma_formatada}")
        
        print("-" * 40)
        total_formatado = f"R$ {total_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"SOMA TOTAL REAL: {total_formatado}")
        print("="*40 + "\n")

        # Segue para a exportação...
        final_df = clean_and_sort_dataframe(df_categorized)
        # ...
        
        # Exportação JSON e CSV seguem aqui como no seu código...
        # ... (seu código de exportação JSON) ...
        # ... (seu código de exportação CSV) ...

        print(f"\n✅ Processamento concluído com sucesso!")
    else:
        print("\n❌ Nenhum dado válido para processar.")
