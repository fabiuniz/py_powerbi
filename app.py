# app.py
import base64
import pandas as pd
import io
from dash import Dash, html, dcc, callback, Output, Input
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
        df['Valor'] = df['Valor'].astype(str).str.replace(' ', '', regex=False)
        df['Valor'] = df['Valor'].str.replace('R$', '', regex=False)
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
app = Dash(__name__)
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
    df_distribuicao = df_gasto_categoria.sort_values('Valor', ascending=False)
    top_categorias = df_distribuicao.head(6)  # Top 6 categorias
    outros_valor = df_distribuicao[6:]['Valor'].sum()  # Soma das demais
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

# Função para carregar e limpar dados de despesas pessoais
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
        df['Valor'] = df['Valor'].astype(str).str.replace(',', '.', regex=False)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        df['Valor'] = df['Valor'].apply(lambda x: abs(x) if pd.notnull(x) and x < 0 else x)
        
        # Remover linhas com valores nulos após conversão
        df = df.dropna(subset=['Data', 'Categoria', 'Valor'], how='any')
        logger.info(f"Linhas após limpeza final: {len(df)}")
        logger.info(f"Primeiras linhas de df_despesas_pessoais: \n{df.head().to_string()}")
        
        # Verificar transações específicas
        logger.info(f"Transações para 07/04/2025: \n{df[df['Data'] == '2025-04-07'].to_string()}")
        
        if df.empty:
            logger.warning("Nenhum dado válido encontrado após limpeza")
        else:
            logger.info(f"Dados de despesas pessoais carregados de {file_path} com {len(df)} linhas")
        return df
    except FileNotFoundError:
        logger.error(f"Arquivo {file_path} não encontrado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Carregar os dados de despesas pessoais
df_despesas_pessoais = load_personal_expenses_data()

# Layout do Dashboard de Despesas Pessoais
def layout_despesas_pessoais():
    if df_despesas_pessoais.empty:
        logger.warning("Dados de despesas pessoais vazios ou não carregados")
        return html.Div("Erro: Dados de despesas pessoais não carregados.")
    
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
    df_distribuicao = df_despesas_pessoais.groupby('Categoria')['Valor'].sum().reset_index()
    df_distribuicao = df_distribuicao.sort_values('Valor', ascending=False)
    top_categorias = df_distribuicao.head(6)
    outros_valor = df_distribuicao['Valor'][6:].sum()
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
            'MERCADO': '#e74c3c',        # Red
            'CONDOMINIO': '#3498db',     # Blue
            'TELEFONE': '#2ecc71',       # Green
            'INTERNET': '#f1c40f',       # Yellow
            'RESTAURANTE': '#9b59b6',    # Purple
            'Desconhecida': '#7f8c8d'    # Gray
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
        hovertemplate='Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<br>Categoria: %{customdata}'
    )

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
        html.H2("Dashboard de Despesas Pessoais", className="text-2xl font-bold mb-4 text-gray-800"),
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
            html.Div(insights, className="dashboard-section")
        ])
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
    html.Div(className="header", children=[
        html.H1("Dashboard Geral da Empresa", className="text-4xl font-bold"),
    ]),
    html.Div(className="nav-bar", children=[
        dcc.Link("Geral", href="/", className="nav-link"),
        dcc.Link("Financeiro", href="/financeiro", className="nav-link"),
        dcc.Link("Logística", href="/logistica", className="nav-link"),
        dcc.Link("Vendas", href="/vendas", className="nav-link"),
        dcc.Link("Despesas", href="/despesas", className="nav-link"),
        dcc.Link("Despesas Pessoais", href="/despesas-pessoais", className="nav-link"),
    ]),
    html.Div(id='page-content', className="content")
])

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
    else:
        return layout_geral()

# --- 8. Execução da Aplicação ---
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)