import json
from bson import ObjectId
from config import coll_normative_un
from analisar_associados import analisar_associacao_documento
from listar_regras_cliente import json_converter

def gerar_relatorio_avancado_pos_envio(cliente_id, origem):
    """
    Gera um relatório de análise avançado para todos os documentos em Pós-Envio
    de um cliente e origem específicos, mostrando a prova de associação para cada um.
    """
    print("\n" + "=" * 60)
    print("INICIANDO RELATÓRIO AVANÇADO DE PÓS-ENVIO")
    print(f"Cliente ID: {cliente_id} | Origem: {origem}")
    print("=" * 60)

    # Pipeline de Agregação para buscar e filtrar de forma eficiente
    pipeline = [
        {"$match": {"un_root": ObjectId(cliente_id), "stages": 2}},
        {"$lookup": {"from": "norm", "localField": "norm_un", "foreignField": "_id", "as": "norm_details"}},
        {"$unwind": "$norm_details"},
        {"$match": {"norm_details.origin": origem}}
    ]
    
    documentos_filtrados = list(coll_normative_un.aggregate(pipeline))

    if not documentos_filtrados:
        print(f"\nNenhum documento encontrado em Pós-Envio para este cliente com a origem '{origem}'.")
        print("=" * 60)
        return

    print(f"\n--- Análise de {len(documentos_filtrados)} Documentos em Pós-Envio ---")

    for doc_assoc in documentos_filtrados:
        documento_id_str = str(doc_assoc["norm_details"]["_id"])
        titulo = doc_assoc["norm_details"].get("title", "Título não encontrado")
        
        print(f"\n------------------------------------------------------------")
        print(f"DOCUMENTO: {titulo} (ID: {documento_id_str})")
        print(f"------------------------------------------------------------")

        # Chama o orquestrador principal para obter a causa da associação
        causa = analisar_associacao_documento(documento_id_str, cliente_id)
        
        print(f"  -> TIPO DE ASSOCIAÇÃO: {causa.get('tipo', 'N/A')}")
        
        # Imprime a prova com base no tipo de associação
        if causa.get('tipo') == 'Monitoramento':
            detalhes = causa.get('detalhes_match', {})
            tags = detalhes.get('lista_tags_positivas_encontradas', {})
            print(f"  -> PROVA: Capturado pela regra '{causa.get('nome_regra')}' (Status: {causa.get('status_regra')})")
            print(f"     Tags encontradas: {list(tags.keys())}")
        
        elif causa.get('tipo') == 'Taxonomia/Roteamento':
            detalhes = causa.get('detalhes_match', {})
            print(f"  -> PROVA: Capturado pela taxonomia '{causa.get('nome_taxonomia')}'")
            print(f"     Classe: '{detalhes.get('classe_documento')}' | Subclasse: '{detalhes.get('subclasse_documento')}'")
            print(f"     Acionou a Regra de Roteamento ID: {causa.get('id_regra')}")

        elif causa.get('tipo') == 'Encaminhamento Manual':
            detalhes = causa.get('detalhes_match', {})
            print(f"  -> PROVA: Ação manual detectada.")
            print(f"     Primeiro encaminhamento em: {detalhes.get('primeiro_encaminhamento_em')}")
            print(f"     Total de áreas associadas: {detalhes.get('total_areas_associadas')}")
        
        else: # Cobre falhas e outros casos
            print(f"  -> DETALHES: {causa.get('detalhes', 'Não foi possível determinar a causa exata.')}")

    print("\n" + "=" * 60)
    print("RELATÓRIO AVANÇADO CONCLUÍDO")
    print("=" * 60)