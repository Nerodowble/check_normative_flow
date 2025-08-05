from bson import ObjectId
from config import coll_normative_un
from analisar_taxonomia import analisar_associacao_por_taxonomia

def validar_pos_envio_com_prova():
    """
    Realiza uma análise completa de todos os documentos em Pós-Envio para um cliente
    e origem específicos, provando como os documentos de taxonomia foram associados.
    """
    # Parâmetros da análise
    cliente_id = "62aa15ba5ccad9aa706a2f4d"
    origem_filtro = "ANATEL/DOU"
    
    print("=" * 60)
    print(f"Iniciando análise com PROVA do Pós-Envio para o cliente ID: {cliente_id}")
    print(f"Filtrando pela origem: '{origem_filtro}'")
    print("=" * 60)

    # Pipeline de Agregação para buscar e filtrar de forma eficiente
    pipeline = [
        {"$match": {"un_root": ObjectId(cliente_id), "stages": 2}},
        {"$lookup": {"from": "norm", "localField": "norm_un", "foreignField": "_id", "as": "norm_details"}},
        {"$unwind": "$norm_details"},
        {"$match": {"norm_details.origin": origem_filtro}}
    ]
    
    documentos_filtrados = list(coll_normative_un.aggregate(pipeline))

    if not documentos_filtrados:
        print(f"Nenhum documento encontrado em Pós-Envio para este cliente com a origem '{origem_filtro}'.")
        return

    # Contadores e listas para o relatório
    capturados_por_monitor = 0
    capturados_por_taxonomia = 0
    provas_taxonomia = []
    
    for doc in documentos_filtrados:
        if doc.get("from_monitor", False):
            capturados_por_monitor += 1
        else:
            capturados_por_taxonomia += 1
            # Para os documentos de taxonomia, buscamos a prova!
            documento_id_str = str(doc["norm_details"]["_id"])
            prova = analisar_associacao_por_taxonomia(documento_id_str, cliente_id)
            provas_taxonomia.append({
                "title": doc["norm_details"].get("title", "Título não encontrado"),
                "analise": prova
            })

    # Imprime o relatório final
    print("\n--- Relatório de Análise do Pós-Envio (Com Prova de Taxonomia) ---\n")
    print(f"Total de documentos encontrados: {len(documentos_filtrados)}")
    print("-" * 50)
    
    print(f"Capturados por Monitoramento: {capturados_por_monitor}")
    
    print(f"\nCapturados por Taxonomia/Roteamento: {capturados_por_taxonomia}")
    if provas_taxonomia:
        print("\n--- PROVA DE ASSOCIAÇÃO POR TAXONOMIA ---")
        for item in provas_taxonomia:
            print(f"\n  Documento: {item['title']}")
            if item['analise'].get('tipo') == 'Taxonomia/Roteamento':
                detalhes = item['analise']['detalhes_match']
                print(f"    -> Causa: Classificado como '{detalhes['classe_documento']} / {detalhes['subclasse_documento']}'")
                print(f"    -> Acionou a Regra de Roteamento ID: {item['analise']['id_regra']}")
            else:
                # Mostra outras mensagens, como "Dados Insuficientes"
                print(f"    -> Análise: {item['analise'].get('detalhes', 'Detalhe não disponível')}")

    print("\n" + "=" * 60)
    print("Análise concluída.")
    print("=" * 60)

if __name__ == "__main__":
    validar_pos_envio_com_prova()