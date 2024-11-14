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
    Retorna todos os monitores criados para um cliente específico.
    """
    monitores = list(coll_monitor.find({"un_root": ObjectId(cliente_id)}))
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
    
    # Iterar sobre cada filtro, pois filtros é uma lista
    for filtro in filtros:
        # Verificação de origem
        origens_monitoradas = filtro.get("origin", [])
        if origens_monitoradas and documento.get("origin") not in origens_monitoradas:
            log_detalhado("[INFO] Origem do documento não corresponde às origens monitoradas.")
            return {
                "captura_esperada": False,
                "motivo": "Origem do documento não corresponde às origens monitoradas"
            }
        
        # Verificação das tags positivas
        tags_positivas = [tag for grupo in filtro.get("tag_positive", []) for tag in grupo.get("value", [])]
        ocorrencias_positivas = contar_ocorrencias_tags(texto, tags_positivas)
        num_tags_positivas_encontradas = sum(1 for ocorrencia in ocorrencias_positivas.values() if ocorrencia > 0)
        log_detalhado(f"[INFO] Tags positivas encontradas: {num_tags_positivas_encontradas}, Detalhes: {ocorrencias_positivas}")
        
        # Verificação das tags negativas
        tags_negativas = [tag for grupo in filtro.get("tag_negative", []) for tag in grupo.get("value", [])]
        ocorrencias_negativas = contar_ocorrencias_tags(texto, tags_negativas)
        num_tags_negativas_encontradas = sum(1 for ocorrencia in ocorrencias_negativas.values() if ocorrencia > 0)
        log_detalhado(f"[INFO] Tags negativas encontradas: {num_tags_negativas_encontradas}, Detalhes: {ocorrencias_negativas}")
        
        # Porcentagem de tags positivas e negativas
        total_tags_encontradas = num_tags_positivas_encontradas + num_tags_negativas_encontradas
        if total_tags_encontradas > 0:
            porcentagem_positivas = (num_tags_positivas_encontradas / total_tags_encontradas) * 100
            porcentagem_negativas = (num_tags_negativas_encontradas / total_tags_encontradas) * 100
        else:
            porcentagem_positivas = porcentagem_negativas = 0

        log_detalhado(f"[INFO] Porcentagem de tags positivas: {porcentagem_positivas}%, negativas: {porcentagem_negativas}%")

        # Determina se o documento atende aos critérios de captura
        captura_esperada = num_tags_positivas_encontradas > 0 and num_tags_negativas_encontradas == 0
        motivo = []
        if not captura_esperada:
            if num_tags_positivas_encontradas == 0:
                motivo.append("Nenhuma tag positiva obrigatória encontrada.")
            if num_tags_negativas_encontradas > 0:
                motivo.append("Tags negativas encontradas, o documento não deve ser capturado.")
        
        log_detalhado(f"[INFO] Resultado da verificação: Captura esperada: {captura_esperada}, Motivo: {motivo}")
        
        return {
            "captura_esperada": captura_esperada,
            "num_tags_positivas_encontradas": num_tags_positivas_encontradas,
            "lista_tags_positivas_encontradas": dict(ocorrencias_positivas),
            "num_tags_negativas_encontradas": num_tags_negativas_encontradas,
            "lista_tags_negativas_encontradas": dict(ocorrencias_negativas),
            "porcentagem_positivas": porcentagem_positivas,
            "porcentagem_negativas": porcentagem_negativas,
            "motivo": motivo or ["Documento atende aos critérios de captura."]
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
            
            # Variáveis para armazenar contagens totais para este documento em todos os monitores
            total_tags_positivas_encontradas = 0
            total_tags_negativas_encontradas = 0
            
            # Verifica o documento em cada monitor para o cliente
            for monitor in monitores:
                resultado_monitor = verificar_documento_por_monitor(documento, monitor)
                
                # Adiciona o resultado detalhado ao relatório
                doc_resultado["reason_not_captured"].append({
                    "monitor_id": str(monitor["_id"]),
                    "captura_esperada": resultado_monitor["captura_esperada"],
                    "num_tags_positivas_encontradas": resultado_monitor["num_tags_positivas_encontradas"],
                    "lista_tags_positivas_encontradas": resultado_monitor["lista_tags_positivas_encontradas"],
                    "num_tags_negativas_encontradas": resultado_monitor["num_tags_negativas_encontradas"],
                    "lista_tags_negativas_encontradas": resultado_monitor["lista_tags_negativas_encontradas"],
                    "porcentagem_positivas": resultado_monitor["porcentagem_positivas"],
                    "porcentagem_negativas": resultado_monitor["porcentagem_negativas"],
                    "motivo": resultado_monitor["motivo"]
                })
                log_detalhado(f"[INFO] Resultado para monitor {monitor['_id']}: {resultado_monitor}")
                
                # Atualizar contagens totais
                total_tags_positivas_encontradas += resultado_monitor["num_tags_positivas_encontradas"]
                total_tags_negativas_encontradas += resultado_monitor["num_tags_negativas_encontradas"]

            # Adicionar resumo das contagens ao final de cada documento
            doc_resultado["summary"] = {
                "total_tags_positivas_encontradas": total_tags_positivas_encontradas,
                "total_tags_negativas_encontradas": total_tags_negativas_encontradas
            }

            relatorio.append(doc_resultado)

    # Salva o relatório em um arquivo JSON
    with open(f"relatorio_monitoramento_{cliente_id}.json", "w") as f:
        json.dump(relatorio, f, indent=4, ensure_ascii=False)
    
    print("Verificação de monitoramento concluída e salva em JSON.")
    log_detalhado(f"[INFO] Relatório final salvo para cliente ID {cliente_id}")

# Função para ser chamada a partir do main
def executar_verificacao_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
    verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes)
