from datetime import datetime
from buscar_normativos import buscar_normativos
from verificar_normativos_clientes import verificar_normativos_clientes
from exibir_relatorio import exibir_relatorio
from verificar_taxonomia import verificar_taxonomia

if __name__ == "__main__":
    # Solicitar ao usuário a origem e as datas de pesquisa
    origin = input("Informe a origem do normativo (ex: Receita Federal/DOU): ")
    
    # Solicitar as datas no formato DD/MM/YYYY e convertê-las
    data_inicial = input("Informe a data inicial (formato DD/MM/YYYY): ")
    data_final = input("Informe a data final (formato DD/MM/YYYY): ")

    # Converter as datas para o formato esperado (YYYY-MM-DD)
    data_inicial = datetime.strptime(data_inicial, "%d/%m/%Y").strftime("%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%d/%m/%Y").strftime("%Y-%m-%d")

    # Etapa 1: Buscar normativos pela origem e data
    normativos = buscar_normativos(origin, data_inicial, data_final)

    # Etapa 2: Verificar normativos para todos os clientes
    clientes_dict, documentos_faltantes = verificar_normativos_clientes(normativos)

    # Etapa 3: Para cada cliente com documentos faltantes, verificar a associação de taxonomia
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
