import json
from bson import ObjectId
from config import coll_norm
from listar_regras_cliente import json_converter # Reutilizando o conversor que já criamos

def obter_e_salvar_documento(doc_id):
    """
    Busca um documento na coleção 'norm' pelo seu ID e o salva em um arquivo JSON.
    """
    print(f"Buscando documento com ID: {doc_id}...")
    documento = coll_norm.find_one({"_id": ObjectId(doc_id)})

    if not documento:
        print(f"ERRO: Documento com ID {doc_id} não foi encontrado na coleção 'norm'.")
        return

    nome_arquivo = f"documento_{doc_id}.json"
    try:
        with open(nome_arquivo, "w", encoding='utf-8') as f:
            json.dump(documento, f, indent=4, ensure_ascii=False, default=json_converter)
        print(f"Sucesso! Documento completo salvo em: {nome_arquivo}")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo JSON: {e}")


if __name__ == '__main__':
    print("Este script busca um documento normativo completo no banco de dados e o salva em um arquivo JSON.")
    doc_id_input = input("Por favor, informe o ID de um dos 11 documentos associados: ").strip()
    if doc_id_input:
        obter_e_salvar_documento(doc_id_input)
