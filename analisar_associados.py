import json
from bson import ObjectId
from config import coll_norm, coll_normative_un, coll_monitor, coll_routing_rule
from verificar_monitoramento import verificar_documento_por_monitor
from verificar_taxonomia import verificar_taxonomia

def analisar_associacao_documento(documento_id, cliente_id):
    """
    Analisa um único documento associado, usando uma abordagem híbrida para
    determinar a regra específica que causou a associação.
    """
    print(f"Analisando o motivo da associação para o documento {documento_id}...")

    # 1. Buscar dados essenciais
    assoc_data = coll_normative_un.find_one({"norm_un": ObjectId(documento_id), "un_root": ObjectId(cliente_id)})
    if not assoc_data:
        return {"tipo": "Erro", "detalhes": "Associação não encontrada na coleção normative_un."}

    documento = coll_norm.find_one({"_id": ObjectId(documento_id)})
    if not documento:
        return {"tipo": "Erro", "detalhes": f"Documento com ID {documento_id} não encontrado."}

    from_monitor = assoc_data.get("from_monitor", False)

    # 2. Lógica Híbrida de Verificação
    if from_monitor:
        # TENTATIVA 1: Verificar via lógica de Monitoramento
        # Busca TODOS os monitores do cliente, incluindo inativos, para um diagnóstico completo.
        monitores_cliente = list(coll_monitor.find({"un_root": ObjectId(cliente_id)}))
        for monitor in monitores_cliente:
            resultado = verificar_documento_por_monitor(documento, monitor)
            if resultado.get("captura_esperada"):
                return {
                    "tipo": "Monitoramento",
                    "id_regra": str(monitor["_id"]),
                    "nome_regra": monitor.get("name", "Monitor sem nome"),
                    "status_regra": "Ativo" if monitor.get("status") == 1 else "Inativo",
                    "detalhes_match": resultado
                }
        
        # Se a simulação do monitor não encontrar uma correspondência, isso indica uma discrepância.
        return {
            "tipo": "Monitoramento (Falha na Simulação)",
            "detalhes": "O documento foi marcado como capturado por um monitor, mas a simulação atual não conseguiu replicar essa captura. Isso pode indicar uma regra de monitoramento que foi alterada ou desativada desde a captura original."
        }

    else: # Se from_monitor for False, verificamos apenas via Taxonomia
        resultado_taxonomia = verificar_taxonomia(documento_id)
        for res in resultado_taxonomia:
            if res.get("associado_ao_cliente") and res.get("cliente_id") == cliente_id:
                 return {
                    "tipo": "Taxonomia/Roteamento",
                    "nome_regra": res.get("taxonomia"),
                    "descricao_regra": res.get("descricao"),
                    "detalhes_match": {
                        "tags_correspondentes": res.get("tags_correspondentes")
                    }
                }
        return {"tipo": "Taxonomia/Roteamento (Falhou)", "detalhes": "Match de taxonomia indicado, mas nenhuma regra de roteamento correspondente foi encontrada."}

def executar_analise_associados(documentos_ids, cliente_id):
    """
    Orquestra a análise para uma lista de documentos associados a um cliente
    e gera um relatório em JSON. Também salva um documento de exemplo para depuração.
    """
    print(f"\nIniciando análise de causa para {len(documentos_ids)} documentos já associados...")
    
    relatorio_final = []
    debug_documento_salvo = False

    for doc_id in documentos_ids:
        # Obter o título do normativo para o relatório
        normativo = coll_norm.find_one({"_id": ObjectId(doc_id)})
        titulo = normativo.get("title", "Título não encontrado") if normativo else "Documento não encontrado"

        # Para depuração, salva o primeiro documento da lista em um arquivo separado
        if not debug_documento_salvo and normativo:
            nome_arquivo_debug = f"debug_documento_{doc_id}.json"
            with open(nome_arquivo_debug, "w", encoding='utf-8') as f:
                # Reutiliza o conversor de JSON para garantir que ObjectId seja tratado
                from listar_regras_cliente import json_converter
                json.dump(normativo, f, indent=4, ensure_ascii=False, default=json_converter)
            print(f"Arquivo de depuração salvo: {nome_arquivo_debug}")
            debug_documento_salvo = True

        # Analisar o motivo da associação
        causa_associacao = analisar_associacao_documento(doc_id, cliente_id)
        
        relatorio_final.append({
            "documento_id": doc_id,
            "title": titulo,
            "causa_da_associacao": causa_associacao
        })

    # Salvar o relatório final em um arquivo JSON
    nome_arquivo = f"relatorio_analise_associados_{cliente_id}.json"
    with open(nome_arquivo, "w", encoding='utf-8') as f:
        json.dump(relatorio_final, f, indent=4, ensure_ascii=False)
        
    print(f"Análise de associados concluída. Relatório salvo em: {nome_arquivo}")

if __name__ == '__main__':
    # Exemplo de como chamar a função (para testes futuros)
    # Substituir com IDs de teste reais
    # test_doc_ids = ["ID_DO_DOCUMENTO_1", "ID_DO_DOCUMENTO_2"]
    # test_cliente_id = "ID_DO_CLIENTE"
    # executar_analise_associados(test_doc_ids, test_cliente_id)
    pass
