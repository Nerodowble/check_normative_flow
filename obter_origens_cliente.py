from bson import ObjectId
from config import coll_normative_un

def obter_todas_origens(cliente_id):
    """
    Busca todas as origens únicas associadas a um cliente na coleção 'normative_un'
    usando uma pipeline de agregação para eficiência.

    Args:
        cliente_id (str): O ID do cliente.

    Returns:
        list: Uma lista de strings contendo as origens únicas, ordenadas alfabeticamente.
    """
    try:
        pipeline = [
            # Estágio 1: Filtrar todos os registros de associação para o cliente raiz.
            {
                "$match": {
                    "un_root": ObjectId(cliente_id)
                }
            },
            # Estágio 2: Agrupar pelo campo 'origin' para obter valores únicos.
            {
                "$group": {
                    "_id": "$norm_infos.origin"
                }
            },
            # Estágio 3: Ordenar os resultados alfabeticamente.
            {
                "$sort": {
                    "_id": 1
                }
            }
        ]
        
        resultados = coll_normative_un.aggregate(pipeline)
        
        # Extrai os nomes das origens, filtrando valores nulos ou vazios.
        origens = [doc['_id'] for doc in resultados if doc['_id']]
        
        return origens

    except Exception as e:
        print(f"Ocorreu um erro ao buscar as origens do cliente: {e}")
        return []

if __name__ == '__main__':
    # Exemplo de como usar a função para teste
    # Substitua pelo ID de um cliente real para testar
    test_cliente_id = "62aa15ba5ccad9aa706a2f4d" 
    print(f"Buscando origens para o cliente ID: {test_cliente_id}")
    lista_origens = obter_todas_origens(test_cliente_id)
    print(f"Encontradas {len(lista_origens)} origens:")
    for origem in lista_origens:
        print(f"- {origem}")