# rules.py
# rules.py
categorization_rules = {
    'ACOUGUE': [r'CASA DE CAr', r'WEST BOI', r'RSHOP MARWAL', r'MARWAL'],
    'AEROPORTO': [r'GRU ', r'RSHOP GRU TPS'],
    'BANCO': [r'RSHOP PISTA', r'SEGURO CARTAO', r'TAR PACOTE ITAU', r'TARIFA', r'ITAU', r'PINBANK'],
    'BELEZA': [r'ANGELA PE', r'TAIYANG', r'CORTEFINO', r'DEBORARODRI', r'DEBORAr', r'JOYC2208'],
    'COSTURA': [r'BORDAD', r'YOKO', r'TIAGO MAQUI', r'FIVELAS', r'TECIDOS', r'JJS', r'BL PLAST'], 
    'CONDOMINIO': [
        # 1. Regra existente (para descrições que contêm o nome do condomínio)
        {'descricao': r'CONJUNTO RESIDENCIAL|RESIDENCIAL|CONDOMINIO', 'valor_entre': [-650.00, -350.00]},        
        # 2. Nova regra para os boletos do Bradesco (Banco 237) na faixa de valor do condomínio
        {'descricao': r'MOBILE PAG TIT BANCO 237|MOBILEPAG TIT BANCO 237', 'valor_entre': [-600.00, -370.00]},        
        # 3. Nova regra para os boletos com o código final "6079" que se repete nos pagamentos de -529,76
        {'descricao': r'PAG TIT 6079|TIT 6079933340', 'valor_entre': [-550.00, -500.00]},
    ],
    'DENTISTA': [r'DENTISTA', r'PERSIO', r'PERCIO'],
    'ESTACIONAMENTO': [r'ESTACION', r'ESTAC ', r'PARK ', r'ESTAPAr', r'SP MARKET E', r'RODOANEL PED', r'ESTAC SHOP'],
    'FARMACIA': [r'GOYA PERFU', r'USEMAISFARM', r'DROGA', r'FARMACIA', r'DROGARIA', r'FARMA', r'MASTER FARMA'],
    'GAS': [r' GAS ', r'INT COMGAS', r'COMGAS', r'ZP GASSI'],
    'GASOLINA': [r'N S FATIMA', r'AURUM', r'PETROL ', r'AUTOSUL', r'AUTO POSTO', r'POTENCIAL TE', r'P STATION', r'AV JOAO DIAS'],
    'HORTIFRUIT': [r'FRUTAO', r'CHACARA DO', r'HORTIFRUTI', r'HORTIFRU', r'GRAO DA FAM', r'ORVALHO COM', r'ARMAZEMFLOr', r'HORTIFr'], 
    'IGREJA': [r'CONADIBE', r'ADS', r'SOCIEDADE B', r'ADSA', r'ADSABRASIL'],
    'IMPRESSORA': [r'PONTODOSCAr', r'PRODATA', r'ATMK COM DE'],
    'INTERNET': [r'INTERNET', r'NET', r'CLARO'],
    'LUZ': [r'ELETROPAULO', r'ENEL'],
    'MECANICO': [r' AUTOPE', r'MERCADOCAr', r'PREMYEr', r'CENTRO AUTO', r'CLIMATOA', r'ESCALADA AU', r'MALURE AUTO', r'AUTOZONE', r'FUJIHEI', r'PALUDETO'], 
    'MERCADO': [
        r'OXXO', r'PAO DE AC', r'MINIMERCADO', r'SUPERM', r'MERCEARIA', r'CHOCOLANDIA', r'EXTRA HIPEr', r'ATACAD[AÃ]O', 
        r'MERCADINHO', r'PANIF', r'PADARIA', r'CARREFOUr', r'BIG BOM', r'MERCADO ', r'MARCO', r'MUFFATO', r'GIGA ATACADO', 
        r'DG ALIMENTOS', r'ALEMAO HIGI', r'VPMS', r'SUP CERCADAO', r'NOVA BANDEIr', r'SOL E NEVE', r'FRUTAO', r'EMPORIUM ME', r'PRECO JUSTO'
    ],
    'MATERIAL': [r'MARIKA', r'TINTAS', r'ARAUJO MATEr', r'LOJA ELET', r'APOIO TINTAS', r'R PIRES SACO', r'OKINALAr'],
    'OUTROS': [
        r'EDUARDODIAS', r'EDUARDO', r'MARIVAN', r'MARIVAM', r'KEVERSON', r'LUCASDASILVA', r'RODRIGODEJES', r'SANDRAREGINA', 
        r'ANDREROBERT', r'DORIVALDO', r'DORIVALD', r'JOSE ROGERIO', r'MARCELO MAGE', r'MARCELO MAG', r'COREMAS', r'MARIA JOSE', r'MARIA IMACUL',
        r'PEDRO GUSTAV', r'CAPPTA CORA', r'ETHERIC LIGH', r'DJANIRALEIT', r'VANDERLEI P', r'WILLIAN JOA', r'FRENANDO PA', 
        r'VINICIUSOLIV', r'JOZENIBEZER', r'ORLANDOREIS', r'LEANDROSOUZA', r'PAULODEOLIVE', r'S E SOARES', r'JOSAFAF', r'MARIADE',
        r'SUELLEN ARMA', r'FUNDACAO Ar', r'PG TON', r'GETULIO', r'MERCADOPAGO', r'62 372', r'46 629'  # Adicionados novos padrões de CNPJ e termos corretos
    ],
    'PAPELARIA': [r'LAN HOUSE', r'KALUNGA'],
    'PREFEITURA': [r'PM SAO', r'INT PM SAO PAU', r'INT LICENC SP', r'INT MULTA ', r'IPTU', r'IPVA', r'LICENCIAMENTO', r'BARUERI', r'LICENC', r'MULTA'],        
    'RESTAURANTE': [
        r'FRIENDS', r'BACON', r'CHURRAS', r'BURGEr', r'ESFIHA', r'DOGDODIE', r'JIN JIN', r'MP CALDODE', r'MEI MEI', r'EXPRESS GRI', 
        r'CAFETERIA', r'CAFE ', r'MANIA DE CHU', r'SABORINI', r'EMPORIO', r'PONTO SP MA', r'DONALD', r'THE STEAK', r'CHURRASCARI', 
        r'AQUARELA', r'DOGAO', r'FEIJOADA', r'PASTEL', r'ESPETO', r'BACIO DI', r'VIVENDA DO', r'FRANGO', r'RESTAURA', r'SANTA GULA', 
        r'PIZZARIA', r'HANNOVEr', r'MAGA RESTAUr', r'FATTORIA', r'SAN PIETRO', r'DONA MARIA', r'COMERCIAL VI', r'FRIED CHICKE', 
        r'MP JOILTON', r'SAMPA SUSHI', r'PAG FRIENDS', r'VARANDAS', r'JIM COM', r'SANCREAM', r'PONTO SANTA', r'REAL SUL', r'SALDANHA',
        r'MP ALE', r'PRA LA DE BO', r'NIPPON', r'ASSB COMERC', r'SPAD' # Adicionado SPAD restaurante
    ],
    'SAQUE': [r'SAQUE', r'CXE'],
    'SEGURO': [r'PORTO', r'INT TED D', r'BOLETO PORTO S'],
    'SHOPPING': [
        r'RIACHUE', r'DAISO', r'LOJAS AMERI', r'BAHIA', r'CELLSHOP', r'SHOPPING', r'SP MARKET', r'LOJAS RENNE', r'CEA ', r'RENNEr', 
        r'MULTIPLAN', r'OPCAO CENTEr', r'VIVA MORUMBI', r'VIVA MORUMB', r'7015 MORUMB', r'1950 SHOPPIN', r'PORTAL VL DA', r'ANAVITORIAS', r'PARK PLACE',
        r'DMW COMERCIO', r'JARDIM DAS', r'AUTTAR LOJA', r'GSMMYCOMERC', r'MAG 1 CENTr', r'SERRANA', r'UNISO IBIRA', r'PONTO CERTO',
        r'SANTO AMARO', r'SP MAR' # Adicionados Santo Amaro e SP Mar
    ],
    'TELEFONE': [
        r'MOBILE PAG TIT BANCO 422',
        r'MOBILEPAG TIT BANCO 422',
        r'INT PRE-PAGO',
        r'INT PRE PAGO',
        # Corrigido chave 'descricao' para minúscula
        {'descricao': r'PAG BOLETO|MOBILEPAG|MOBILE PAG|PAG TIT', 'valor_entre': [-170.00, -30.00]},
        r'VIVO',
        r'CLARO'            
    ],
    'TRANSFERENCIAS': [
        r'TED D', r'TBI ', r' TRANSF ', r'PIX ', r'SALDO DO DIA', r'TED 237', r'TED 999' # Adicionados informativos de entrada de dinheiro
    ],
    'VIAGEM': [r'FAZENDA GRA', r'FOZ PLAZA', r'PANORAMA', r'NATURAL TRAV', r'CATARA', r'ESPACO DAS A', r'FOZ ', r'URBIA', r'GRANDE HOTEL', r'FEL EMPREEND']
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
        '../../../../Doc/Docs/Extratos/extrato_052026_260716_102322.txt',  # 06/26 a 07/26
        '../../../../Doc/Docs/Extratos/extrato_042026_260602_181120.txt',  # 04/26 a 06/26
        '../../../../Doc/Docs/Extratos/extrato_032026_260505_124517.txt',  # 03/26 a 05/26
        '../../../../Doc/Docs/Extratos/extrato_012026_260313_202844.txt',  # 02/26 a 03/26
        '../../../../Doc/Docs/Extratos/extrato_122025_260202_174922.txt',  # 01/26 a 02/26
        '../../../../Doc/Docs/Extratos/extrato_122025_251231_134915.txt',  # 10/25 a 12/25
        '../../../../Doc/Docs/Extratos/extrato_102025_251212_082340.txt',  # 10/25 a 12/25
        '../../../../Doc/Docs/Extratos/extrato_092025_251103_165930.txt',  # 09/25 a 10/25
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