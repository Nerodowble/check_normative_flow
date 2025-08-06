import json
from bson import ObjectId
from datetime import datetime
from config import coll_norm, coll_normative_un, coll_monitor, coll_routing_rule
from verificar_monitoramento import verificar_documento_por_monitor
from analisar_taxonomia import analisar_associacao_por_taxonomia

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

    else:  # Se from_monitor for False, a associação veio da Taxonomia ou foi Manual.
        # Tenta primeiro analisar via Taxonomia/Roteamento.
        resultado_taxonomia = analisar_associacao_por_taxonomia(documento_id, cliente_id)

        # Se a análise de taxonomia falhar por falta de dados, verificamos a hipótese de encaminhamento manual.
        if resultado_taxonomia.get("tipo") == "Taxonomia/Roteamento (Dados Insuficientes)":
            associated_uns = assoc_data.get("associated_uns", [])
            # A presença de 'forwarded_at' é a prova da ação manual.
            if associated_uns and any("forwarded_at" in un for un in associated_uns):
                primeiro_encaminhamento = next((un for un in associated_uns if "forwarded_at" in un), None)
                return {
                    "tipo": "Encaminhamento Manual",
                    "detalhes": "O documento foi localizado na Busca e encaminhado manualmente por um usuário para uma ou mais áreas.",
                    "detalhes_match": {
                        "primeiro_encaminhamento_em": primeiro_encaminhamento.get("forwarded_at") if primeiro_encaminhamento else "Não encontrado",
                        "total_areas_associadas": len(associated_uns)
                    }
                }
        
        # Se a análise de taxonomia foi bem-sucedida ou falhou por outro motivo, retorna o resultado original.
        return resultado_taxonomia

def json_converter(o):
    """Converte tipos não serializáveis para JSON."""
    if isinstance(o, ObjectId):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o)} is not JSON serializable")

def executar_analise_associados(documentos_ids, cliente_id, salvar_relatorio=True, salvar_debug=True):
    """
    Orquestra a análise para uma lista de documentos associados a um cliente,
    retorna os resultados e, opcionalmente, salva relatórios.
    """
    relatorio_final = []
    debug_documento_salvo = False

    for doc_id in documentos_ids:
        normativo = coll_norm.find_one({"_id": ObjectId(doc_id)})
        titulo = normativo.get("title", "Título não encontrado") if normativo else "Documento não encontrado"

        if salvar_debug and not debug_documento_salvo and normativo:
            nome_arquivo_debug = f"debug_documento_{doc_id}.json"
            with open(nome_arquivo_debug, "w", encoding='utf-8') as f:
                json.dump(normativo, f, indent=4, ensure_ascii=False, default=json_converter)
            print(f"Arquivo de depuração salvo: {nome_arquivo_debug}")
            debug_documento_salvo = True

        causa_associacao = analisar_associacao_documento(doc_id, cliente_id)
        
        relatorio_final.append({
            "documento_id": doc_id,
            "title": titulo,
            "causa_da_associacao": causa_associacao
        })

    if salvar_relatorio:
        nome_arquivo = f"relatorio_analise_associados_{cliente_id}.json"
        with open(nome_arquivo, "w", encoding='utf-8') as f:
            json.dump(relatorio_final, f, indent=4, ensure_ascii=False, default=json_converter)
        print(f"Análise de associados concluída. Relatório salvo em: {nome_arquivo}")
        
    return relatorio_final

if __name__ == '__main__':
    # Exemplo de como chamar a função (para testes futuros)
    # Substituir com IDs de teste reais
    # test_doc_ids = ["ID_DO_DOCUMENTO_1", "ID_DO_DOCUMENTO_2"]
    # test_cliente_id = "ID_DO_CLIENTE"
    # executar_analise_associados(test_doc_ids, test_cliente_id)
    pass
