from bson import ObjectId
from config import coll_norm, coll_routing_rule

def analisar_associacao_por_taxonomia(documento_id, cliente_id):
    """
    Analisa se um documento foi associado a um cliente via mecanismo de Taxonomia e Roteamento.
    Esta função segue o procedimento descrito na documentação técnica do Sirius.

    Args:
        documento_id (str): O ID do normativo a ser verificado.
        cliente_id (str): O ID do cliente para o qual a associação está sendo verificada.

    Returns:
        dict: Um dicionário contendo o resultado da análise.
    """
    # Passo 1: Obter os dados de classificação e origem do normativo
    documento = coll_norm.find_one({"_id": ObjectId(documento_id)})
    if not documento:
        return {"tipo": "Erro", "detalhes": f"Documento com ID {documento_id} não encontrado na coleção 'norm'."}

    doc_class = documento.get("class")
    doc_subclass = documento.get("subclass")
    doc_source = documento.get("origin") # Corrigido de 'source' para 'origin' para corresponder ao nosso schema

    if not all([doc_class, doc_subclass, doc_source]):
        return {
            "tipo": "Taxonomia/Roteamento (Dados Insuficientes)",
            "detalhes": "O documento não possui os campos 'class', 'subclass' ou 'origin' necessários para a análise de roteamento."
        }

    # Passo 2: Encontrar a Regra de Roteamento (O Elo de Ligação)
    # Constrói a consulta complexa para encontrar a regra correspondente.
    query = {
        "company_id": ObjectId(cliente_id),
        "source_ids": doc_source,
        "$and": [
            {"rules": {"$elemMatch": {"key": "class", "values": doc_class}}},
            {"rules": {"$elemMatch": {"key": "subclass", "values": doc_subclass}}}
        ]
    }

    regra_encontrada = coll_routing_rule.find_one(query)

    # Passo 3: Analisar o Resultado da Consulta
    if regra_encontrada:
        # Cenário de Sucesso: Regra Encontrada
        return {
            "tipo": "Taxonomia/Roteamento",
            "id_regra": str(regra_encontrada["_id"]),
            "nome_taxonomia": regra_encontrada.get("taxonomy_name", "Taxonomia sem nome"),
            "detalhes_match": {
                "classe_documento": doc_class,
                "subclasse_documento": doc_subclass,
                "origem_documento": doc_source,
                "regra_roteamento_acionada": {
                    "key_class": doc_class,
                    "key_subclass": doc_subclass
                }
            }
        }
    else:
        # Cenário de Falha: Nenhuma Regra Encontrada
        return {
            "tipo": "Taxonomia/Roteamento (Falhou)",
            "detalhes": "O documento foi classificado, mas nenhuma regra de roteamento ativa para este cliente correspondeu à combinação de classe, subclasse e origem.",
            "criterios_buscados": {
                "cliente_id": cliente_id,
                "origem": doc_source,
                "classe": doc_class,
                "subclasse": doc_subclass
            }
        }