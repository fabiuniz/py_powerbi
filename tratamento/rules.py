# rules.py
categorization_rules = {
        'ACOUGUE': [r'CASA DE CAR',r'WEST BOI'],
        'AEROPORTO':[r'GRU '],
        'BANCO': [r'RSHOP PISTA',r'SEGURO CARTAO'],
        'BELEZA' :[r'ANGELA PE',r'TAIYANG'],
        'COSTURA' :[r'TIAGO MAQUI',r'FIVELAS',r'TECIDOS'],
        'CONDOMINIO': [
            {'descricao': r'PAG BOLETO|MOBILEPAG|CONDOMINIO|RESIDENCIAL', 'valor_entre': [-600.00, -380.00]},            
        ],
        'ESTACIONAMENTO': [r'Estacion',r'ESTAC ',r'PARK ',r'ESTAPAR',r'RSHOP-SP MARKET'],
        'FARMACIA': [r'GOYA PERFU',r'USEMAISFARM',r'DROGA',r'FARMACIA', r'DROGARIA',r'FARMA'],
        'GAS': [r' GAS ',r'INT COMGAS',r'COMGAS'],
        'GASOLINA': [r'AURUM',r'PETROL ',r'AUTOSUL', r'RSHOP AUTO POSTO', r'RSHOP-AUTO POSTO',r'N S FATIMA'],
        'HOTFRUIT': [r'FRUTAO',r'CHACARA DO',r'Hortifruti',r'HORTIFRU'],
        'IGREJA': [r'CONADIBE',r'ADS',r'SOCIEDADE B', r'ADSA'],
        'IMPRESORA':[r'PONTODOSCAR'],
        'INTERNET': [r'INTERNET', r'NET', r'CLARO'],
        'LUZ': [r'ELETROPAULO'],
        'MECANICO' :[r' AUTOPE',r'Mercadocar',r'PREMYER',r'CENTRO AUTO',r'CLIMATOA'],
        'MERCADO': [r'SUP CERCADAO',r'OXXO',r'PAO DE AC',r'MiniMercado',r'SUPERM',r'MERCEARIA',r'CHOCOLANDIA',r'EXTRA HIPER',r'ATACADAO',r'MERCADINHO',r'PANIF',r'PADARIA',r'CARREFOUR', r'RSHOP BIG BOM', r'RSHOP MERCADO ', r'RSHOP MARCO', r'RSHOP MUFFATO', r'SUPERMERCADO', r'RSHOP-MERCADO'],
        'MATERIAL' :[r'TINTAS'],
        'OUTROS': [r'EDUARDODIAS', r'MARIVANLIMA'],
        'PAPELARIA': [r'LAN HOUSE',r'KALUNGA'],
        'PREFEITURA':[r'INT PM SAO PAU',r'INT LICENC SP',r'INT MULTA ',r'IPTU'],        
        'RESTAURANTE': [r'ESFIHA',r'DOGDODIE',r'JIN JIN',r'MP CALDODE',r'MEI MEI',r'EXPRESS GRI',r'Cafeteria',r'CAFE ',r'MANIA DE CHU',r'SABORINI',r'EMPORIO',r'PONTO SP MA',r'DONALD',r'FRIED CHICKE',r'THE STEAK ',r'CHURRASCARI',r'SUSHI',r'AQUARELA ',r'FRIENDS ',r'DOGAO',r'Feijoada',r'PASTEL',r'Espeto',r'Bacio di',r'VIVENDA DO',r'FRANGO', r'Restaura', r'RSHOP-DOGAO DO', r'RSHOP-SANTA GULA', r'RSHOP-VIVENDA DO', r'RSHOP ESPETO', r'RESTAURANTE', r'PIZZARIA', r'RSHOP-ESPETO'],
        'SAQUE': [r'SAQUE', r'CXE'],
        'SEGURO':[r'PORTO',r'INT TED D',r'BOLETO PORTO S'],
        'SHOPPING': [r'RIACHUE',r'DAISO',r'LOJAS AMERI',r'BAHIA',r'CELLSHOP',r'SHOPPING',r'SP MARKET',r'LOJAS RENNE',r'RSHOP-RIACHUELO'],
        'TARIFA':[r'TARIFA TRAN',r'ITAU'],
        'TELEFONE': [
            r'INT PRE-PAGO',
            {'descricao': r'PAG BOLETO|MOBILEPAG|MOBILE PAG', 'valor_entre': [-280.00, -40.00]},
            r'VIVO',
            r'CLARO'            
        ],
        'TRANSFERENCIAS' :[r'TED D',r'TBI ',r' TRANSF '],
        'VIAGEN': [r'FAZENDA GRA',r'FOZ PLAZA',r'RSHOP PANORAMA ',r'NATURAL TRAV',r'AUTOZONE BRA',r'CATARA',r'ESPACO DAS A']
    }

# As descrições que você quer remover
descricoes_para_remover = [
        'SALDO DO DIA',
        'TED 237',
        'TED 999',
        'descricao_a_remover_2',
        'outra_descricao_qualquer'
    ]

# Os arquivos para extrair informações     # pdftotext.exe
file_paths = [
        '../../../../Doc/Docs/Extratos/extrato_072025_250921_091826.txt',  # 07/25 a 09/25
        '../../../../Doc/Docs/Extratos/extrato_072025_250905_170222.txt',  # 07/25 a 09/25
        '../../../../Doc/Docs/Extratos/extrato_062025_250815_123724.txt',  # 06/25 a 08/25
        '../../../../Doc/Docs/Extratos/extrato_052025_250811_181400.txt',  # 05/25 a 08/25
        '../../../../Doc/Docs/Extratos/extrato_072024_250326_201254.txt',  # 06/04 a 03/25
        '../../../../Doc/Docs/Extratos/extrato_012025_250530_222908.txt',  # 01/25 a 05/25
        '../../../../Doc/Docs/Extratos/extrato_012025_250811_181326.txt',  # 12/24 a 08/25
        '../../../../Doc/Docs/Extratos/extrato_xxxxx.txt',                 # 12/24 a 05/25
        '../../../../Doc/Docs/Extratos/extrato_112023.txt',                # 11/23 a 02/24 
        '../../../../Doc/Docs/Extratos/extrato_0112023_banco_extrato.txt', # 11/23 a 02/24        
        #'../../../../Doc/Docs/Extratos/extrato_2012_ContaCorrente2.txt'    # 10/12    
        #'../../../../Doc/Docs/Extratos/extrato_2012_ContaCorrente.txt',    # 09/12    
    ]