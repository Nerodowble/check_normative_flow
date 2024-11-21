import os
import json
from bson import ObjectId
import pymongo
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

CACHE_FILE = "cache.json"

# Mapeamento de produtos com suas descrições
PRODUCTS_DESCRIPTIONS = {
    "meta.platform.legalbot.com.br": "Base do Sistema",
    "flow.platform.legalbot.com.br": "Produto Flow",
    "search.platform.legalbot.com.br": "Produto Busca",
    "new_search.platform.legalbot.com.br": "Produto Busca Semântica",
    "flow_internal.platform.legalbot.com.br": "Produto Normativos Interno - Flow Internal",
    "export_archer.platform.legalbot.com.br": "Produto Exportar Archer - Archer",
    "radar.platform.legalbot.com.br": "Produto Radar",
    "action_by_role.platform.legalbot.com.br": "Função por Papel",
    "display_risk.platform.legalbot.com.br": "Disponibiliza o Risco na Caixa de Entrada (BNDES)",
    "llm_gpt.platform.legalbot.com.br": "Produto LLM - AI Generativa",
    "ib_sistem.platform.legalbot.com.br": "Vínculo do Sistema IB - BV",
    "paralegal.platform.legalbot.com.br": "Produto Paralegal - AirTable",
    "taxonomy_recommendations.platform.legalbot.com.br": "Produto Taxonomia - Workflow",
    "taxonomy.platform.legalbot.com.br": "Produto Taxonomia - Auto-Serviço",
    "data_quality_monitor.platform.legalbot.com.br": "Produto DataQuality - Monitor de Origens"
}

def carregar_cache():
    """Carrega os dados do cache do arquivo JSON."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_cache(cache):
    """Salva os dados no cache para o arquivo JSON."""
    with open(CACHE_FILE, "w") as f:
        json.dump(serialize_object_ids(cache), f, indent=4)

def serialize_object_ids(data):
    """Converte todos os ObjectIds em strings dentro de uma estrutura de dados."""
    if isinstance(data, dict):
        return {key: serialize_object_ids(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_object_ids(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

def obter_un(cliente_id):
    """Obtém os dados da UN (cliente) com base no ID fornecido."""
    return db.un.find_one({"_id": ObjectId(cliente_id)})

def obter_nome_origens(origens_ids):
    """Obtém os nomes das origens a partir de seus IDs."""
    origens_detalhadas = []
    for origem_id in origens_ids:
        origem_data = db.origins.find_one({"_id": ObjectId(origem_id)})
        if origem_data:
            origens_detalhadas.append({
                "id": str(origem_id),
                "nome": origem_data.get("sid", "Nome Desconhecido")
            })
        else:
            origens_detalhadas.append({
                "id": str(origem_id),
                "nome": "Origem não encontrada"
            })
    return origens_detalhadas

def verificar_origens_configuradas(cliente_id):
    """Verifica se há origens configuradas diretamente no cliente na collection un_config."""
    config = db.un_config.find_one({"un_id": ObjectId(cliente_id)})
    origens_ids = config.get("acquired_origins", []) if config else []
    origens_detalhadas = obter_nome_origens(origens_ids)
    return origens_detalhadas

def calcular_normativos(cliente_id, meses):
    """Calcula a quantidade de normativos nos últimos `meses` e retorna o total e por base."""
    data_limite = datetime.now(timezone.utc) - timedelta(days=30 * meses)
    pipeline = [
        {"$match": {"un_root": ObjectId(cliente_id), "created_at": {"$gte": data_limite}}},
        {"$group": {"_id": "$norm_infos.origin", "count": {"$sum": 1}}}
    ]
    resultados = list(db.normative_un.aggregate(pipeline))

    total_normativos = sum(item["count"] for item in resultados)
    normativos_por_base = {item["_id"]: item["count"] for item in resultados}
    return total_normativos, normativos_por_base

def gerar_relatorio(cliente_id):
    """Gera o relatório de produtos associados ao cliente e normativos."""
    # Carregar cache
    cache = carregar_cache()
    if cliente_id in cache:
        cache_data = cache[cliente_id]
        last_updated = datetime.fromisoformat(cache_data["last_updated"])
        if (datetime.now(timezone.utc) - last_updated).total_seconds() < 86400:  # Cache válido por 24 horas
            print("\n===== Dados do Cache =====")
            print(json.dumps(cache_data, indent=4))
            print("\n===== Fim dos Dados do Cache =====")
            return

    cliente_data = obter_un(cliente_id)
    if not cliente_data:
        print(f"Cliente com ID {cliente_id} não encontrado.")
        return

    origens_configuradas = verificar_origens_configuradas(cliente_id)

    relatorio = {
        "nome_cliente": cliente_data.get("name", "Desconhecido"),
        "status": "Ativo" if cliente_data.get("status", 0) == 1 else "Inativo",
        "root": "Sim" if cliente_data.get("root", False) else "Não",
        "produtos": cliente_data.get("products", []),
        "origens_configuradas": [
            f"ID: {origem['id']} - Nome: {origem['nome']}" for origem in origens_configuradas
        ],
        "contabilidade_normativos": {}
    }

    for meses in [12, 6, 3]:
        total, por_base = calcular_normativos(cliente_id, meses)
        relatorio["contabilidade_normativos"][f"{meses}_meses"] = {
            "total": total,
            "por_base": por_base
        }

    # Serializar dados antes de salvar no cache
    relatorio_serialized = serialize_object_ids(relatorio)

    # Salvar no cache
    cache[cliente_id] = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "data": relatorio_serialized
    }
    salvar_cache(cache)

    print("\n===== Relatório do Cliente =====")
    print(json.dumps(relatorio_serialized, indent=4))
    print("\n===== Fim do Relatório =====")

# Entrada do cliente para gerar o relatório
if __name__ == "__main__":
    cliente_id = input("Informe o ID do cliente: ").strip()
    gerar_relatorio(cliente_id)

#Ele tem as origens especificada para ele (no caso SF3 0)
#Mas ele não esta informando as origens ASSOCIADAS, via RADAR por exemplo.
#Tambem não está informando as ÁREAS, que constam na collection 'un'.