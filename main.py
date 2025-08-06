import json
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from buscar_normativos import buscar_normativos
from verificar_normativos_clientes import verificar_normativos_cliente
from exibir_relatorio import exibir_relatorio
from verificar_monitoramento import executar_verificacao_monitoramento
from analisar_associados import executar_analise_associados
from listar_regras_cliente import listar_regras_cliente
from obter_origens_cliente import obter_todas_origens

def json_converter(o):
    """Converte tipos não serializáveis para JSON."""
    if isinstance(o, ObjectId):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, set):
        return list(o)
    raise TypeError(f"Object of type {type(o)} is not JSON serializable")

def conectar_mongodb():
    username = "readOnlyProd"
    password = "by76HMOjhhf38Aiq"
    uri = f"mongodb+srv://{username}:{password}@lbprod-pri.cuho0.mongodb.net/?tls=true"
    try:
        client = MongoClient(uri)
        print("Conexão com o MongoDB realizada com sucesso!")
        return client
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        exit(1)

client = conectar_mongodb()
db = client['legalbot_platform']
coll_un = db['un']

def obter_cliente_id(cliente_id=None, cliente_nome=None):
    if cliente_id:
        try:
            cliente = coll_un.find_one({"_id": ObjectId(cliente_id)})
            return cliente["_id"] if cliente else None
        except Exception:
            return None
    elif cliente_nome:
        cliente = coll_un.find_one({"name": {"$regex": f"^{cliente_nome}$", "$options": "i"}})
        return cliente["_id"] if cliente else None
    return None

def executar_analise_por_origem(cliente_id_str, origin, data_inicial, data_final):
    """
    Executa o pipeline de análise para uma origem, operando de forma mais silenciosa.
    """
    print(f"Analisando origem: {origin}...")
    
    normativos = buscar_normativos(origin, data_inicial, data_final)
    if not normativos:
        return {"origem": origin, "status": "sem_normativos"}

    clientes_dict, documentos_faltantes = verificar_normativos_cliente(normativos, cliente_id=cliente_id_str)

    # Análise de faltantes (retorna o relatório em vez de salvar)
    relatorio_faltantes = executar_verificacao_monitoramento(cliente_id_str, origin, data_inicial, data_final, documentos_faltantes, salvar_relatorio=False)
    
    # Análise de associados (retorna o relatório em vez de salvar)
    relatorio_associados = None
    for dados_cliente in clientes_dict.values():
        documentos_associados_ids = dados_cliente.get("documentos_ids")
        if documentos_associados_ids:
            relatorio_associados = executar_analise_associados(list(documentos_associados_ids), cliente_id_str, salvar_relatorio=False, salvar_debug=False)

    # Pega os dados do cliente apenas se o dicionário não estiver vazio
    dados_cliente = next(iter(clientes_dict.values()), {}) if clientes_dict else {}

    return {
        "origem": origin,
        "status": "analise_concluida",
        "contagem_status": dados_cliente,
        "analise_documentos_associados": relatorio_associados,
        "analise_documentos_faltantes": relatorio_faltantes
    }

if __name__ == "__main__":
    escolha_cliente = input("Você quer informar o ID ou o Nome do cliente? (Digite 'ID' ou 'Nome'): ").strip().lower()
    cliente_id_input = None
    cliente_nome_input = None
    if escolha_cliente == 'id':
        cliente_id_input = input("Informe o ID do cliente: ").strip()
    elif escolha_cliente == 'nome':
        cliente_nome_input = input("Informe o Nome do cliente: ").strip()
    else:
        print("Entrada inválida.")
        exit(1)

    cliente_id_obj = obter_cliente_id(cliente_id=cliente_id_input, cliente_nome=cliente_nome_input)
    if not cliente_id_obj:
        print("Cliente não encontrado.")
        exit(1)
    cliente_id_str = str(cliente_id_obj)

    listar_regras_cliente(cliente_id_str)

    lista_de_origens = []
    escolha_origem = input("Deseja informar uma origem específica? (s/n): ").strip().lower()
    if escolha_origem == 's':
        origem_especifica = input("Informe a origem do normativo (ex: Receita Federal/DOU): ")
        lista_de_origens.append(origem_especifica)
    elif escolha_origem == 'n':
        print("Buscando todas as origens associadas ao cliente...")
        lista_de_origens = obter_todas_origens(cliente_id_str)
        print(f"Encontradas {len(lista_de_origens)} origens. Iniciando análise para cada uma.")
    else:
        print("Entrada inválida.")
        exit(1)

    data_inicial_str = input("Informe a data inicial (formato DD/MM/YYYY): ")
    data_final_str = input("Informe a data final (formato DD/MM/YYYY): ")
    try:
        data_inicial = datetime.strptime(data_inicial_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        data_final = datetime.strptime(data_final_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print("Formato de data inválido.")
        exit(1)

    relatorio_final_agregado = []
    for origem in lista_de_origens:
        resultado_origem = executar_analise_por_origem(cliente_id_str, origem, data_inicial, data_final)
        relatorio_final_agregado.append(resultado_origem)

    if relatorio_final_agregado:
        nome_arquivo_final = f"relatorio_completo_{cliente_id_str}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(nome_arquivo_final, "w", encoding='utf-8') as f:
            json.dump(relatorio_final_agregado, f, indent=4, ensure_ascii=False, default=json_converter)
        print(f"\nAnálise completa para todas as origens concluída.")
        print(f"Relatório final agregado salvo em: {nome_arquivo_final}")
    else:
        print("\nNenhuma análise foi executada ou nenhum resultado foi gerado.")
