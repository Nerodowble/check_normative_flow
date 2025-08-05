import json
from bson import ObjectId
from config import coll_norm, coll_normative_un
from listar_regras_cliente import json_converter

def inspecionar_associacao_por_titulo():
    """
    Busca um normativo pelo título e exibe seu registro de associação completo
    da coleção 'normative_un' para análise forense.
    """
    # Parâmetros da análise
    cliente_id = "62aa15ba5ccad9aa706a2f4d"
    # Usando um dos títulos do relatório anterior como exemplo
    documento_titulo = "RESOLUÇÃO ANATEL Nº 765, DE 6 DE NOVEMBRO DE 2023"
    
    print("=" * 60)
    print(f"Iniciando inspeção forense para o documento:")
    print(f"'{documento_titulo}'")
    print("=" * 60)

    # Passo 1: Encontrar o documento na coleção 'norm' para obter seu ID
    norm_doc = coll_norm.find_one({"title": documento_titulo})
    if not norm_doc:
        print(f"ERRO: Documento com o título especificado não encontrado na coleção 'norm'.")
        return
    
    norm_id = norm_doc["_id"]
    print(f"Documento encontrado. ID: {norm_id}")

    # Passo 2: Usar o ID para encontrar o registro de associação em 'normative_un'
    query = {
        "norm_un": norm_id,
        "un_root": ObjectId(cliente_id)
    }
    assoc_doc = coll_normative_un.find_one(query)

    if not assoc_doc:
        print(f"ERRO: Registro de associação para o normativo ID {norm_id} não encontrado.")
        return

    # Passo 3: Imprimir o registro de associação completo para análise
    print("\n--- Registro de Associação Completo ('normative_un') ---\n")
    print(json.dumps(assoc_doc, indent=4, ensure_ascii=False, default=json_converter))
    print("\n" + "=" * 60)
    print("Inspeção concluída.")
    print("=" * 60)

if __name__ == "__main__":
    inspecionar_associacao_por_titulo()