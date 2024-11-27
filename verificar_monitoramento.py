import json
from bson import ObjectId
from config import coll_monitor, coll_norm
from collections import Counter

# Função auxiliar para log detalhado
def log_detalhado(mensagem):
    with open("log_verificacao_monitoramento.txt", "a") as log_file:
        log_file.write(mensagem + "\n")

def buscar_monitores(cliente_id):
    """
    Retorna todos os monitores criados para um cliente específico com status ativo (status == 1).
    """
    monitores = list(coll_monitor.find({"un_root": ObjectId(cliente_id), "status": 1}))
    log_detalhado(f"[INFO] Monitores encontrados para cliente {cliente_id}: {len(monitores)}")
    return monitores

def contar_ocorrencias_tags(texto, tags):
    """
    Conta as ocorrências de cada tag em um texto e retorna um dicionário com os resultados.
    """
    ocorrencias = Counter()
    for tag in tags:
        if isinstance(tag, str):  # Garantir que tag é uma string
            ocorrencias[tag] = texto.count(tag.lower())
    log_detalhado(f"[INFO] Ocorrências de tags encontradas: {dict(ocorrencias)}")
    return ocorrencias

def verificar_documento_por_monitor(documento, monitor):
    """
    Verifica se o documento atende aos critérios de um monitor específico.
    Retorna uma análise detalhada.
    """
    texto = documento.get("text", "").lower()
    filtros = monitor.get("filters", [])
    
    log_detalhado(f"[INFO] Verificando documento ID {documento.get('_id')} no monitor ID {monitor.get('_id')}")
    
    for filtro in filtros:
        # Verificação das tags negativas - PRIORIDADE
        tags_negativas = [tag for grupo in filtro.get("tag_negative", []) for tag in grupo.get("value", [])]
        ocorrencias_negativas = contar_ocorrencias_tags(texto, tags_negativas)
        num_tags_negativas_encontradas = sum(1 for ocorrencia in ocorrencias_negativas.values() if ocorrencia > 0)

        if num_tags_negativas_encontradas > 0:
            # Se uma tag negativa for encontrada, isso significa que o documento não deveria estar associado ao cliente.
            log_detalhado("[INFO] Tags negativas encontradas, o documento não deve ser associado.")
            return {
                "captura_esperada": False,
                "motivo": "Tags negativas encontradas, o documento não deve ser associado ao cliente.",
                "num_tags_negativas_encontradas": num_tags_negativas_encontradas,
                "lista_tags_negativas_encontradas": dict(ocorrencias_negativas)
            }

        # Se nenhuma tag negativa for encontrada, verificar as tags positivas
        tags_positivas = [tag for grupo in filtro.get("tag_positive", []) for tag in grupo.get("value", [])]
        ocorrencias_positivas = contar_ocorrencias_tags(texto, tags_positivas)
        num_tags_positivas_encontradas = sum(1 for ocorrencia in ocorrencias_positivas.values() if ocorrencia > 0)

        if num_tags_positivas_encontradas > 0:
            # Se pelo menos uma tag positiva for encontrada, o documento deveria ter sido associado ao cliente
            log_detalhado("[INFO] Tags positivas encontradas, o documento deveria ter sido capturado e associado ao cliente.")
            return {
                "captura_esperada": True,
                "motivo": "Tags positivas encontradas, o documento deveria ter sido capturado.",
                "num_tags_positivas_encontradas": num_tags_positivas_encontradas,
                "lista_tags_positivas_encontradas": dict(ocorrencias_positivas)
            }

        # Caso nenhuma tag positiva seja encontrada
        log_detalhado("[INFO] Nenhuma tag positiva encontrada, o documento não atende aos critérios de captura.")
        return {
            "captura_esperada": False,
            "motivo": "Nenhuma tag positiva encontrada.",
            "num_tags_positivas_encontradas": num_tags_positivas_encontradas,
            "lista_tags_positivas_encontradas": dict(ocorrencias_positivas)
        }

def verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
    """
    Realiza a verificação de monitoramento para os documentos faltantes, com base nas regras dos monitores.
    """
    print(f"Iniciando verificação de monitoramento para o cliente com ID '{cliente_id}'...")
    log_detalhado(f"[INFO] Iniciando verificação para cliente ID {cliente_id} entre {data_inicial} e {data_final} para origem {origem}")
    
    monitores = buscar_monitores(cliente_id)
    relatorio = []

    for doc in documentos_faltantes:
        documento_id = doc["_id"]
        documento = coll_norm.find_one({"_id": ObjectId(documento_id)})
        log_detalhado(f"[INFO] Documento encontrado com ID {documento_id}: {documento}")

        if documento and documento.get("origin") == origem:
            doc_resultado = {
                "documento_id": documento_id,
                "title": doc.get("title"),
                "reason_not_captured": []
            }
            
            # Verifica o documento em cada monitor para o cliente
            for monitor in monitores:
                resultado_monitor = verificar_documento_por_monitor(documento, monitor)
                
                # Adiciona o resultado detalhado ao relatório
                doc_resultado["reason_not_captured"].append({
                    "monitor_id": str(monitor["_id"]),
                    **resultado_monitor
                })
                log_detalhado(f"[INFO] Resultado para monitor {monitor['_id']}: {resultado_monitor}")

            relatorio.append(doc_resultado)

    # Salva o relatório em um arquivo JSON
    with open(f"relatorio_monitoramento_{cliente_id}.json", "w") as f:
        json.dump(relatorio, f, indent=4, ensure_ascii=False)
    
    print("Verificação de monitoramento concluída e salva em JSON.")
    log_detalhado(f"[INFO] Relatório final salvo para cliente ID {cliente_id}")

# Função para ser chamada a partir do main
def executar_verificacao_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
    verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes)
