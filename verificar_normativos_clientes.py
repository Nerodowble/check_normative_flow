from bson import ObjectId
from config import coll_normative_un, coll_un
from concurrent.futures import ThreadPoolExecutor, as_completed

def obter_cliente_id_por_nome(cliente_nome):
    """
    Busca o cliente na coleção 'un' pelo nome usando regex insensível a maiúsculas/minúsculas
    e retorna o ID do cliente.
    """
    cliente = coll_un.find_one({"name": {"$regex": f".*{cliente_nome}.*", "$options": "i"}})
    if cliente:
        return str(cliente["_id"])
    else:
        print(f"Cliente com o nome '{cliente_nome}' não encontrado.")
        return None

def processar_normativo(normativo, cliente_id):
    """Função para processar um normativo individual específico do cliente e retornar dados relacionados."""
    norm_id = normativo["_id"]
    # Filtrar pela un_root que corresponde ao cliente_id fornecido
    normative_un_data = list(coll_normative_un.find({"norm_un": norm_id, "un_root": ObjectId(cliente_id)}))
    cliente_dados = []

    if normative_un_data:
        for entry in normative_un_data:
            un_root = entry.get("un_root")
            stages = entry.get("stages")
            from_monitor = entry.get("from_monitor", False)
            associated_uns = entry.get("associated_uns", [])

            # Verifica se o un_root corresponde ao cliente_id fornecido
            if un_root == ObjectId(cliente_id):
                cliente_data = coll_un.find_one({"_id": ObjectId(un_root)})
                if cliente_data:
                    cliente_dados.append((cliente_data, stages, from_monitor, associated_uns))
    else:
        # Retornar o normativo como faltante se não houver dados relevantes para o cliente específico
        return normativo, None

    return normativo, cliente_dados

def verificar_normativos_cliente(normativos, cliente_id=None, cliente_nome=None):
    """
    Agrupa normativos para um cliente específico, identificado pelo cliente_id ou cliente_nome,
    e conta quantos estão em cada estágio.
    """
    # Se o cliente_id não for fornecido, buscar o ID a partir do nome do cliente
    if not cliente_id and cliente_nome:
        cliente_id = obter_cliente_id_por_nome(cliente_nome)
        if not cliente_id:
            return {}, []  # Retorna vazio se o cliente não foi encontrado

    print(f"Iniciando verificação de normativos para o cliente com ID '{cliente_id}'...")
    clientes_dict = {}
    documentos_faltantes = []
    
    # Lista com todos os IDs de normativos encontrados para comparação posterior
    todos_ids_normativos = {str(normativo["_id"]) for normativo in normativos}

    # Executar cada normativo em paralelo
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(processar_normativo, normativo, cliente_id) for normativo in normativos]
        
        for future in as_completed(futures):
            normativo, cliente_dados = future.result()
            norm_id_str = str(normativo["_id"])
            
            if cliente_dados:
                for cliente_data, stages, from_monitor, associated_uns in cliente_dados:
                    cliente_nome = cliente_data.get("name", "Desconhecido")
                    cliente_status = cliente_data.get("status")

                    # Inicializar contadores para o cliente, se não existir
                    if cliente_nome not in clientes_dict:
                        clientes_dict[cliente_nome] = {
                            "total_documentos": 0,
                            "pre_envio": 0,
                            "pos_envio_caixa_entrada": 0,
                            "pos_envio_sem_caixa_entrada": 0,
                            "busca": 0,
                            "monitor": 0,
                            "nao_monitor": 0,
                            "documentos_ids": set()
                        }

                    # Contabilizar documento no cliente apenas se o status for ativo
                    if cliente_status == 1:
                        clientes_dict[cliente_nome]["total_documentos"] += 1
                        clientes_dict[cliente_nome]["documentos_ids"].add(norm_id_str)

                        # Contagem por estágio e verificação de Caixa de Entrada para o Pós-Envio
                        if stages == 1:
                            clientes_dict[cliente_nome]["pre_envio"] += 1
                        elif stages == 2:
                            if associated_uns:
                                clientes_dict[cliente_nome]["pos_envio_caixa_entrada"] += 1
                            else:
                                clientes_dict[cliente_nome]["pos_envio_sem_caixa_entrada"] += 1
                        elif stages == 3:
                            clientes_dict[cliente_nome]["busca"] += 1

                        # Contar quantos vieram do monitor e quantos não vieram
                        if from_monitor:
                            clientes_dict[cliente_nome]["monitor"] += 1
                        else:
                            clientes_dict[cliente_nome]["nao_monitor"] += 1
            else:
                # Documento sem entrada relevante - adicionar aos faltantes gerais
                documentos_faltantes.append({
                    "_id": norm_id_str,
                    "title": normativo.get("title", "N/A"),
                    "type": normativo.get("type", "N/A"),
                    "subject": normativo.get("subject", "N/A"),
                    "link": normativo.get("link", "N/A")
                })

    # Comparar IDs de normativos para encontrar faltantes específicos do cliente
    for cliente, dados in clientes_dict.items():
        ids_faltantes = todos_ids_normativos - dados["documentos_ids"]
        if ids_faltantes:
            dados["documentos_faltantes"] = [
                {"_id": doc_id} for doc_id in ids_faltantes
            ]
        else:
            dados["documentos_faltantes"] = []

    print("Verificação de normativos concluída.")
    return clientes_dict, documentos_faltantes
