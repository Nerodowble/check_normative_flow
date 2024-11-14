def exibir_relatorio(clientes_dict, documentos_faltantes):
    """Exibe o relatório com detalhes de todos os clientes e documentos faltantes, incluindo taxonomias associadas."""
    
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
        
        # Exibir status de taxonomia automática
        print(f"Taxonomia automática associada: {dados['taxonomia_auto_serviço']}")

        # Verificar documentos faltantes específicos do cliente
        if dados["documentos_faltantes"]:
            print("\nDocumentos faltantes para este cliente:")
            for doc in dados["documentos_faltantes"]:
                print(f"ID: {doc['_id']}")
        else:
            print("Nenhum documento faltante para este cliente.")

        # Exibir informações de taxonomias automáticas associadas
        if isinstance(dados["taxonomia_auto_serviço"], dict):
            print("\nTaxonomias Automáticas para os Normativos deste Cliente:")
            print(f"Título: {dados['taxonomia_auto_serviço']['titulo']}")
            print(f"Descrição: {dados['taxonomia_auto_serviço']['descricao']}")
            print("Regras:")
            for regra in dados["taxonomia_auto_serviço"]["regras"]:
                print(f"  - Chave: {regra['key']}, Operador: {regra['operator']}, Valores: {regra['values']}")
        else:
            print("Nenhuma taxonomia associada para os normativos deste cliente.")

        print("-----")

    # Exibição de documentos faltantes gerais
    if documentos_faltantes:
        print("\n===== Documentos Faltantes Gerais =====")
        for doc in documentos_faltantes:
            print(f"ID: {doc['_id']}, Título: {doc['title']}, Tipo: {doc['type']}, Assunto: {doc['subject']}, Link: {doc['link']}")
        print("===== Fim dos Documentos Faltantes =====")
    else:
        print("Nenhum documento faltante.")
    
    print("===== Fim do Relatório =====")
