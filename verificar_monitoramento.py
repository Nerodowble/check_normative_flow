import json
import os
from bson import ObjectId
from pymongo import MongoClient
from collections import Counter
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Obter as configurações do MongoDB a partir do .env
MONGO_URI = os.getenv("MONGO_URI")
CERTIFICATE_PATH = os.getenv("CERTIFICATE_PATH")
DB_NAME = os.getenv("DB_NAME")

# Validar se as variáveis foram carregadas corretamente
if not MONGO_URI or not CERTIFICATE_PATH or not DB_NAME:
    raise ValueError("As variáveis MONGO_URI, CERTIFICATE_PATH e DB_NAME precisam ser definidas no arquivo .env")

# Função auxiliar para log detalhado
def log_detalhado(mensagem):
    with open("log_verificacao_monitoramento.txt", "a") as log_file:
        log_file.write(mensagem + "\n")

def buscar_monitores(cliente_id, origem, db):
    """
    Retorna todos os monitores criados para um cliente específico com status ativo (status == 1) e a origem especificada.
    """
    monitor_collection = db["monitor"]
    monitores = list(monitor_collection.find({"un_root": ObjectId(cliente_id), "status": 1, "filters.origin": origem}))
    log_detalhado(f"[INFO] Monitores encontrados para cliente {cliente_id}: {len(monitores)}")
    return monitores

def verificar_documento_por_monitor(documento, monitor):
    """
    Verifica se o documento atende aos critérios de um monitor específico.
    Retorna uma análise detalhada.
    """
    texto = documento.get("text", "").lower()
    filtros = monitor.get("filters", [])

    log_detalhado(f"[INFO] Verificando documento ID {documento.get('_id')} no monitor ID {monitor.get('_id')}")

    if filtros:
        tag_negative = filtros[0].get("tag_negative", [])
        tag_positive = filtros[0].get("tag_positive", [])
    else:
        tag_negative = []
        tag_positive = []

    # Verificação das tags negativas
    negative_words = []
    for tag in tag_negative:
        for value in tag.get("value", []):
            negative_words.extend(value.get("value", []))

    for word in negative_words:
        if word.lower() in texto:
            log_detalhado(f"[INFO] Tag negativa encontrada: '{word}' no documento ID {documento.get('_id')}")
            return {
                "captura_esperada": False,
                "motivo": f"Tag negativa encontrada: '{word}' no documento.",
                "tags_negativas_encontradas": word
            }

    # Verificação das tags positivas
    positive_words = []
    for tag in tag_positive:
        for value in tag.get("value", []):
            positive_words.extend(value.get("value", []))

    tags_positivas_encontradas = []
    for word in positive_words:
        if word.lower() in texto:
            tags_positivas_encontradas.append(word)

    if tags_positivas_encontradas:
        log_detalhado(f"[INFO] Tags positivas encontradas: {tags_positivas_encontradas} no documento ID {documento.get('_id')}")
        return {
            "captura_esperada": True,
            "motivo": "Tags positivas encontradas, o documento deveria ter sido capturado.",
            "tags_positivas_encontradas": tags_positivas_encontradas
        }

    # Caso nenhuma tag positiva seja encontrada
    log_detalhado("[INFO] Nenhuma tag positiva encontrada, o documento não atende aos critérios de captura.")
    return {
        "captura_esperada": False,
        "motivo": "Nenhuma tag positiva encontrada."
    }

def verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
    """
    Realiza a verificação de monitoramento para os documentos faltantes, com base nas regras dos monitores.
    """
    # Configurando o cliente MongoDB
    client = MongoClient(MONGO_URI, tlsCertificateKeyFile=CERTIFICATE_PATH)
    db = client[DB_NAME]

    try:
        print(f"Iniciando verificação de monitoramento para o cliente com ID '{cliente_id}'...")
        log_detalhado(f"[INFO] Iniciando verificação para cliente ID {cliente_id} entre {data_inicial} e {data_final} para origem {origem}")

        monitores = buscar_monitores(cliente_id, origem, db)
        relatorio = []

        norm_collection = db["norm"]

        for doc in documentos_faltantes:
            documento_id = doc["_id"]
            documento = norm_collection.find_one({"_id": ObjectId(documento_id)})
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

    finally:
        # Fechar a conexão com o MongoDB no final do script, garantindo que isso ocorra após toda a execução
        client.close()

# Função para ser chamada a partir do main
def executar_verificacao_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
    verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes)
