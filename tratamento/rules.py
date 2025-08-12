# rules.py
categorization_rules = {
        'ACOUGUE': [r'CASA DE CAR',r'WEST BOI'],
        'AEROPORTO':[r'GRU '],
        'BANCO': [r'SEGURO CARTAO'],
        'BELEZA' :[r'TAIYANG'],
        'CONDOMINIO': [
            {'descricao': r'PAG BOLETO|MOBILEPAG', 'valor': -529.76},
            {'descricao': r'MOBILEPAG', 'valor': -383.02},
            r'CONJUNTO RESIDENCIAL'
        ],
        'ESTACIONAMENTO': [r'ESTAC ',r'PARK ',r'ESTAPAR',r'RSHOP-SP MARKET'],
        'FARMACIA': [r'DROGA',r'FARMACIA', r'DROGARIA'],
        'GAS': [r' GAS ',r'INT COMGAS'],
        'GASOLINA': [r'AUTOSUL', r'RSHOP AUTO POSTO', r'RSHOP-AUTO POSTO'],
        'HOTEL': [r'FOZ PLAZA',r'RSHOP PANORAMA '],
        'HOTFRUIT': [r'FRUTAO',r'CHACARA DO',r'Hortifruti'],
        'IGREJA': [r'ADS',r'SOCIEDADE B', r'ADSA'],
        'IMPRESORA':[r'PONTODOSCAR'],
        'INTERNET': [r'INTERNET', r'NET', r'CLARO'],
        'LUZ': [r'ELETROPAULO'],
        'MECANICO' :[r'Mercadocar',r'PREMYER',r'CENTRO AUTO',r'CLIMATOA'],
        'MERCADO': [r'EXTRA HIPER',r'ATACADAO',r'MERCADINHO',r'PANIF',r'PADARIA',r'CARREFOUR', r'RSHOP BIG BOM', r'RSHOP MERCADO ', r'RSHOP MARCO', r'RSHOP MUFFATO', r'SUPERMERCADO', r'RSHOP-MERCADO'],
        'OUTROS': [r'EDUARDODIAS', r'MARIVANLIMA'],
        'PAPELARIA': [r'LAN HOUSE',r'KALUNGA'],
        'PREFEITURA':[r'INT PM SAO PAU',r'INT LICENC SP',r'INT MULTA '],        
        'RESTAURANTE': ['AQUARELA ',r'FRIENDS ',r'DOGAO',r'Feijoada',r'PASTEL',r'Espeto',r'Bacio di',r'VIVENDA DO',r'FRANGO', r'Restaura', r'RSHOP-DOGAO DO', r'RSHOP-SANTA GULA', r'RSHOP-VIVENDA DO', r'RSHOP ESPETO', r'RESTAURANTE', r'PIZZARIA', r'RSHOP-ESPETO'],
        'SAQUE': [r'SAQUE', r'CXE'],
        'SEGURO':[r'BOLETO PORTO S'],
        'SHOPPING': [r'CELLSHOP',r'SHOPPING',r'SP MARKET',r'LOJAS RENNE',r'RSHOP-RIACHUELO'],
        'TARIFA':[r'TARIFA TRAN',r'ITAU'],
        'TELEFONE': [
            r'INT PRE-PAGO',
            r'VIVO',
            r'CLARO',
            {'descricao': r'PAG BOLETO', 'valor': -61.93},
            r'MOBILEPAG',
            r'MOBILE PAG'
        ],
        'TRANSFERENCIAS' :[r'TED D',r'TBI ',r' TRANSF ']        
    }

# As descrições que você quer remover
descricoes_para_remover = [
        'SALDO DO DIA',
        'TED ',
        'descricao_a_remover_2',
        'outra_descricao_qualquer'
    ]

# Os arquivos para extrair informações
file_paths = [
        '../../../../Doc/Docs/Extratos/extrato_012025_250811_181326.txt',
        '../../../../Doc/Docs/Extratos/extrato_072024_250326_201254.txt',
        '../../../../Doc/Docs/Extratos/extrato_052025_250811_181400.txt',
        '../../../../Doc/Docs/Extratos/extrato_112023.txt',
        '../../../../Doc/Docs/Extratos/banco_extrato.txt',
        '../../../../Doc/Docs/Extratos/extrato_012025_250530_222908.txt'
    ]