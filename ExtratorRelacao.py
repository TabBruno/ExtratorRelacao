import os
from os import chdir, getcwd, listdir
import json
import pandas as pd
from collections import defaultdict

diretoriopadrao = os.getcwd() 
#verifica se path exites
if not os.path.exists(diretoriopadrao + "\\resultado\\"):
    os.mkdir (diretoriopadrao + "\\resultado\\")

if not os.path.exists(diretoriopadrao + "\\lidos\\"):
    os.mkdir (diretoriopadrao + "\\lidos\\")

def mostrar_menu():
    print("\nMenu de Opções:")
    print("1 - Capturar Relações")
    print("2 - Sair")

def listararquivos():
    #lista arquivos existente na pasta de execucao
    extensao = '.json'
    
    arquivos = os.listdir(diretoriopadrao)
    arquivos_filtrados = [arquivo for arquivo in arquivos if arquivo.endswith(extensao)]

    return (arquivos_filtrados)

def executa():
    #verifica arquivos da pasta
    for json_file in listararquivos():
        
        #monta caminho completo para leitura
        caminhoArq = diretoriopadrao + "\\" + json_file
        
        #abre arquivo para leitura
        with open(caminhoArq) as arquivo:
            data = json.load(arquivo)
        
        #valida tipo de arquivo (borda, bt, interop)
        if "contracts" in data or "Contracts" in data:
            result = borda(caminhoArq)
            salvaArquivo(result, json_file, "BORDA - ")
        elif "idContratoExterno" in data or "idcontratoexterno" in data:
            result = interop(caminhoArq)
            salvaArquivo(result, json_file, "INTEROP - ")
        elif "key" in data[0] or "Key" in data[0]:
            result = bt(caminhoArq)
            salvaArquivo(result, json_file, "BT - ")
            
        else:
            print("Arquivo inválido - " + json_file)
        
        #move arquivos
        if os.path.exists(diretoriopadrao + "\\Lidos\\" + json_file):
            os.remove(diretoriopadrao + "\\Lidos\\" + json_file)
        os.rename(caminhoArq, diretoriopadrao + "\\Lidos\\" + json_file)

def salvaArquivo(result, json_file, tipo):
        
    nomedoarquivo = diretoriopadrao + "\\resultado\\" + tipo + json_file
    
    #gera arquivo resultado
    with open(nomedoarquivo, "w") as arquivo:
        print(json.dumps(result, indent=4), file=arquivo)

    #mensagem para checar arquivo de saida
    print("Valide arquivo de saida: " + nomedoarquivo )

def borda(caminho):
    
    #abre arquivo para leitura
    with open(caminho) as arquivo:
        data = json.load(arquivo)

    #fomata para ignorar case sensitive
    data = {k.lower(): v for k, v in data.items()}
    
    records = []
            
    for contract in data['contracts']:
        #fomata para ignorar case sensitive
        contract = {k.lower(): v for k, v in contract.items()}
                
        for spec in contract['contractspecifications']:
            #fomata para ignorar case sensitive
            spec = {k.lower(): v for k, v in spec.items()}

            original_asset_holder = spec.get('originalassetholder', spec.get('assetholder', '')).lower()

            records.append({
                'originalAssetHolder': original_asset_holder,
                'receivableDebtor': spec['receivabledebtor'],
                'paymentScheme': spec['paymentscheme']
            })
    
    df = pd.DataFrame(records)
    
    # Agrupar por originalAssetHolder e receivableDebtor concatenando paymentScheme
    grouped = df.groupby(['originalAssetHolder', 'receivableDebtor'])['paymentScheme'].apply(lambda x: ', '.join(x)).reset_index().sort_values(by='paymentScheme')
    
    #retorna resultado
    return grouped.to_dict(orient='records')

def bt(caminho):
    
    #abre arquivo para leitura
    with open(caminho) as arquivo:
        data = json.load(arquivo)
    
    # Extrair as especificações do contrato para um DataFrame do pandas
    specs = []
    for item in data:
        for effect in item["effects"]:
            for spec in effect["contractSpecifications"]:
                specs.append({
                    "originalAssetHolder": spec["originalAssetHolder"],
                    "receivableDebtor": spec["receivableDebtor"],
                    "paymentScheme": spec["paymentScheme"]
                })

    df = pd.DataFrame(specs)

    # Agrupar por originalAssetHolder e receivableDebtor concatenando paymentScheme
    grouped = df.groupby(['originalAssetHolder', 'receivableDebtor'])['paymentScheme'].apply(lambda x: ', '.join(x.unique())).reset_index().sort_values(by='paymentScheme')

    #retorna resultado
    return grouped.to_dict(orient='records')

def interop(caminho):
    
    #abre arquivo para leitura
    with open(caminho) as arquivo:
        data = json.load(arquivo)
    
    records = []
    
    for contract in data['grupoEfeitos']:
        records.append({
            'cpfCnpjOriginador': contract['cpfCnpjOriginador'],
            'cnpjCredenciadora': contract['cnpjCredenciadora'],
            'arranjo': contract['arranjo']
        })
    
    df = pd.DataFrame(records)
    
    # Agrupar por originalAssetHolder e receivableDebtor concatenando paymentScheme
    grouped = df.groupby(['cpfCnpjOriginador', 'cnpjCredenciadora'])['arranjo'].apply(lambda x: ', '.join(x)).reset_index().sort_values(by='arranjo')
    
    #retorna resultado
    return grouped.to_dict(orient='records')


while True:
    mostrar_menu()
    escolha = input("Escolha uma opção: ")
    
    clear = lambda: os.system('cls')
    
    if escolha == '2':
        print("Saindo do programa...")
        break
    if escolha == '1':
        clear()
        executa()
    else:
        clear()
        print("Opção inválida. Tente novamente.")