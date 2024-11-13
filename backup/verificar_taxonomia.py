from config import coll_norm, coll_routing_rule
from bson import ObjectId

def verificar_taxonomia(normativo_id):
    """
    Verifica se um normativo está associado a uma taxonomia ativa e quais são as tags que correspondem.
    Retorna informações detalhadas da taxonomia, incluindo tags correspondentes e não correspondentes.
    """
    # Consultar o normativo pelo ID
    normativo = coll_norm.find_one({"_id": ObjectId(normativo_id)})
    if not normativo:
        return None  # Retorna None se o normativo não for encontrado
    
    # Obter a origem e as tags do normativo
    origem = normativo.get("origin")
    tags_normativo = normativo.get("tags", [])
    theme_normativo = normativo.get("theme", "")

    # Consultar regras de roteamento ativas na coleção `routing_rule` baseadas na origem
    routing_rules = coll_routing_rule.find({"query.origins": origem, "deleted_by": None})
    
    # Lista para armazenar informações de taxonomia e clientes associados
    taxonomias_associadas = []
    possui_taxonomia = False  # Flag para verificar se há alguma taxonomia associada

    # Verificar associação com a taxonomia e clientes associados
    for rule in routing_rules:
        rule_ptags = rule.get("query", {}).get("ptags", [])
        rule_ntags = rule.get("query", {}).get("ntags", [])
        rule_themes = rule.get("query", {}).get("themes", [])

        # Verificar tags positivas e negativas
        associated_ptags = [tag for tag in rule_ptags if tag in tags_normativo]
        associated_ntags = [tag for tag in rule_ntags if tag in tags_normativo]
        theme_match = theme_normativo not in rule_themes if rule_themes else True

        # Verificar se o normativo tem um match válido (sem tags negativas e com match de tema)
        if associated_ptags and not associated_ntags and theme_match:
            possui_taxonomia = True
            for assoc_un in rule.get("un_ids", []):
                cliente_id = assoc_un.get("un_id")
                if cliente_id:
                    taxonomias_associadas.append({
                        "cliente_id": str(cliente_id),
                        "taxonomia": rule.get("title"),
                        "descricao": rule.get("subject"),
                        "tags_correspondentes": associated_ptags,
                        "tags_excluidas": associated_ntags,
                        "associado_ao_cliente": True
                    })

    # Retornar a lista completa de taxonomias e clientes associados ou indicar falta de taxonomia
    return taxonomias_associadas if taxonomias_associadas else [{"taxonomia": "Nenhuma", "descricao": "Sem taxonomia associada", "associado_ao_cliente": False}]
