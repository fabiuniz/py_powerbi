# app.py
import base64
import pandas as pd
import io
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table,clientside_callback
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging



# Configurar o logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Salva logs em um arquivo
        logging.StreamHandler()  # Exibe logs no console
    ]
)
logger = logging.getLogger(__name__)

# --- 1. Dados ---

# Função para carregar e limpar dados financeiros
def load_financial_data(file_path='csv/relatorio.csv'):
    try:
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        df.columns = [
            'Data', 'ID Transação', 'Tipo', 'Categoria', 'ID Detalhe',
            'Conta', 'Status Pagamento', 'Valor Formatado', 'Valor'
        ]
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df['Tipo'] = df['Tipo'].str.strip()  # Remove espaços em branco
        # Removendo espaços, R$ e tratando separadores
        df['Valor'] = df['Valor'].astype(str).str.replace('R$', '', regex=False).str.strip()
        df['Valor'] = df['Valor'].str.replace(' ', '', regex=False)
        # A vacina: Remove ponto de milhar antes de trocar a vírgula
        df['Valor'] = df['Valor'].str.replace('.', '', regex=False)
        df['Valor'] = df['Valor'].str.replace(',', '.', regex=False)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        logger.info(f"Dados financeiros carregados de {file_path} com {len(df)} linhas")
        logger.info(f"Valores únicos em 'Tipo': {df['Tipo'].unique()}")
        return df
    except FileNotFoundError:
        logger.error(f"Arquivo {file_path} não encontrado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Função para carregar dados de setores
def load_sectors_data(file_path='csv/setores.csv'):
    try:
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        logger.info(f"Dados de setores carregados de {file_path} com {len(df)} linhas")
        return df
    except FileNotFoundError:
        logger.error(f"Arquivo {file_path} não encontrado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Função para carregar e limpar dados de logística
def load_logistics_data(file_path='csv/historico_importacao.csv'):
    try:
        df = pd.read_csv(file_path, sep=',', encoding='utf-8')
        logger.info(f"Colunas em {file_path}: {list(df.columns)}")
        df['Data da Coleta'] = pd.to_datetime(df['Data da Coleta'], format='%d/%m/%Y', errors='coerce')
        df['Data da Entrega'] = pd.to_datetime(df['Data da Entrega'], format='%d/%m/%Y', errors='coerce')
        df['Peso (kg)'] = pd.to_numeric(df['Peso (kg)'], errors='coerce')
        df['Volume (cbm)'] = pd.to_numeric(df['Volume (cbm)'], errors='coerce')
        df['Prazo Realizado'] = pd.to_numeric(df['Prazo Realizado'], errors='coerce')
        df['Prazo Contratado'] = pd.to_numeric(df['Prazo Contratado'], errors='coerce')
        logger.info(f"Dados de logística carregados de {file_path} com {len(df)} linhas")
        return df
    except FileNotFoundError:
        logger.error(f"Arquivo {file_path} não encontrado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Função para carregar e limpar dados de vendas
def load_sales_data(file_path='csv/pedidos.csv'):
    try:
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df['Data_Entrega'] = pd.to_datetime(df['Data_Entrega'], format='%d/%m/%Y', errors='coerce')
        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
        df['Total'] = df['Total'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
        logger.info(f"Dados de vendas carregados de {file_path} com {len(df)} linhas")
        return df
    except FileNotFoundError:
        logger.error(f"Arquivo {file_path} não encontrado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Carregar os dados
df_financeiro = load_financial_data()
df_setor = load_sectors_data()
df_logistica = load_logistics_data()
df_vendas = load_sales_data()

# --- 2. Inicialização do Dash ---
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Necessário para o Gunicorn no Docker

# Estilo CSS para o fundo e elementos do dashboard
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Dashboard Geral</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .header { 
                background-color: #2c3e50; 
                color: white; 
                padding: 20px; 
                text-align: center; 
            }
            .nav-bar { 
                background-color: #34495e; 
                padding: 10px; 
                display: flex; 
                justify-content: center; 
                gap: 20px; 
            }
            .nav-link { 
                color: white; 
                text-decoration: none; 
                font-weight: bold; 
            }
            .nav-link:hover { 
                color: #3498db; 
            }
            .content { 
                padding: 20px; 
                max-width: 1200px; 
                margin: 0 auto; 
            }
            .card-container { 
                display: flex; 
                gap: 20px; 
                justify-content: center; 
                flex-wrap: wrap; 
                margin-bottom: 20px; 
            }
            .card { 
                background-color: white; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                text-align: center; 
                min-width: 200px; 
            }
            .dashboard-section { 
                background-color: white; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- 3. Layouts dos Dashboards ---

def layout_financeiro():
    if df_financeiro.empty:
        logger.warning("Dados financeiros vazios ou não carregados")
        return html.Div("Erro: Dados financeiros não carregados.")
    
    # Certifique-se de que 'Data' é datetime
    df_financeiro['Data'] = pd.to_datetime(df_financeiro['Data'], errors='coerce')

    # Calcular métricas financeiras
    total_entradas = df_financeiro[df_financeiro['Tipo'] == 'Entradas']['Valor'].sum()
    total_saidas = abs(df_financeiro[df_financeiro['Tipo'] == 'Saídas']['Valor'].sum())  # Use abs para exibir positivo
    saldo_total = total_entradas + df_financeiro[df_financeiro['Tipo'] == 'Saídas']['Valor'].sum()

    # Gráfico de Linha: Entradas e Saídas Mensais
    # Transformar Saídas em valores positivos para visualização
    df_plot = df_financeiro.copy()
    df_plot['Valor'] = df_plot.apply(lambda x: abs(x['Valor']) if x['Tipo'] == 'Saídas' else x['Valor'], axis=1)
    df_entradas_saidas_monthly = df_plot.groupby([pd.Grouper(key='Data', freq='ME'), 'Tipo'])['Valor'].sum().unstack(fill_value=0).reset_index()
    logger.info(f"Dados relatorios para gráfico: \n{df_entradas_saidas_monthly}")
    
    if 'Entradas' not in df_entradas_saidas_monthly.columns:
        df_entradas_saidas_monthly['Entradas'] = 0
    if 'Saídas' not in df_entradas_saidas_monthly.columns:
        df_entradas_saidas_monthly['Saídas'] = 0
    
    fig_entradas_saidas = px.line(
        df_entradas_saidas_monthly,
        x='Data',
        y=['Entradas', 'Saídas'],
        title='Entradas e Saídas Mensais',
        labels={"Data": "Mês", "value": "Valor (R$)", "variable": "Tipo de Transação"},
        color_discrete_map={'Entradas': '#27ae60', 'Saídas': '#e74c3c'},
        template="plotly_white"
    )
    fig_entradas_saidas.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Mês", yaxis_title="Valor (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0'),
        legend_title_text='Tipo'
    )
    fig_entradas_saidas.update_yaxes(rangemode='tozero')
    fig_entradas_saidas.update_traces(hovertemplate='Mês: %{x|%b %Y}<br>Tipo: %{variable}<br>Valor: R$ %{y:,.2f}')
    fig_entradas_saidas.update_layout(hovermode="x unified")

    # Gráfico de Saldo Acumulado
    df_financeiro_monthly_saldo = df_financeiro.set_index('Data').resample('ME')['Valor'].sum().reset_index()
    df_financeiro_monthly_saldo['Saldo Acumulado'] = df_financeiro_monthly_saldo['Valor'].cumsum()
    fig_saldo_tempo = px.line(df_financeiro_monthly_saldo, x='Data', y='Saldo Acumulado',
                              title='Saldo Acumulado ao Longo do Tempo',
                              labels={'Data': 'Data', 'Saldo Acumulado': 'Saldo (R$)'})
    fig_saldo_tempo.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Data", yaxis_title="Saldo (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # Gráfico de Barras: Entradas e Saídas por Categoria
    df_categorias = df_plot.groupby(['Tipo', 'Categoria'])['Valor'].sum().reset_index()
    fig_categorias = px.bar(df_categorias, x='Categoria', y='Valor', color='Tipo',
                            title='Entradas e Saídas por Categoria',
                            barmode='group',
                            color_discrete_map={'Entradas': '#27ae60', 'Saídas': '#e74c3c'})
    fig_categorias.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Categoria", yaxis_title="Valor (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # Gráfico de Rosca: Despesas por Setor
    df_financeiro_com_setor = pd.merge(df_financeiro, df_setor, left_on='Conta', right_on='Centro de Custo', how='left')
    df_despesas_por_setor = df_financeiro_com_setor[df_financeiro_com_setor['Tipo'] == 'Saídas'].copy()
    df_despesas_por_setor_relatorio = df_despesas_por_setor.groupby('Setor')['Valor'].apply(lambda x: abs(x).sum()).reset_index()
    fig_donut_setor = px.pie(
        df_despesas_por_setor_relatorio, values='Valor', names='Setor',
        title='Despesas por Setor', hole=0.5, template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_donut_setor.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), legend_title_text='Setor', title_x=0.5
    )
    fig_donut_setor.update_traces(hovertemplate='Setor: %{label}<br>Despesa: R$ %{value:,.2f}<br>Porcentagem: %{percent}')

    return html.Div([
        html.H2("Dashboard Financeiro", className="text-2xl font-bold mb-4 text-gray-800"),
        html.Div(className="card-container", children=[
            html.Div(className="card", children=[
                html.H3("Total de Entradas"),
                html.P(f"R$ {total_entradas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
            html.Div(className="card", children=[
                html.H3("Total de Saídas"),
                html.P(f"R$ {total_saidas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
            html.Div(className="card", children=[
                html.H3("Saldo Total"),
                html.P(f"R$ {saldo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
        ]),
        html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6", children=[
            dcc.Graph(figure=fig_entradas_saidas, className="dashboard-section"),
            dcc.Graph(figure=fig_saldo_tempo, className="dashboard-section"),
            dcc.Graph(figure=fig_categorias, className="dashboard-section"),
            dcc.Graph(figure=fig_donut_setor, className="dashboard-section")
        ])
    ])

# Layout do Dashboard de Logística
def layout_logistica():
    if df_logistica.empty:
        logger.warning("Dados de logística vazios ou não carregados")
        return html.Div("Erro: Dados de logística não carregados.")
    
    # Métricas de Logística
    total_envios = len(df_logistica)
    custo_total = df_logistica['Peso (kg)'].sum()  # Usando peso como proxy para custo
    tipo_col = 'Tipo de serviço'  # Nome esperado
    if tipo_col not in df_logistica.columns:
        logger.warning(f"Coluna '{tipo_col}' não encontrada em df_logistica. Colunas disponíveis: {list(df_logistica.columns)}")
        tipo_col = None
        status_counts = pd.DataFrame({'Serviço': ['N/A'], 'Contagem': [0]})
    else:
        status_counts = df_logistica[tipo_col].value_counts().reset_index()
        status_counts.columns = ['Serviço', 'Contagem']

    # Gráfico de Pizza: Tipos de Serviço
    fig_status = px.pie(status_counts, values='Contagem', names='Serviço',
                        title='Distribuição por Tipo de Serviço',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_status.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Indicador OTD (On Time Delivery)
    df_logistica['OTD'] = df_logistica['Prazo Realizado'] <= df_logistica['Prazo Contratado']
    otd_por_modal = df_logistica.groupby('Tipo')['OTD'].mean().reset_index()
    otd_por_modal['OTD'] = otd_por_modal['OTD'] * 100
    fig_otd = px.bar(otd_por_modal, x='Tipo', y='OTD',
                     title='On Time Delivery (OTD) por Modal',
                     labels={'Tipo': 'Modal', 'OTD': 'OTD (%)'},
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig_otd.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis=dict(showgrid=True, gridcolor='#e0e0e0'),
        yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    return html.Div([
        html.H2("Dashboard de Logística", className="text-2xl font-bold mb-4 text-gray-800"),
        html.Div(className="card-container", children=[
            html.Div(className="card", children=[
                html.H3("Total de Embarques"),
                html.P(f"{total_envios}")
            ]),
            html.Div(className="card", children=[
                html.H3("Peso Total (kg)"),
                html.P(f"{custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
        ]),
        html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6", children=[
            dcc.Graph(figure=fig_status, className="dashboard-section"),
            dcc.Graph(figure=fig_otd, className="dashboard-section")
        ])
    ])

def layout_vendas():
    if df_vendas.empty:
        return html.Div("Erro: Dados de vendas não carregados.")
    
    # Métricas de Vendas
    total_vendas = df_vendas['Total'].sum()
    total_produtos_vendidos = df_vendas['Quantidade'].sum()
    vendas_por_produto = df_vendas.groupby('Produto')['Total'].sum().sort_values(ascending=False).reset_index()

    # Gráfico de Barras: Vendas por Produto
    fig_vendas_produto = px.bar(vendas_por_produto, x='Produto', y='Total',
                                title='Vendas Totais por Produto',
                                color_discrete_sequence=px.colors.qualitative.Set2)
    fig_vendas_produto.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Produto", yaxis_title="Total de Venda (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # Gráfico de Sazonalidade: Volume por Mês
    df_vendas_monthly = df_vendas.groupby(pd.Grouper(key='Data', freq='ME'))['Quantidade'].sum().reset_index()
    fig_sazonalidade = px.line(df_vendas_monthly, x='Data', y='Quantidade',
                               title='Volume de Produção por Mês (Sazonalidade)',
                               labels={'Data': 'Mês', 'Quantidade': 'Volume'})
    fig_sazonalidade.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Mês", yaxis_title="Volume",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    return html.Div([
        html.H2("Dashboard de Vendas", className="text-2xl font-bold mb-4 text-gray-800"),
        html.Div(className="card-container", children=[
            html.Div(className="card", children=[
                html.H3("Total de Vendas"),
                html.P(f"R$ {total_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
            html.Div(className="card", children=[
                html.H3("Total de Produtos Vendidos"),
                html.P(f"{total_produtos_vendidos}")
            ]),
        ]),
        html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6", children=[
            dcc.Graph(figure=fig_vendas_produto, className="dashboard-section"),
            dcc.Graph(figure=fig_sazonalidade, className="dashboard-section")
        ])
    ])
# --- 5. Layout do Dashboard de Despesas ---
def layout_despesas():
    if df_financeiro.empty:
        logger.warning("Dados financeiros vazios ou não carregados")
        return html.Div("Erro: Dados financeiros não carregados.")
    
    # Filtrar apenas saídas para despesas
    df_despesas = df_financeiro[df_financeiro['Tipo'] == 'Saídas'].copy()
    df_despesas['Valor'] = df_despesas['Valor'].apply(abs)  # Transformar em valores positivos para visualização

    # Métricas de Despesas
    total_despesas = df_despesas['Valor'].sum()
    media_despesa = df_despesas['Valor'].mean() if len(df_despesas) > 0 else 0
    num_transacoes = len(df_despesas)

    # Gráfico de Linha: Despesas Mensais
    df_despesas_mensal = df_despesas.groupby(pd.Grouper(key='Data', freq='ME'))['Valor'].sum().reset_index()
    fig_despesas_mensal = px.line(
        df_despesas_mensal, x='Data', y='Valor',
        title='Despesas Mensais',
        labels={'Data': 'Mês', 'Valor': 'Valor (R$)'},
        template="plotly_white",
        color_discrete_sequence=['#e74c3c']
    )
    fig_despesas_mensal.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Mês", yaxis_title="Valor (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )
    fig_despesas_mensal.update_yaxes(rangemode='tozero')
    fig_despesas_mensal.update_traces(hovertemplate='Mês: %{x|%b %Y}<br>Valor: R$ %{y:,.2f}')

    # Gráfico de Barras Horizontais: Gasto Total por Categoria (Top 5)
    df_gasto_categoria = df_despesas.groupby('Categoria')['Valor'].sum().reset_index()
    df_gasto_categoria_top5 = df_gasto_categoria.sort_values('Valor', ascending=False).head(5)
    fig_gasto_categoria = px.bar(
        df_gasto_categoria_top5, y='Categoria', x='Valor',
        title='Gasto Total por Categoria (Top 5)',
        labels={'Categoria': 'Categoria', 'Valor': 'Valor (R$)'},
        color_discrete_sequence=['#e74c3c'],
        template="plotly_white",
        orientation='h'
    )
    fig_gasto_categoria.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Valor (R$)", yaxis_title="Categoria",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # Gráfico de Barras Verticais: Frequência de Transações por Categoria (Top 5)
    df_frequencia_categoria = df_despesas['Categoria'].value_counts().reset_index()
    df_frequencia_categoria.columns = ['Categoria', 'Contagem']
    df_frequencia_categoria_top5 = df_frequencia_categoria.head(5)
    fig_frequencia_categoria = px.bar(
        df_frequencia_categoria_top5, x='Categoria', y='Contagem',
        title='Frequência de Transações por Categoria (Top 5)',
        labels={'Categoria': 'Categoria', 'Contagem': 'Número de Transações'},
        color_discrete_sequence=['#e74c3c'],
        template="plotly_white"
    )
    fig_frequencia_categoria.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Categoria", yaxis_title="Número de Transações",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # Gráfico de Rosca: Distribuição de Gastos (Top 5-7 + Outros)
    tops = 10
    df_distribuicao = df_gasto_categoria.sort_values('Valor', ascending=False)
    top_categorias = df_distribuicao.head(tops)  # Top 6 categorias
    outros_valor = df_distribuicao[tops:]['Valor'].sum()  # Soma das demais
    df_distribuicao_final = pd.concat([
        top_categorias,
        pd.DataFrame({'Categoria': ['Outros'], 'Valor': [outros_valor]})
    ])
    fig_donut_despesas = px.pie(
        df_distribuicao_final, values='Valor', names='Categoria',
        title='Distribuição de Gastos',
        hole=0.5, template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_donut_despesas.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), legend_title_text='Categoria', title_x=0.5
    )
    fig_donut_despesas.update_traces(hovertemplate='Categoria: %{label}<br>Despesa: R$ %{value:,.2f}<br>Porcentagem: %{percent}')

    # Gráfico de Dispersão: Picos de Gasto Diário
    df_gasto_diario = df_despesas.groupby('Data')['Valor'].sum().reset_index()
    fig_picos_diario = px.scatter(
        df_gasto_diario, x='Data', y='Valor',
        title='Picos de Gasto Diário',
        labels={'Data': 'Data', 'Valor': 'Gasto Diário (R$)'},
        color_discrete_sequence=['#e74c3c'],
        template="plotly_white"
    )
    fig_picos_diario.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Data", yaxis_title="Gasto Diário (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # Insights e Anomalias
    top_categoria = df_gasto_categoria.loc[df_gasto_categoria['Valor'].idxmax()]
    top_frequencia = df_frequencia_categoria.loc[df_frequencia_categoria['Contagem'].idxmax()]
    pico_diario = df_gasto_diario.loc[df_gasto_diario['Valor'].idxmax()]
    tendencia = "aumento" if df_despesas_mensal['Valor'].iloc[-1] > df_despesas_mensal['Valor'].iloc[0] else "diminuição"
    insights = [
        html.P(f"- **Categoria Dominante**: A categoria '{top_categoria['Categoria']}' lidera com R$ {top_categoria['Valor']:,.2f}, indicando uma área significativa de despesa."),
        html.P(f"- **Frequência de Transações**: '{top_frequencia['Categoria']}' tem o maior número de transações ({top_frequencia['Contagem']}), sugerindo gastos recorrentes."),
        html.P(f"- **Tendência Mensal**: Observa-se uma tendência de {tendencia} nos gastos mensais, com base nos dados iniciais e finais."),
        html.P(f"- **Pico Diário**: O maior gasto diário foi de R$ {pico_diario['Valor']:,.2f} em {pico_diario['Data'].strftime('%d/%m/%Y')}, possivelmente devido a uma compra excepcional ou evento sazonal.")
    ]
    anomalias = []
    if pico_diario['Valor'] > total_despesas * 0.1:  # Considera pico anômalo se >10% do total
        anomalias.append(html.P(f"- **Anomalia Detectada**: Gasto elevado de R$ {pico_diario['Valor']:,.2f} em {pico_diario['Data'].strftime('%d/%m/%Y')} excede 10% do total de despesas (R$ {total_despesas:,.2f}), sugerindo uma compra atípica ou erro de registro."))

    # Recomendações
    recomendacoes = [
        html.P("- **Revisão de Categorias Principais**: Analise a categoria dominante '{}' para identificar oportunidades de redução de custos, como negociar com fornecedores ou substituir produtos.".format(top_categoria['Categoria'])),
        html.P("- **Controle de Gastos Recorrentes**: Monitore as transações frequentes em '{}' para evitar acumulações desnecessárias; considere orçamentos mensais.".format(top_frequencia['Categoria'])),
        html.P("- **Investigação de Picos**: Investigue o pico de R$ {:.2f} em {} para confirmar se foi uma despesa planejada ou uma anomalia (e.g., compra emergencial, erro de entrada).".format(pico_diario['Valor'], pico_diario['Data'].strftime('%d/%m/%Y'))),
        html.P("- **Planejamento Orçamentário**: Estabeleça limites mensais e alertas para categorias de alto impacto, ajustando gastos com base na tendência de {} observada.".format(tendencia))
    ]

    return html.Div([
        html.H2("Dashboard de Despesas", className="text-2xl font-bold mb-4 text-gray-800"),
        html.Div(className="card-container", children=[
            html.Div(className="card", children=[
                html.H3("Total de Despesas"),
                html.P(f"R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
            html.Div(className="card", children=[
                html.H3("Média por Despesa"),
                html.P(f"R$ {media_despesa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
            html.Div(className="card", children=[
                html.H3("Número de Transações"),
                html.P(f"{num_transacoes:,}".replace(",", "."))
            ]),
        ]),
        html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6", children=[
            dcc.Graph(figure=fig_despesas_mensal, className="dashboard-section"),
            dcc.Graph(figure=fig_gasto_categoria, className="dashboard-section"),
            dcc.Graph(figure=fig_frequencia_categoria, className="dashboard-section"),
            dcc.Graph(figure=fig_donut_despesas, className="dashboard-section"),
            dcc.Graph(figure=fig_picos_diario, className="dashboard-section"),
            html.Div(className="dashboard-section", children=[
                html.H3("Insights e Anomalias", className="text-xl font-semibold mb-2 text-gray-800"),
                html.Ul(className="list-disc list-inside", children=insights + anomalias)
            ]),
            html.Div(className="dashboard-section", children=[
                html.H3("Recomendações", className="text-xl font-semibold mb-2 text-gray-800"),
                html.Ul(className="list-disc list-inside", children=recomendacoes)
            ])
        ])
    ])

# Layout do Dashboard de Despesas Gestor
def layout_despesas_pessoais():
    # Função para carregar e limpar dados de despesas Gestor
    def load_personal_expenses_data(file_path='csv/despesas.csv'):
        try:
            # Ler o arquivo como texto para verificar linhas
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            logger.info(f"Total de linhas no arquivo {file_path}: {len(lines)}")

            # Carregar o DataFrame
            df = pd.read_csv(
                file_path, 
                sep=';', 
                encoding='utf-8', 
                on_bad_lines=lambda x: logger.warning(f"Linha inválida ignorada: {x}"), 
                names=['Data', 'Categoria', 'Valor'], 
                skiprows=1, 
                engine='python'
            )
            logger.info(f"Linhas carregadas antes da limpeza: {len(df)}")

            # Remover linhas com valores nulos antes de conversão
            df = df.dropna(subset=['Data', 'Categoria', 'Valor'], how='any')
            logger.info(f"Linhas após remoção de nulos iniciais: {len(df)}")

            # Converter e limpar
            df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            # 1. Converte para string e limpa espaços extras
            df['Valor'] = df['Valor'].astype(str).str.strip()

            # 2. LIMPEZA TOTAL (Remove R$, espaços e o ponto de milhar ANTES de trocar a vírgula)
            df['Valor'] = df['Valor'].str.replace('R$', '', regex=False)
            df['Valor'] = df['Valor'].str.replace('.', '', regex=False) # Remove o ponto (1.345 -> 1345)
            df['Valor'] = df['Valor'].str.replace(',', '.', regex=False) # Troca vírgula por ponto (1345,83 -> 1345.83)

            # 3. Converte para número e garante que não seja nulo
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            # Isso remove depósitos, estornos ou saldos positivos do gráfico de despesas
            df = df[df['Valor'] < 0].copy()
            
            # 4. Transforma negativos em positivos (se houver)
            df['Valor'] = df['Valor'].abs()

            # 5. Só agora remove o que for realmente inválido
            df = df.dropna(subset=['Valor'])
            logger.info(f"Linhas após limpeza final: {len(df)}")
            logger.info(f"Primeiras linhas de df_despesas_pessoais: \n{df.head().to_string()}")

            # Verificar transações específicas
            logger.info(f"Transações para 07/04/2025: \n{df[df['Data'] == '2025-04-07'].to_string()}")

            if df.empty:
                logger.warning("Nenhum dado válido encontrado após limpeza")
            else:
                logger.info(f"Dados de despesas Gestor carregados de {file_path} com {len(df)} linhas")
            return df
        except FileNotFoundError:
            logger.error(f"Arquivo {file_path} não encontrado")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Erro ao carregar {file_path}: {str(e)}")
            return pd.DataFrame()

    # Carregar os dados de despesas Gestor
    df_despesas_pessoais = load_personal_expenses_data()

    if df_despesas_pessoais.empty:
        logger.warning("Dados de despesas Gestor vazios ou não carregados")
        return html.Div("Erro: Dados de despesas Gestor não carregados.")

    # --- Métricas ---
    total_despesas = df_despesas_pessoais['Valor'].sum()
    media_despesa = df_despesas_pessoais['Valor'].mean()
    num_transacoes = len(df_despesas_pessoais)

    # --- Gráfico 1: Gasto Total por Categoria (Top 5) ---
    df_gasto_categoria = df_despesas_pessoais.groupby('Categoria')['Valor'].sum().reset_index()
    df_gasto_categoria = df_gasto_categoria.sort_values('Valor', ascending=False).head(5)
    fig_gasto_categoria = px.bar(
        df_gasto_categoria, y='Categoria', x='Valor',
        title='Gasto Total por Categoria (Top 5)',
        labels={'Categoria': 'Categoria', 'Valor': 'Valor (R$)'},
        color_discrete_sequence=['#e74c3c'],
        template="plotly_white",
        orientation='h'
    )
    fig_gasto_categoria.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Valor (R$)", yaxis_title="Categoria",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # --- Gráfico 2: Frequência de Transações por Categoria (Top 5) ---
    df_freq_categoria = df_despesas_pessoais['Categoria'].value_counts().reset_index()
    df_freq_categoria.columns = ['Categoria', 'Contagem']
    df_freq_categoria = df_freq_categoria.sort_values('Contagem', ascending=False).head(5)
    fig_freq_categoria = px.bar(
        df_freq_categoria, x='Categoria', y='Contagem',
        title='Frequência de Transações por Categoria (Top 5)',
        labels={'Categoria': 'Categoria', 'Contagem': 'Número de Transações'},
        color_discrete_sequence=['#3498db'],
        template="plotly_white"
    )
    fig_freq_categoria.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Categoria", yaxis_title="Número de Transações",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    # --- Gráfico 3: Gasto Mensal ao Longo do Tempo ---
    df_gasto_mensal = df_despesas_pessoais.groupby(pd.Grouper(key='Data', freq='ME'))['Valor'].sum().reset_index()
    fig_gasto_mensal = px.line(
        df_gasto_mensal, x='Data', y='Valor',
        title='Gasto Mensal ao Longo do Tempo',
        labels={'Data': 'Mês', 'Valor': 'Valor (R$)'},
        color_discrete_sequence=['#e74c3c'],
        template="plotly_white"
    )
    fig_gasto_mensal.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Mês", yaxis_title="Valor (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )
    fig_gasto_mensal.update_yaxes(rangemode='tozero')
    fig_gasto_mensal.update_traces(hovertemplate='Mês: %{x|%b %Y}<br>Valor: R$ %{y:,.2f}')

    # --- Gráfico 4: Distribuição de Gastos (Rosca) ---
    tops = 20
    df_distribuicao = df_despesas_pessoais.groupby('Categoria')['Valor'].sum().reset_index()
    df_distribuicao = df_distribuicao.sort_values('Valor', ascending=False)
    top_categorias = df_distribuicao.head(tops)
    outros_valor = df_distribuicao['Valor'][tops:].sum()
    df_distribuicao_final = pd.concat([
        top_categorias,
        pd.DataFrame({'Categoria': ['Outros'], 'Valor': [outros_valor]})
    ])
    fig_distribuicao = px.pie(
        df_distribuicao_final, values='Valor', names='Categoria',
        title='Distribuição de Gastos',
        hole=0.5, template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_distribuicao.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), legend_title_text='Categoria', title_x=0.5
    )
    fig_distribuicao.update_traces(hovertemplate='Categoria: %{label}<br>Valor: R$ %{value:,.2f}<br>Porcentagem: %{percent}')

    # --- Gráfico 5: Picos de Gasto Diário ---
    df_gasto_diario = df_despesas_pessoais.groupby('Data')['Valor'].sum().reset_index()
    df_top_categoria = df_despesas_pessoais.groupby(['Data', 'Categoria'])['Valor'].sum().reset_index()
    df_top_categoria = df_top_categoria.loc[df_top_categoria.groupby('Data')['Valor'].idxmax()].drop_duplicates(subset=['Data'])
    df_gasto_diario = df_gasto_diario.merge(df_top_categoria[['Data', 'Categoria']], on='Data', how='left')
    df_gasto_diario['Categoria'] = df_gasto_diario['Categoria'].fillna('Desconhecida')
    logger.info(f"df_gasto_diario após merge: \n{df_gasto_diario.to_string()}")
    logger.info(f"Total para 07/04/2025 em df_gasto_diario: \n{df_gasto_diario[df_gasto_diario['Data'] == '2025-04-07'].to_string()}")
    fig_picos_diario = px.scatter(
        df_gasto_diario, x='Data', y='Valor',
        title='Picos de Gasto Diário',
        labels={'Data': 'Data', 'Valor': 'Valor (R$)'},
        color='Categoria',  # Colorir pontos pela categoria
        color_discrete_map={
            'MERCADO': '#e74c3c',      # Red
            'CONDOMINIO': '#3498db',   # Blue
            'TELEFONE': '#2ecc71',      # Green
            'INTERNET': '#f1c40f',      # Yellow
            'RESTAURANTE': '#9b59b6',  # Purple
            'Desconhecida': '#7f8c8d'  # Gray
        },  # Mapa de cores personalizado
        template="plotly_white",
        custom_data=['Categoria']
    )
    fig_picos_diario.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=100, b=40),  # Aumentar a margem superior
        xaxis_title="Data", yaxis_title="Valor (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0'),
        title=dict(
            y=0.95,  # Ajustar a posição do título para evitar sobreposição
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        legend=dict(
            title='Categoria',
            orientation='h',
            yanchor='bottom',
            y=1.02,  # Mantém a legenda acima do gráfico
            xanchor='right',
            x=1,
            font=dict(size=10),
            itemsizing='constant'
        )
    )
    fig_picos_diario.update_traces(
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br>" +
            "<b>Valor:</b> R$ %{y:,.2f}<br>" +
            "<b>Categoria:</b> %{customdata[0]}"
    )

    # --- Gráfico 6: Gasto Mensal por Categoria (Linhas) ---
    df_gasto_mensal_categoria = df_despesas_pessoais.groupby([
        pd.Grouper(key='Data', freq='ME'),
        'Categoria'
    ])['Valor'].sum().reset_index()
    
    # Criar um gráfico de linhas para cada categoria
    fig_gasto_mensal_categoria = px.line(
        df_gasto_mensal_categoria, 
        x='Data', 
        y='Valor', 
        color='Categoria', # Esta linha faz o Plotly criar uma linha para cada valor único na coluna 'Categoria'
        title='Gasto Mensal por Categoria',
        labels={'Data': 'Mês', 'Valor': 'Valor (R$)', 'Categoria': 'Categoria'},
        template="plotly_white"
    )
    
    fig_gasto_mensal_categoria.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Mês", yaxis_title="Valor (R$)",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )
    fig_gasto_mensal_categoria.update_yaxes(rangemode='tozero')
    hovertemplate='Mês: %{x|%b %Y}<br>Categoria: %{customdata}<br>Valor: R$ %{y:,.2f}'


    # --- Análise de Insights e Anomalias ---
    top_categoria = df_gasto_categoria.iloc[0]['Categoria']
    top_valor = df_gasto_categoria.iloc[0]['Valor']
    pico_diario = df_gasto_diario.loc[df_gasto_diario['Valor'].idxmax()]
    pico_data = pico_diario['Data']
    pico_valor = pico_diario['Valor']
    tendencia = "aumento" if df_gasto_mensal['Valor'].iloc[-1] > df_gasto_mensal['Valor'].iloc[0] else "redução"
    insights = html.Div([
        html.H3("Insights e Anomalias", className="text-xl font-semibold mb-2 text-gray-800"),
        html.Ul(className="list-disc list-inside", children=[
            html.Li(f"Categoria Dominante: '{top_categoria}' lidera os gastos com R$ {top_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            html.Li(f"Pico de Gasto: O maior gasto diário foi R$ {pico_valor:,.2f} em {pico_data.strftime('%d/%m/%Y')}, possivelmente devido a compras excepcionais ou emergenciais.".replace(",", "X").replace(".", ",").replace("X", ".")),
            html.Li(f"Tendência: Observa-se uma tendência de {tendencia} nos gastos mensais, sugerindo necessidade de revisão do orçamento."),
            html.Li("Anomalias: Verificar gastos elevados em dias específicos, como o pico identificado, para confirmar se são justificados ou erros.")
        ]),
        html.H3("Recomendações", className="text-xl font-semibold mb-2 text-gray-800"),
        html.Ul(className="list-disc list-inside", children=[
            html.Li(f"Reduzir gastos em '{top_categoria}' por meio de negociações ou alternativas mais baratas."),
            html.Li("Monitorar dias de picos para evitar gastos impulsivos ou não planejados."),
            html.Li("Estabelecer um limite mensal de gastos com base na tendência observada para melhor controle financeiro.")
        ])
    ])

    return html.Div([
        html.H2("Dashboard de Despesas Gestor", className="text-2xl font-bold mb-4 text-gray-800"),
        html.Div(className="card-container", children=[
            html.Div(className="card", children=[
                html.H3("Total de Despesas"),
                html.P(f"R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
            html.Div(className="card", children=[
                html.H3("Média por Despesa"),
                html.P(f"R$ {media_despesa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ]),
            html.Div(className="card", children=[
                html.H3("Número de Transações"),
                html.P(f"{num_transacoes:,}".replace(",", "."))
            ]),
        ]),
        html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6", children=[
            dcc.Graph(figure=fig_gasto_categoria, className="dashboard-section"),
            dcc.Graph(figure=fig_freq_categoria, className="dashboard-section"),
            dcc.Graph(figure=fig_gasto_mensal, className="dashboard-section"),
            dcc.Graph(figure=fig_distribuicao, className="dashboard-section"),
            dcc.Graph(figure=fig_picos_diario, className="dashboard-section"),
            dcc.Graph(figure=fig_gasto_mensal_categoria, className="dashboard-section"), # Novo gráfico adicionado aqui
            html.Div(insights, className="dashboard-section")
        ])
    ])
import dash_table

def get_relatorio_despesas_por_mes():
    # Carregar os dados de despesas pessoais (assumindo que esta função já existe e funciona)
    # ou de um DataFrame global, se for o caso.
    # Exemplo: df_despesas_pessoais = load_personal_expenses_data()
    # Para este exemplo, usaremos o DataFrame de 'despesas.csv' fornecido
    try:
        df_despesas_pessoais = pd.read_csv(
            'csv/despesas.csv',
            sep=';',
            encoding='utf-8',
            parse_dates=['Data'],
            date_format='%d/%m/%Y'
        )
# 1. Garante que é string e limpa espaços
        df_despesas_pessoais['Valor'] = df_despesas_pessoais['Valor'].astype(str).str.strip()
        # 2. REMOVE PONTO DE MILHAR E TROCA VÍRGULA POR PONTO
        # Transforma "-1.234,72" -> "-1234.72"
        df_despesas_pessoais['Valor'] = (
            df_despesas_pessoais['Valor']
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
        # 3. Converte para número e trata sinais
        df_despesas_pessoais['Valor'] = pd.to_numeric(df_despesas_pessoais['Valor'], errors='coerce')
        # Filtra para manter apenas o que é menor que zero (Saídas)
        df_despesas_pessoais = df_despesas_pessoais[df_despesas_pessoais['Valor'] < 0].copy()
        df_despesas_pessoais['Valor'] = df_despesas_pessoais['Valor'].abs()
        # 4. Remove nulos (agora as linhas de milhar não serão removidas!)
        df_despesas_pessoais.dropna(subset=['Data', 'Categoria', 'Valor'], inplace=True)
    except FileNotFoundError:
        return html.Div("Erro: Arquivo csv/despesa.csv não encontrado.")
    except Exception as e:
        return html.Div(f"Erro ao processar dados: {str(e)}")

    if df_despesas_pessoais.empty:
        return html.Div("Erro: Dados de despesas pessoais vazios ou não carregados.")

    # Adicionar colunas de Ano e Mês
    df_despesas_pessoais['Ano'] = df_despesas_pessoais['Data'].dt.year
    df_despesas_pessoais['Mês'] = df_despesas_pessoais['Data'].dt.month

    # Preparar os dados para o relatório (similar à sua query SQL)
    # 1. Agrupar por Ano, Mês e Categoria, somando os valores
    df_relatorio_mensal = df_despesas_pessoais.groupby(['Ano', 'Categoria', 'Mês'])['Valor'].sum().unstack(fill_value=0)

    # 2. Renomear as colunas de mês para nomes em português
    nomes_meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    df_relatorio_mensal = df_relatorio_mensal.rename(columns=nomes_meses)

    # 3. Calcular a coluna 'Total' (soma de todos os meses)
    df_relatorio_mensal['Total'] = df_relatorio_mensal.sum(axis=1)

     # 4. Resetar o índice para transformar as colunas 'Ano' e 'Categoria' em colunas de dados
    df_relatorio_mensal = df_relatorio_mensal.reset_index()

    # Arredondar os valores para 2 casas decimais
    colunas_para_arredondar = list(nomes_meses.values()) + ['Total']
    df_relatorio_mensal[colunas_para_arredondar] = df_relatorio_mensal[colunas_para_arredondar].round(2)

    # Organizar a ordem das colunas para combinar com sua query
    colunas_ordenadas = ['Ano', 'Categoria'] + list(nomes_meses.values()) + ['Total']
    df_relatorio_mensal = df_relatorio_mensal[colunas_ordenadas]    

    # Criar um gráfico de barras para o relatório mensal, se desejado
    fig_relatorio_barras = px.bar(
        df_relatorio_mensal,
        x='Categoria',
        y=list(nomes_meses.values()),
        title='Gasto Mensal por Categoria',
        labels={'value': 'Valor (R$)', 'variable': 'Mês'},
        template="plotly_white"
    )

     # seja a escala máxima do eixo. Usei 4000 como exemplo, mas você
    # pode calcular o valor máximo real do seu DataFrame
    # se preferir `max_value = df_relatorio_mensal[colunas_para_arredondar].max().max() + 500`
    fig_relatorio_barras.update_yaxes(range=[0, 4000])

    # 2. Formatar o eixo y para exibir os valores como moeda, incluindo
    # o símbolo 'R$' e o formato de milhar com ponto
    fig_relatorio_barras.update_layout(
        xaxis_title="Categoria",
        yaxis_title="Valor (R$)",
        yaxis=dict(tickprefix='R$ ',
        tickformat=',.2f')
    )

    columns = []
    for i in df_relatorio_mensal.columns:
        col_def = {"name": i, "id": i}

        if i == 'Ano':
            col_def["type"] = "numeric"
        elif i in colunas_para_arredondar:
            col_def["type"] = "numeric"
            col_def["format"] = {
                'specifier': '.2f',
                'locale': {
                    'decimal': ',',
                    'group': '.'
                }
            }
        columns.append(col_def)

    return html.Div(children=[
        # Componente invisível que gerencia o download do arquivo
        dcc.Download(id="download-dataframe-csv"),
        
        html.H2("Relatório de Despesas Mensais por Categoria", className="text-2xl font-bold mb-4 text-gray-800"),
        dcc.Graph(figure=fig_relatorio_barras, className="dashboard-section"),    
        
        # Container das Tabelas
        html.Div(className="dashboard-section area-tabela", style={'overflowX': 'auto', 'width': '100%'}, children=[
            
            # 🗂️ OS DOIS BOTÕES LADO A LADO DO MESMO TAMANHO E ESTILO
            html.Div(className="area-botoes-lado-a-lado", children=[
                # Botão 1: Imprimir
                html.Button(
                    "🖨️ Imprimir",
                    id="btn-print",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#f8f9fa',
                        'color': '#212529',
                        'border': '1px solid #dee2e6',
                        'padding': '6px 12px',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontWeight': '600',
                        'fontSize': '12px',
                        'display': 'inline-flex',
                        'alignItems': 'center',
                    }
                ),
                # Botão 2: Exportar (Criado agora)
                html.Button(
                    "📥 Exportar Planilha (CSV)",
                    id="btn-export-csv",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#f8f9fa',
                        'color': '#212529',
                        'border': '1px solid #dee2e6',
                        'padding': '6px 12px',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontWeight': '600',
                        'fontSize': '12px',
                        'display': 'inline-flex',
                        'alignItems': 'center',
                    }
                ),
            ]),
            
            # Área de Impressão (Apenas as duas tabelas)
            html.Div(
                className="secao-impressao", 
                children=[
                    # 1. Tabela Principal (Export_format removido daqui)
                    dash_table.DataTable(
                        id='table-relatorio-mensal',
                        columns=columns,
                        data=df_relatorio_mensal.to_dict('records'),
                        style_data={'cursor': 'pointer'},
                        filter_action="native",
                        sort_action="native",
                        page_size=100,
                        style_table={'minWidth': '100%'},
                        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                        style_cell={
                            'minWidth': '100px',
                            'width': '100px',
                            'maxWidth': '100px',
                            'padding': '10px'
                        },
                    ),
                    # 2. Tabela de Total
                    dash_table.DataTable(
                        id='table-total-footer',
                        columns=columns,
                        data=[], 
                        style_table={'minWidth': '100%', 'marginTop': '-1px'},
                        style_header={'display': 'none'}, 
                        style_cell={
                            'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                            'fontWeight': 'bold', 'backgroundColor': '#f1f3f5'
                        },
                    )
                ]
            )
        ]),
        
        # Area de Detalhes
        html.Div(id='detalhe-itens-clicados', className="dashboard-section", style={'marginTop': '20px'})
    ])

def layout_geral():
    total_financeiro_geral = df_financeiro['Valor'].sum() if not df_financeiro.empty else 0
    total_envios_geral = len(df_logistica) if not df_logistica.empty else 0
    total_vendas_geral = df_vendas['Total'].sum() if not df_vendas.empty else 0
    # Métricas resumidas
    total_entradas = df_financeiro[df_financeiro['Tipo'] == 'Entradas']['Valor'].sum() if not df_financeiro.empty else 0
    total_saidas = abs(df_financeiro[df_financeiro['Tipo'] == 'Saídas']['Valor'].sum()) if not df_financeiro.empty else 0
    saldo_total = total_entradas + (df_financeiro[df_financeiro['Tipo'] == 'Saídas']['Valor'].sum() if not df_financeiro.empty else 0)
    total_envios = len(df_logistica) if not df_logistica.empty else 0
    total_pedidos = len(df_vendas) if not df_vendas.empty else 0
    total_vendas = df_vendas['Total'].sum() if not df_vendas.empty else 0
    total_despesas = abs(df_financeiro[df_financeiro['Tipo'] == 'Saídas']['Valor'].sum()) if not df_financeiro.empty else 0

    kpi_data = pd.DataFrame({
        'Indicador': ['Saldo Financeiro', 'Total de Embarques', 'Total de Vendas'],
        'Valor': [total_financeiro_geral, total_envios_geral, total_vendas_geral]
    })
    fig_kpi = px.bar(kpi_data, x='Indicador', y='Valor',
                     title='Resumo Geral de KPIs',
                     color_discrete_sequence=px.colors.qualitative.Set3)
    fig_kpi.update_layout(
        plot_bgcolor='white', paper_bgcolor='white', font_color='#2c3e50',
        margin=dict(l=40, r=40, t=60, b=40), xaxis_title="Indicador", yaxis_title="Valor",
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0'), yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
    )

    return html.Div([
        html.H2("Visão Geral dos Dashboards", className="text-2xl font-bold mb-4 text-gray-800"),
        html.Div(className="card-container", children=[
            html.A(
                href="/financeiro",
                style={"text-decoration": "none", "color": "inherit"},
                children=[
                    html.Div(className="card", children=[
                        html.H3("Saldo Financeiro"),
                        html.P(f"R$ {total_financeiro_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    ])
                ]
            ),
            html.A(
                href="/logistica",
                style={"text-decoration": "none", "color": "inherit"},
                children=[
                    html.Div(className="card", children=[
                        html.H3("Total de Embarques"),
                        html.P(f"{total_envios_geral}")
                    ])
                ]
            ),
            html.A(
                href="/vendas",
                style={"text-decoration": "none", "color": "inherit"},
                children=[
                    html.Div(className="card", children=[
                        html.H3("Total de Vendas"),
                        html.P(f"R$ {total_vendas_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    ])
                ]
            ),
            html.A(
                href="/despesas",
                style={"text-decoration": "none", "color": "inherit"},
                children=[
                    html.Div(className="card", children=[
                        html.H3("Total de Despesas"),
                        html.P(f"R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    ])
                ]
            ),
        ]),
        html.Div(className="grid grid-cols-1 gap-6", children=[
            dcc.Graph(figure=fig_kpi, className="dashboard-section"),
            html.Div(className="dashboard-section", children=[
                html.H3("Navegação para Dashboards Específicos"),
                html.Ul(className="list-disc list-inside", children=[
                    html.Li(dcc.Link("Dashboard Financeiro", href="/financeiro", className="text-blue-600 hover:underline")),
                    html.Li(dcc.Link("Dashboard de Logística", href="/logistica", className="text-blue-600 hover:underline")),
                    html.Li(dcc.Link("Dashboard de Vendas", href="/vendas", className="text-blue-600 hover:underline")),
                    html.Li(dcc.Link("Dashboard de Despesas", href="/despesas", className="text-blue-600 hover:underline")),
                ])
            ])
        ])
    ])

# --- 7. Configuração de Rotas ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='dummy-output', style={'display': 'none'},className="header", children=[
        html.H1("Dashboard Geral da Empresa", className="text-4xl font-bold"),
    ]),
    html.Div(className="nav-bar", children=[
        dcc.Link("Geral", href="/", className="nav-link"),
        dcc.Link("Financeiro", href="/financeiro", className="nav-link"),
        dcc.Link("Logística", href="/logistica", className="nav-link"),
        dcc.Link("Vendas", href="/vendas", className="nav-link"),
        dcc.Link("Despesas", href="/despesas", className="nav-link"),
        dcc.Link("Despesas Gestor", href="/despesas-pessoais", className="nav-link"),
        dcc.Link("Despesas Gestor2", href="/get_relatorio_despesas_por_mes", className="nav-link"),
    ]),
    html.Div(id='page-content', className="content")
])
#-----------------------------------------------------------
@callback(
    Output('detalhe-itens-clicados', 'children'),
    Input('table-relatorio-mensal', 'active_cell'),
    State('table-relatorio-mensal', 'derived_virtual_data'),
    prevent_initial_call=True
)
def mostrar_detalhes_itens(active_cell, virtual_data):
    if not active_cell or virtual_data is None:
        return html.P("💡 Dica: Clique em qualquer valor de mês na tabela acima para ver os itens detalhados.", 
                      className="text-gray-500 italic text-center p-4")

    col_id = active_cell['column_id']
    row_index = active_cell['row']
    
    # Lista de meses para validar o clique
    meses_lista = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    if col_id not in meses_lista:
        return html.P("Selecione um valor de mês para detalhamento.", className="text-warning")

    # Extrai os dados da célula clicada
    categoria_clicada = virtual_data[row_index]['Categoria']
    ano_clicado = virtual_data[row_index]['Ano']
    
    # Mapa para o filtro
    mapa_meses = {m: i+1 for i, m in enumerate(meses_lista)}
    mes_num = mapa_meses[col_id]

    try:
        # Carregamos o CSV original para buscar as linhas que compõem o total
        df_raw = pd.read_csv('csv/despesas.csv', sep=';', encoding='utf-8')
        df_raw['Data'] = pd.to_datetime(df_raw['Data'], format='%d/%m/%Y', errors='coerce')
        
        # Limpeza rápida para o filtro bater
        df_raw['Valor_Num'] = df_raw['Valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_raw['Valor_Num'] = pd.to_numeric(df_raw['Valor_Num'], errors='coerce')
        
        # Filtro mestre
        df_detalhe = df_raw[
            (df_raw['Categoria'] == categoria_clicada) & 
            (df_raw['Data'].dt.month == mes_num) & 
            (df_raw['Data'].dt.year == ano_clicado) &
            (df_raw['Valor_Num'] < 0)
        ].copy()
        
        df_detalhe['Valor'] = df_detalhe['Valor_Num'].abs()

        return html.Div([
            html.H3(f"📋 Detalhamento: {categoria_clicada} ({col_id}/{ano_clicado})", 
                    className="text-lg font-bold mb-3 text-blue-800"),
            dash_table.DataTable(
                data=df_detalhe[['Data', 'Categoria', 'Valor']].to_dict('records'),
                columns=[{"name": i, "id": i} for i in ['Data', 'Categoria', 'Valor']],
                style_header={'backgroundColor': '#2c3e50', 'color': 'white'},
                style_cell={'textAlign': 'left', 'padding': '8px'},
                page_size=10,
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f2f2f2'}]
            )
        ])
    except Exception as e:
        return html.P(f"Erro ao carregar detalhes: {str(e)}", className="text-danger")
    
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks && n_clicks > 0) {
            window.print();
        }
        return ""; // Retorna texto vazio para a nossa div invisível
    }
    """,
    Output("dummy-output", "children"),  # <--- Direcionado para a div de descarte
    Input("btn-print", "n_clicks"),
    prevent_initial_call=True
)
#---------------------------------------------------------------
@callback(
    Output('table-total-footer', 'data'),
    Input('table-relatorio-mensal', 'derived_virtual_data'),
    prevent_initial_call=True
)
def atualizar_rodape_dinamico(rows):
    if rows is None:
        return []    
    df_temp = pd.DataFrame(rows)    
    if df_temp.empty:
        return []
    # Lista de colunas para somar
    nomes_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro', 'Total']    
    # Criar dicionário de totais
    linha_total = {}
    for col in df_temp.columns:
        if col in nomes_meses:
            linha_total[col] = df_temp[col].sum()
        else:
            linha_total[col] = "" # Limpa colunas que não são somáveis            
    linha_total['Ano'] = 'Total'
    linha_total['Categoria'] = 'TOTAL FILTRADO'    
    return [linha_total]
#------------------------------------------------------------
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-export-csv", "n_clicks"),
    State("table-relatorio-mensal", "derived_virtual_data"), # Pega os dados filtrados/ordenados na tela
    prevent_initial_call=True,
)
def export_table_to_csv(n_clicks, virtual_data):
    if n_clicks > 0 and virtual_data:
        # Converte os dados ativos da tabela de volta para um DataFrame
        df_filtered = pd.DataFrame(virtual_data)
        
        # Retorna o arquivo CSV formatado para download
        return dcc.send_data_frame(df_filtered.to_csv, "relatorio_mensal.csv", index=False, sep=";", encoding="utf-8-sig")
    return None    
#------------------------------------------------------------
# Callback para navegação entre páginas
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/financeiro':
        return layout_financeiro()
    elif pathname == '/logistica':
        return layout_logistica()
    elif pathname == '/vendas':
        return layout_vendas()
    elif pathname == '/despesas':
        return layout_despesas()
    elif pathname == '/despesas-pessoais':
        return layout_despesas_pessoais()
    elif pathname == '/get_relatorio_despesas_por_mes':
        return get_relatorio_despesas_por_mes()
    else:
        return layout_geral()
#------------------------------------------------------------
# --- 8. Execução da Aplicação ---
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

    