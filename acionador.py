# acionador.py

import re
from datetime import datetime
from buscar_normativos import buscar_normativos
from verificar_normativos_clientes import verificar_normativos_clientes
from exibir_relatorio import exibir_relatorio
from verificar_taxonomia import verificar_taxonomia
from config import coll_un  # Importa a coleção 'un' onde os dados do cliente estão armazenados

def main(cliente_id=None, cliente_nome=None, origem=None, data_inicio=None, data_fim=None):
    # Converter datas para o formato esperado (YYYY-MM-DD)
    data_inicio_fmt = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
    data_fim_fmt = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")

    # Obter ID do cliente pelo nome se o ID não for fornecido
    if not cliente_id and cliente_nome:
        # Usar expressão regular para buscar o nome do cliente, insensível a maiúsculas/minúsculas
        cliente = coll_un.find_one({"name": {"$regex": f"^{re.escape(cliente_nome)}$", "$options": "i"}})
        if cliente:
            cliente_id = str(cliente["_id"])
            print(f"Cliente '{cliente_nome}' encontrado com ID: {cliente_id}")
        else:
            print(f"Cliente com o nome '{cliente_nome}' não encontrado.")
            return

    # Verificar se o ID do cliente foi encontrado ou informado
    if not cliente_id:
        print("É necessário fornecer um ID do cliente ou nome válido.")
        return

    # Etapa 1: Buscar normativos pela origem e data
    normativos = buscar_normativos(origem, data_inicio_fmt, data_fim_fmt)

    # Filtrar normativos específicos para o cliente
    normativos_filtrados = [n for n in normativos if n.get("client_id") == cliente_id]

    # Etapa 2: Verificar normativos para o cliente
    clientes_dict, documentos_faltantes = verificar_normativos_clientes(normativos_filtrados)

    # Etapa 3: Verificação de taxonomia para documentos faltantes
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
    # Solicitar ao usuário os dados necessários
    cliente_id = input("Informe o ID do cliente (ou pressione Enter para buscar pelo nome): ")
    cliente_nome = input("Informe o nome do cliente (caso não forneça o ID): ") if not cliente_id else None
    origem = input("Informe a origem (ex: BACEN): ")
    data_inicio = input("Informe a data de início (formato DD/MM/YYYY): ")
    data_fim = input("Informe a data de fim (formato DD/MM/YYYY): ")

    # Executa o processo principal
    main(cliente_id, cliente_nome, origem, data_inicio, data_fim)
