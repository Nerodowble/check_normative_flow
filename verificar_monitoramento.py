import json
import re
from bson import ObjectId
from config import coll_monitor, coll_norm
from collections import Counter

# Função auxiliar para log detalhado
def log_detalhado(mensagem):
    with open("log_verificacao_monitoramento.txt", "a", encoding="utf-8") as log_file:
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
    Verifica se o documento atende aos critérios de um monitor específico,
    considerando todos os seus filtros e múltiplos formatos de tag.
    Retorna uma análise detalhada.
    """
    # Cria um "super texto" concatenando os campos relevantes para uma busca mais abrangente.
    # Limpa o texto de tags HTML para uma busca mais precisa
    raw_text = str(documento.get("text", ""))
    clean_text = re.sub('<[^<]+?>', '', raw_text)

    texto_busca = (
        str(documento.get("title", "")) + " " +
        str(documento.get("subject", "")) + " " +
        clean_text
    ).lower()
    
    filtros = monitor.get("filters", [])
    
    log_detalhado(f"[INFO] Verificando documento ID {documento.get('_id')} no monitor ID {monitor.get('_id')}")

    resultados_filtros = []

    for i, filtro in enumerate(filtros):
        log_detalhado(f"[INFO] Avaliando filtro {i+1}/{len(filtros)} do monitor.")
        
        # 1. Extrair e verificar tags negativas (lógica final e correta)
        tags_negativas_raw = filtro.get("tag_negative", [])
        tags_negativas = [
            tag.lower()
            for grupo in tags_negativas_raw
            for tag in grupo.get("value", [])
            if isinstance(tag, str) and tag
        ]
        ocorrencias_negativas = contar_ocorrencias_tags(texto_busca, tags_negativas)
        if any(v > 0 for v in ocorrencias_negativas.values()):
            motivo = f"Filtro {i+1}: Tags negativas encontradas, documento não deve ser associado."
            log_detalhado(f"[RESULT] {motivo}")
            # Se uma tag negativa é encontrada, este filtro resulta em um veto.
            # Podemos parar de verificar este monitor e considerá-lo como "não capturar".
            return {
                "captura_esperada": False,
                "motivo": motivo,
                "num_tags_negativas_encontradas": sum(1 for v in ocorrencias_negativas.values() if v > 0),
                "lista_tags_negativas_encontradas": dict(ocorrencias_negativas)
            }

        # 2. Verificar tags positivas com a lógica final e correta
        grupos_positivos_raw = filtro.get("tag_positive", [])
        
        # Para o relatório de falha, calcula as ocorrências de todas as tags positivas do filtro.
        todas_tags_positivas_do_filtro = [
            tag.lower()
            for grupo in grupos_positivos_raw
            for tag in grupo.get("value", [])
            if isinstance(tag, str) and tag
        ]
        ocorrencias_positivas = contar_ocorrencias_tags(texto_busca, todas_tags_positivas_do_filtro)

        if not grupos_positivos_raw:
            continue

        todos_grupos_corresponderam = True
        tags_encontradas_no_filtro = {}

        for grupo in grupos_positivos_raw:
            # A lógica E/OU está aninhada, precisamos descer um nível
            subgrupos = grupo.get("value", [])
            for subgrupo in subgrupos:
                if isinstance(subgrupo, dict) and subgrupo.get("operator") == "Or":
                    tags_do_subgrupo = [tag.lower() for tag in subgrupo.get("value", []) if isinstance(tag, str) and tag]
                    
                    if not any(texto_busca.count(tag) > 0 for tag in tags_do_subgrupo):
                        todos_grupos_corresponderam = False
                        break
                    else:
                        for tag in tags_do_subgrupo:
                            if texto_busca.count(tag) > 0:
                                tags_encontradas_no_filtro[tag] = texto_busca.count(tag)
            if not todos_grupos_corresponderam:
                break
        
        if todos_grupos_corresponderam and tags_encontradas_no_filtro:
            motivo = f"Filtro {i+1}: Todas as condições de tags positivas foram atendidas."
            log_detalhado(f"[RESULT] {motivo}")
            return {
                "captura_esperada": True,
                "motivo": motivo,
                "num_tags_positivas_encontradas": len(tags_encontradas_no_filtro),
                "lista_tags_positivas_encontradas": tags_encontradas_no_filtro
            }
        
        # Guarda o resultado de falha deste filtro para o relatório final, caso nenhum filtro dê match
        resultados_filtros.append({
            "filtro": i + 1,
            "motivo": "Nenhuma tag positiva encontrada neste filtro.",
            "ocorrencias": dict(ocorrencias_positivas)
        })

    # 3. Se o loop terminar, nenhum filtro deu match positivo
    log_detalhado("[RESULT] Nenhum dos filtros do monitor resultou em captura.")
    return {
        "captura_esperada": False,
        "motivo": "Nenhum dos filtros do monitor correspondeu aos critérios de captura (sem tags positivas encontradas).",
        "detalhes_filtros": resultados_filtros
    }

def verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
    """
    Realiza a verificação de monitoramento para os documentos faltantes e retorna o relatório.
    """
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
            
            for monitor in monitores:
                resultado_monitor = verificar_documento_por_monitor(documento, monitor)
                doc_resultado["reason_not_captured"].append({
                    "monitor_id": str(monitor["_id"]),
                    **resultado_monitor
                })
            relatorio.append(doc_resultado)
    
    return relatorio

# Função para ser chamada a partir do main
def executar_verificacao_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes, salvar_relatorio=True):
    relatorio = verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes)
    if salvar_relatorio:
        # Salva o relatório em um arquivo JSON
        with open(f"relatorio_monitoramento_{cliente_id}.json", "w") as f:
            json.dump(relatorio, f, indent=4, ensure_ascii=False)
        print("Verificação de monitoramento concluída e salva em JSON.")
    log_detalhado(f"[INFO] Relatório final salvo para cliente ID {cliente_id}")
