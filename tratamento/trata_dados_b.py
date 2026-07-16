import pandas as pd
import re
import hashlib
import io
import sys
from rules import categorization_rules,descricoes_para_remover,file_paths
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

def categorize_transactions(df, categorization_rules):
    """
    Categoriza as transações com base em um dicionário de regras.
    Aceita regras simples (regex string) e regras complexas (dict com descricao e valor).
    """
    df['Categoria'] = 'Nao_Categorizado'
    # Converte o valor para float, substituindo a vírgula por ponto
    df['Valor_num'] = df['Valor'].str.replace(',', '.').astype(float)
    
    # Cria uma cópia para evitar o SettingWithCopyWarning
    df_categorized = df.copy()
    
    for category, rules in categorization_rules.items():
        for rule in rules:
            
            # --- RESET DAS VARIÁVEIS PARA CADA REGRA ---
            descricao_pattern = None
            valor_exato = None
            valor_maior_que = None
            valor_menor_que = None
            valor_entre = None

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
            
            # Se houver um padrão de descrição válido para esta regra, aplica a máscara.
            if descricao_pattern:
                descricao_mask = df_categorized['Descricao'].str.contains(descricao_pattern, case=False, na=False)
                combined_mask = combined_mask & descricao_mask
            else:
                # Se não houver padrão de descrição definido para a regra, ela não deve validar nada por texto
                combined_mask = pd.Series([False] * len(df_categorized))

            # Aplica a categoria APENAS se a categoria atual for 'Nao_Categorizado'.
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
    # Create a new DataFrame using a deep copy
    df_cleaned = df.drop_duplicates(subset=['Data', 'Descricao'], keep='first').copy()
    
    # Use .loc to safely modify the DataFrame
    df_cleaned.loc[:, 'Data'] = pd.to_datetime(df_cleaned['Data'], format='%d/%m/%Y')
    
    # Ordena o DataFrame pela coluna 'Data' em ordem crescente.
    df_sorted = df_cleaned.sort_values(by='Data', ascending=False)
    
    return df_sorted

def process_full_statement(file_path, categorization_rules):
    """
    Executa o ciclo completo de processamento para um único arquivo:
    1. Lê e limpa o extrato.
    2. Extrai os campos.
    3. Retorna um DataFrame com os dados brutos e um DataFrame categorizado.
    """
    print(f"--- 📖 Lendo e limpando o arquivo bruto: {file_path}")
    lines = preprocess_raw_statement(file_path)
    if not lines:
        return None, None

    print("--- 🔍 Extraindo campos (Data, Descrição, Valor)...")
    df_raw = parse_statement_lines(lines)
    if df_raw.empty:
        print(f"⚠️Nenhuma linha válida encontrada no arquivo {file_path}. O processo foi encerrado.")
        return None, None

    return df_raw, None # Retorna o DataFrame bruto e None para o categorizado, pois a categorização será feita no final.

def add_txt(df, file_path):
    """
    Salva as transações de um DataFrame em um arquivo de texto.

    Args:
        df (pd.DataFrame): O DataFrame a ser salvo.
        file_path (str): O caminho e nome do arquivo de saída.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("--- Transações não categorizadas ---\n")
        f.write("-" * 50 + "\n")
        
        for index, row in df.iterrows():
            linha = f"Data: {row['Data']:<10} | Descrição: {row['Descricao']:<40} | Valor: {row['Valor']}\n"
            f.write(linha)
            
        f.write("-" * 50 + "\n")

import hashlib

def descaracterizar_misto(descricao: str) -> str:
    if not descricao:
        return "***"    
    palavras = descricao.split()
    primeira_palavra = palavras[0] if palavras else ""    
    # Gera o hash do texto completo para garantir a unicidade
    hash_unico = hashlib.sha256(descricao.encode('utf-8')).hexdigest()[:8]    
    # Retorna a primeira palavra + o hash identificador
    return f"{primeira_palavra} #{hash_unico}"

def print_nao_categorizadas(nao_categorizadas):
    if not nao_categorizadas.empty:
        # 2. Remove duplicatas apenas para exibição no terminal (evita poluição visual)
        nao_categorizadas_unicas = nao_categorizadas.drop_duplicates(subset=['Descricao'])
        print(f"\n⚠️  ALERTA: Foram encontradas {len(nao_categorizadas_unicas)} descrições únicas sem categoria!")
        print("-" * 80)
        print(f"{'DATA':<12} | {'DESCRIÇÃO':<45} | {'VALOR (R$)':<10}")
        print("-" * 80)        
        # 3. Varre e imprime cada uma delas formatada
        for index, row in nao_categorizadas_unicas.iterrows():
            print(f"{row['Data']:<12} | {row['Descricao']:<45} | {row['Valor']:<10}")        
        print("-" * 80)
        print("💡 Dica: Adicione estes termos acima ao seu arquivo 'rules.py' para categorizá-los.\n")
    else:
        print("--- 🎉 Excelente! Todas as transações foram categorizadas com sucesso!\n")

# --- Bloco principal de execução ---
if __name__ == '__main__':

    # call rules.py here
    
    all_dataframes = []
    
    # Itera sobre a lista de arquivos e processa cada um, acumulando os DataFrames.
    print("\n📖1. Extraindo todas as transações...")
    for path in file_paths:
        df_raw, _ = process_full_statement(path, categorization_rules)
        if df_raw is not None and not df_raw.empty:
            all_dataframes.append(df_raw)
    
    # Se houver DataFrames para concatenar, continua o processamento.
    if all_dataframes:
        print("\n🔗2. Unindo todos os arquivos processados em um único DataFrame...")
        df_combined = pd.concat(all_dataframes, ignore_index=True)
        print(f"---📊 Total de registros unificados: {len(df_combined)} linhas.\n")

        # --- MÉTRICAS DE AUDITORIA INICIAL ---
        # Converte temporariamente para float para somar o valor bruto total extraído
        df_combined['Valor_num_temp'] = df_combined['Valor'].str.replace(',', '.').astype(float)
        total_linhas_bruto = len(df_combined)
        valor_total_bruto = df_combined['Valor_num_temp'].sum()

        print("🏷️3. Categorizando todas as transações...")
        df_categorized, _ = categorize_transactions(df_combined.copy(), categorization_rules)
        nao_categorizadas = df_categorized[df_categorized['Categoria'] == 'Nao_Categorizado'].copy()
        print_nao_categorizadas(nao_categorizadas)

        # --- Removendo descrições indesejadas do DataFrame completo ---
        print("🧹3.1. Removendo descrições indesejadas...")
        padrao_regex = '|'.join(descricoes_para_remover)
        mascara_remocao = df_categorized['Descricao'].str.contains(padrao_regex, case=False, na=False)
        df_filtrado_final = df_categorized[~mascara_remocao].copy()

        # --- Removendo duplicados
        df_combined.drop_duplicates(inplace=True)
        # Converte 'Data' para datetime, ordena e formata de volta para string
        df_combined['Data'] = pd.to_datetime(df_combined['Data'], format='%d/%m/%Y', errors='coerce')
        df_combined = df_combined.sort_values(by='Data', ascending=False)
        df_combined['Data'] = df_combined['Data'].dt.strftime('%d/%m/%Y')
        
        # Salva o DataFrame já ordenado no arquivo de log
        # Se você removeu descrições indesejadas (como SALDO ANTERIOR), guarde o impacto:
        valor_removido_filtros = df_categorized[mascara_remocao]['Valor_num'].sum()
        linhas_removidas_filtros = mascara_remocao.sum()
        add_txt(df_combined, "../logs/rep_combined_trated.log")

        # Filtra o DataFrame para encontrar as transações não categorizadas
        uncategorized_df = df_filtrado_final[df_filtrado_final['Categoria'] == 'Nao_Categorizado'].copy()

        if not uncategorized_df.empty:
            # 1. Converte a coluna 'Data' para datetime
            uncategorized_df['Data'] = pd.to_datetime(uncategorized_df['Data'], format='%d/%m/%Y')
            
            # 2. Ordena o DataFrame pela data em ordem decrescente
            uncategorized_df = uncategorized_df.sort_values(by='Data', ascending=False)
            
            # 3. Formata a coluna 'Data' de volta para string antes de salvar
            uncategorized_df['Data'] = uncategorized_df['Data'].dt.strftime('%d/%m/%Y')
            
            output_txt_path = '..\logs\descricoes_nao_categorizadas.log'
            # Chama a função para salvar as transações não categorizadas
            add_txt(uncategorized_df, output_txt_path)

            print("\n--- ⚠️ATENÇÃO: Descrições não categorizadas encontradas! ---")
            print("As seguintes transações serão salvas com a categoria 'Nao_Categorizado':")
            
            # Exibe as 3 colunas (Data, Descricao, Valor)
            print("-" * 50)
            for index, row in uncategorized_df.iterrows():        
                #desc = descaracterizar_misto(row['Descricao']);        
                desc = row['Descricao'];
                print(f"Data: {row['Data']:<10} | Descrição: {desc:<40} | Valor: {row['Valor']}")
            print("-" * 50)
            
        else:
            print("--- ✨Todas as descrições foram categorizadas com sucesso! ---\n")
        
        final_df = df_filtrado_final.copy() # Good practice to work on a copy

        # --- Passo 5: Chamada da função de limpeza e ordenação ---
        print("⚡4. Removendo duplicatas e ordenando o DataFrame...")
                # 1. Guarda a quantidade de linhas antes da limpeza
        linhas_antes = len(final_df)
                # 2. Executa a função
        final_df = clean_and_sort_dataframe(final_df)
                # 3. Calcula e exibe a quantidade de duplicatas removidas
        removidos = linhas_antes - len(final_df)
        print(f"--- 🗑️ Linhas duplicadas removidas: {removidos}")

        # Convert 'Data' to datetime just to be safe before formatting
        final_df['Data'] = pd.to_datetime(final_df['Data'], format='%d/%m/%Y', errors='coerce')

        # A coluna 'Data' agora é do tipo datetime, então podemos formatá-la
        final_df['Data'] = final_df['Data'].dt.strftime('%d/%m/%Y')

        # Reordena as colunas para o padrão final: Data, Categoria, Valor
        final_df = final_df[['Data', 'Categoria', 'Valor']]

        # Define o caminho e o nome do arquivo de saída
        output_csv_path = '../csv/despesas_processadas.csv'
        
        # Remove duplicidades
        final_df.drop_duplicates(inplace=True)
        
        # Salva o DataFrame em um arquivo CSV
        final_df.to_csv(output_csv_path, sep=';', index=False)
        
        print(f"\n💾5. Dados processados e salvos em: {output_csv_path}")
        print("\n--- Primeiras 5 linhas do arquivo gerado:")
        preview_linhas = final_df.head().to_string()
        preview_com_recuo = "\n".join("        " + linha for linha in preview_linhas.split("\n"))        
        print(preview_com_recuo)
        
        # --- MÉTRICAS DE AUDITORIA FINAL ---
        final_df['Valor_num_temp'] = final_df['Valor'].str.replace(',', '.').astype(float)
        total_linhas_final = len(final_df)
        valor_total_final = final_df['Valor_num_temp'].sum()
        
        # Cálculo das diferenças (o que foi considerado duplicata)
        linhas_duplicadas = total_linhas_bruto - total_linhas_final - linhas_removidas_filtros
        valor_duplicadas = valor_total_bruto - valor_total_final - valor_removido_filtros
        
        # --- PAINEL DE AUDITORIA ---
        print("\n==================================================")
        print("📋6. RELATÓRIO DE RECONCILIAÇÃO (AUDITORIA DE DADOS)")
        print("==================================================")
        print(f"📥 Total extraído dos arquivos: {total_linhas_bruto} linhas | R$ {valor_total_bruto:.2f}")
        print(f"🧹 Removidos por filtro (Saldos etc.): {linhas_removidas_filtros} linhas | R$ {valor_removido_filtros:.2f}")
        print(f"👥 Duplicatas eliminadas: {linhas_duplicadas} linhas | R$ {valor_duplicadas:.2f}")
        print(f"💾 Gravados no CSV Final: {total_linhas_final} lines | R$ {valor_total_final:.2f}")
        print("--------------------------------------------------")

        # A prova dos nove:
        diferenca = (valor_total_bruto - (valor_total_final + valor_removido_filtros + valor_duplicadas))
        if abs(diferenca) < 0.01:
            print("✅ RECONCILIAÇÃO PERFEITA: A matemática bateu 100%!")
        else:
            print(f"❌ ALERTA: Há uma quebra de integridade de R$ {diferenca:.2f} não explicada!")
        print("==================================================")
    else:
        print("\n⚠️Nenhum dado válido para processar.")