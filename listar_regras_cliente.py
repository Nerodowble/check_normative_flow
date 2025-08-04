import json
from bson import ObjectId
from datetime import datetime
from config import coll_monitor, coll_routing_rule

def json_converter(o):
    """Função auxiliar para converter tipos não serializáveis para JSON."""
    if isinstance(o, ObjectId):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

def listar_regras_cliente(cliente_id):
    """
    Busca todas as regras de Monitoramento e Taxonomia/Roteamento ativas
    para um cliente específico e as salva em um arquivo JSON.
    """
    print("\n" + "="*50)
    print(f"Buscando regras ativas para o cliente ID: {cliente_id}")
    print("="*50)

    relatorio_regras = {
        "cliente_id": cliente_id,
        "data_extracao": datetime.now().isoformat(),
        "regras_monitoramento": [],
        "regras_taxonomia_roteamento": []
    }

    # 1. Coletar Regras de Monitoramento
    monitores = list(coll_monitor.find({"un_root": ObjectId(cliente_id), "status": 1}))
    for monitor in monitores:
        filtros_formatados = []
        for filtro in monitor.get('filters', []):
            filtros_formatados.append({
                "tags_positivas": [tag for grupo in filtro.get("tag_positive", []) for tag in grupo.get("value", [])],
                "tags_negativas": [tag for grupo in filtro.get("tag_negative", []) for tag in grupo.get("value", [])]
            })
        
        relatorio_regras["regras_monitoramento"].append({
            "id": str(monitor['_id']),
            "nome": monitor.get('name', 'Sem nome'),
            "filtros": filtros_formatados
        })

    # 2. Coletar Regras de Taxonomia/Roteamento
    regras_roteamento = list(coll_routing_rule.find({
        "$or": [
            {"company_id": ObjectId(cliente_id)},
            {"un_ids.un_id": ObjectId(cliente_id)}
        ],
        "deleted_by": None
    }))

    for regra in regras_roteamento:
        query = regra.get('query', {})
        relatorio_regras["regras_taxonomia_roteamento"].append({
            "id": str(regra['_id']),
            "titulo": regra.get('title', 'Sem título'),
            "assunto": regra.get('subject', 'Sem assunto'),
            "criterios": {
                "origens": query.get('origins', []),
                "tags_positivas_ptags": query.get('ptags', []),
                "tags_negativas_ntags": query.get('ntags', []),
                "themes": query.get('themes', [])
            }
        })

    # 3. Salvar em arquivo JSON e exibir resumo no console
    nome_arquivo = f"regras_cliente_{cliente_id}.json"
    with open(nome_arquivo, "w", encoding='utf-8') as f:
        json.dump(relatorio_regras, f, indent=4, ensure_ascii=False, default=json_converter)

    print(f"Encontrados {len(relatorio_regras['regras_monitoramento'])} monitores ativos.")
    print(f"Encontradas {len(relatorio_regras['regras_taxonomia_roteamento'])} regras de roteamento ativas.")
    print(f"Relatório completo de regras salvo em: {nome_arquivo}")
    print("="*50)

if __name__ == '__main__':
    # Para teste direto do script
    test_cliente_id = input("Informe o ID do cliente para listar as regras: ").strip()
    if test_cliente_id:
        listar_regras_cliente(test_cliente_id)
