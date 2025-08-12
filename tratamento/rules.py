# rules.py
categorization_rules = {
        'MERCADO': [r'EXTRA HIPER',r'ATACADAO',r'MERCADINHO',r'PANIF',r'PADARIA',r'CARREFOUR', r'RSHOP BIG BOM', r'RSHOP MERCADO ', r'RSHOP MARCO', r'RSHOP MUFFATO', r'SUPERMERCADO', r'RSHOP-MERCADO'],
        'FARMACIA': [r'DROGA',r'FARMACIA', r'DROGARIA'],
        'SAQUE': [r'SAQUE', r'CXE'],
        'RESTAURANTE': [r'FRIENDS ',r'DOGAO',r'Feijoada',r'PASTEL',r'Espeto',r'Bacio di',r'VIVENDA DO',r'FRANGO', r'Restaura', r'RSHOP-DOGAO DO', r'RSHOP-SANTA GULA', r'RSHOP-VIVENDA DO', r'RSHOP ESPETO', r'RESTAURANTE', r'PIZZARIA', r'RSHOP-ESPETO'],
        'TELEFONE': [r'MOBILE PAG TIT BANC',r'TIM', r'VIVO', r'CLARO'],
        'INTERNET': [r'INTERNET', r'NET', r'CLARO'],
        'OUTROS': [r'EDUARDODIAS', r'MARIVANLIMA'],
        'GASOLINA': [r'AUTOSUL', r'RSHOP AUTO POSTO', r'RSHOP-AUTO POSTO'],
        'LUZ': [r'ELETROPAULO'],
        'GAS': [r' GAS ',r'INT COMGAS'],
        'ESTACIONAMENTO': ['PARK ',r'ESTAPAR',r'RSHOP-SP MARKET'],
        'IGREJA': [r'ADS',r'SOCIEDADE B', r'ADSA'],
        'HOTEL': [r'FOZ PLAZA',r'RSHOP PANORAMA '],
        'BANCO': [r'SEGURO CARTAO'],
        'SHOPPING': [r'CELLSHOP',r'SHOPPING',r'SP MARKET',r'LOJAS RENNE',r'RSHOP-RIACHUELO'],
        'HOTFRUIT': [r'FRUTAO',r'CHACARA DO',r'Hortifruti'],
        'AEROPORTO':[r'GRU '],
        'PAPELARIA': [r'LAN HOUSE',r'KALUNGA'],
        'ACOUGUE': [r'WEST BOI'],
        'TRANSFERENCIAS' :[r'TBI ',r' TRANSF '],
        'MECANICO' :[r'Mercadocar',r'PREMYER',r'CENTRO AUTO',r'CLIMATOA'],
        'TARIFA':[r'ITAU'],
        'CONDOMINIO': {'descricao': r'PAG BOLETO|MOBILEPAG','valor': -529.76 }
    }

# As descrições que você quer remover
descricoes_para_remover = [
        'SALDO DO DIA',
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