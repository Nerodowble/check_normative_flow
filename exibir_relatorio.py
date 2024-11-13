# exibir_relatorio.py

def exibir_relatorio(clientes_dict, documentos_faltantes):
    """Exibir o relatório com detalhes de todos os clientes e documentos faltantes, incluindo taxonomias associadas."""
    print("\n===== Relatório de Normativos e Clientes =====")
    for cliente, dados in clientes_dict.items():
        print(f"\nCliente: {cliente}")
        print(f"Quantidade de documentos: {dados['total_documentos']}")
        print(f"Quantidade de documentos no Pré-Envio: {dados['pre_envio']}")
        print(f"Quantidade de documentos no Pós-Envio (Caixa de Entrada): {dados['pos_envio_caixa_entrada']}")
        print(f"Quantidade de documentos no Pós-Envio (Sem Caixa de Entrada): {dados['pos_envio_sem_caixa_entrada']}")
        print(f"Quantidade de documentos na Busca: {dados['busca']}")
        print(f"Quantidade de documentos que vieram do Monitor: {dados['monitor']}")
        print(f"Quantidade de documentos que não vieram do Monitor: {dados['nao_monitor']}")

        # Verificar documentos faltantes específicos do cliente
        if dados["documentos_faltantes"]:
            print("\nDocumentos faltantes para este cliente:")
            for doc in dados["documentos_faltantes"]:
                print(f"ID: {doc['_id']}")
        else:
            print("Nenhum documento faltante para este cliente.")

        # Exibir informações de taxonomias associadas
        if "taxonomias_associadas" in dados:
            print("\nTaxonomias Associadas para os Normativos deste Cliente:")
            for taxonomia in dados["taxonomias_associadas"]:
                print(f"Normativo ID: {taxonomia['normativo_id']}")
                print(f"  - Taxonomia: {taxonomia['taxonomia']}")
                print(f"  - Descrição: {taxonomia['descricao']}")
                print(f"  - Associado ao Cliente: {'Sim' if taxonomia['associado_ao_cliente'] else 'Não'}")
        else:
            print("Nenhuma taxonomia associada para os normativos deste cliente.")

        print("-----")

    if documentos_faltantes:
        print("\n===== Documentos Faltantes Gerais =====")
        for doc in documentos_faltantes:
            print(f"ID: {doc['_id']}, Título: {doc['title']}, Tipo: {doc['type']}, Assunto: {doc['subject']}, Link: {doc['link']}")
        print("===== Fim dos Documentos Faltantes =====")
    else:
        print("Nenhum documento faltante.")
    print("===== Fim do Relatório =====")
