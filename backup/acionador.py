# acionador.py

from datetime import datetime
from buscar_normativos import buscar_normativos
from verificar_normativos_clientes import verificar_normativos_clientes
from exibir_relatorio import exibir_relatorio
from verificar_taxonomia import verificar_taxonomia

def main(cliente_id, origem, data_inicio, data_fim):
    # Converter as datas para o formato esperado (YYYY-MM-DD)
    data_inicio_fmt = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
    data_fim_fmt = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")

    # Etapa 1: Buscar normativos pela origem e data
    normativos = buscar_normativos(origem, data_inicio_fmt, data_fim_fmt)

    # Filtrar os normativos apenas para o cliente especificado
    normativos_filtrados = [n for n in normativos if n.get("client_id") == cliente_id]

    # Etapa 2: Verificar normativos para o cliente especificado
    clientes_dict, documentos_faltantes = verificar_normativos_clientes(normativos_filtrados)

    # Etapa 3: Para cada documento faltante, verificar a associação de taxonomia
    for cliente_nome, dados_cliente in clientes_dict.items():
        if dados_cliente["documentos_faltantes"]:
            print(f"\nVerificando taxonomia para documentos faltantes do cliente '{cliente_nome}'...")
            for doc in dados_cliente["documentos_faltantes"]:
                normativo_id = str(doc["_id"])
                resultado_taxonomia = verificar_taxonomia(normativo_id)

                # Adiciona a informação de taxonomia (ou ausência dela) ao relatório
                if resultado_taxonomia:
                    if "taxonomias_associadas" not in dados_cliente:
                        dados_cliente["taxonomias_associadas"] = []
                    dados_cliente["taxonomias_associadas"].append({
                        "normativo_id": normativo_id,
                        "taxonomia": resultado_taxonomia[0]["taxonomia"],
                        "descricao": resultado_taxonomia[0]["descricao"],
                        "associado_ao_cliente": resultado_taxonomia[0]["associado_ao_cliente"]
                    })

    # Etapa 4: Exibir relatório final com informações de taxonomia
    exibir_relatorio(clientes_dict, documentos_faltantes)

if __name__ == "__main__":
    # Solicitar ao usuário os quatro dados necessários
    cliente_id = input("Informe o ID do cliente: ")
    origem = input("Informe a origem (ex: BACEN): ")
    data_inicio = input("Informe a data de início (formato DD/MM/YYYY): ")
    data_fim = input("Informe a data de fim (formato DD/MM/YYYY): ")

    # Executar o processo principal
    main(cliente_id, origem, data_inicio, data_fim)
