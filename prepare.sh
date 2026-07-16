cd tratamento 
echo "🚀Iniciando processamento Python ---"
# Roda o python usando o caminho absoluto para evitar erros de diretório
python "trata_dados_b.py"


echo "🔄Atualizando arquivo de despesas oficial ---"
# Usa caminhos absolutos para a cópia
cp "../csv/despesas_processadas.csv" "../csv/despesas.csv"
echo "✅[OK] Arquivo copiado com sucesso."
