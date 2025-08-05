# Documentação Técnica: Ferramenta de Auditoria de Normativos

## 1. Intuito e Finalidade

Esta ferramenta é um sistema de **auditoria e diagnóstico de ponta a ponta**, projetado para analisar a integridade da entrega de documentos normativos a um cliente específico. Sua finalidade é responder a três perguntas de negócio cruciais com precisão técnica:

1.  **O Que Foi Entregue?** Quantificar e categorizar todos os normativos associados a um cliente dentro de um escopo definido (origem e data).
2.  **O Que Não Foi Entregue?** Identificar quais normativos, dentro do mesmo escopo, não foram associados ao cliente.
3.  **Qual a Causa Raiz?** Para cada documento (entregue ou não), determinar o motivo técnico exato da sua associação ou ausência dela, validando a lógica de captura do sistema de produção.

A ferramenta opera como um sistema de análise post-mortem, inspecionando o estado do banco de dados para fornecer uma trilha de auditoria completa e compreensível.

---

## 2. Arquitetura e Módulos Principais

O projeto é composto por uma série de módulos Python orquestrados pelo script `main.py`. Cada módulo tem uma responsabilidade específica no processo de auditoria.

-   **`main.py`**: Orquestrador principal. Coleta os parâmetros de entrada (cliente, origem, data) e coordena a execução sequencial dos módulos de análise e relatório.
-   **`buscar_normativos.py`**: Responsável por consultar a coleção `norm` e "pescar" o conjunto inicial de documentos que serve como base para a auditoria.
-   **`verificar_normativos_clientes.py`**: Realiza a primeira grande análise. Compara o conjunto de normativos pescados com os registros de associação (`normative_un`) para separar os documentos em duas categorias principais: **associados** e **faltantes**. Também realiza a contagem de status (Pré-Envio, Pós-Envio, etc.).
-   **`analisar_associados.py`**: Atua como um **orquestrador de diagnóstico** para os documentos que *foram* associados. Ele determina qual mecanismo de captura foi usado e chama o módulo de análise apropriado.
-   **`verificar_monitoramento.py`**: Contém o **motor de análise** para o mecanismo de Monitoramento Direto. Sua lógica simula a correspondência de palavras-chave (tags) para provar como uma regra de monitoramento foi acionada.
-   **`analisar_taxonomia.py`**: Contém o **motor de análise** para o mecanismo de Taxonomia e Roteamento. Sua lógica simula a busca por uma `routing_rule` que corresponda à classificação (`class`/`subclass`) de um documento.
-   **`relatorio_avancado.py`**: Módulo final que gera um relatório detalhado no terminal, focando na análise de causa raiz para os documentos em Pós-Envio.
-   **`exibir_relatorio.py`**: Gera o relatório de status inicial no terminal, mostrando as contagens e a lista de documentos faltantes.

---

## 3. Fluxo de Execução e Análise Técnica

A execução do `main.py` dispara um fluxo sequencial de sete etapas, culminando em um diagnóstico completo no terminal.

### Etapa 1: Definição do Escopo da Auditoria
-   **O que acontece:** O usuário fornece o `cliente_id`, `origem` e o `range de datas`.
-   **Intuito:** Definir o universo exato de normativos que serão auditados.

### Etapa 2: Coleta de Dados Brutos (`buscar_normativos`)
-   **O que acontece:** O sistema consulta a coleção `norm` e recupera todos os documentos que correspondem à `origem` e `data` especificadas.
-   **Finalização:** O resultado é uma lista de documentos que representa o "universo total" de normativos publicados.

### Etapa 3: Verificação de Associações (`verificar_normativos_cliente`)
-   **O que acontece:** O sistema itera sobre o universo total de normativos e, para cada um, verifica se existe um registro correspondente na coleção `normative_un` para o cliente em questão.
-   **Finalização:** A etapa termina com duas listas primárias:
    1.  `documentos_associados`: Contém os IDs dos normativos que o cliente recebeu.
    2.  `documentos_faltantes`: Contém os detalhes dos normativos que o cliente **não** recebeu.

### Etapa 4: Relatório de Status (`exibir_relatorio`)
-   **O que acontece:** O primeiro grande relatório é impresso no terminal.
-   **Intuito:** Fornecer uma visão geral quantitativa da auditoria.
-   **Finalização:** O log exibe:
    -   As contagens de documentos associados, quebradas por status (`Pré-Envio`, `Pós-Envio`, etc.).
    -   A lista detalhada de todos os `documentos_faltantes`.

### Etapa 5: Análise de Causa Raiz dos Faltantes (`verificar_monitoramento`)
-   **O que acontece:** O sistema analisa a lista de `documentos_faltantes`, simulando as regras de monitoramento do cliente contra cada um.
-   **Intuito:** Responder à pergunta: "O sistema errou ao não capturar estes documentos, ou a decisão foi correta?".
-   **Finalização:** Um arquivo `relatorio_monitoramento_...json` é gerado, contendo o laudo técnico que prova, para cada documento faltante, por que ele não correspondeu às regras de captura do cliente.

### Etapa 6: Análise de Causa Raiz dos Associados (`executar_analise_associados`)
-   **O que acontece:** O sistema analisa a lista de `documentos_associados`. O orquestrador `analisar_associados.py` examina cada associação para determinar o mecanismo de captura.
-   **Intuito:** Responder à pergunta: "**Qual regra específica causou esta associação?**".
-   **Finalização:** Um arquivo `relatorio_analise_associados_...json` é gerado. Este é o relatório de diagnóstico principal, que detalha, para cada documento, a causa exata da sua associação, identificando um dos três possíveis mecanismos:
    1.  **Monitoramento:** A prova são as tags encontradas.
    2.  **Taxonomia/Roteamento:** A prova é a `class`/`subclass` que acionou uma `routing_rule`.
    3.  **Encaminhamento Manual:** A prova é a detecção de uma ação de encaminhamento (`forwarded_at`) na ausência de uma causa automática.

### Etapa 7: Relatório Avançado de Pós-Envio (`relatorio_avancado`)
-   **O que acontece:** Como etapa final, o sistema foca nos documentos que já estão no estágio "Pós-Envio" (para a `origem` e `cliente` especificados) e gera um relatório detalhado diretamente no terminal.
-   **Intuito:** Fornecer uma prova de auditoria imediata e de fácil leitura para os documentos mais críticos (aqueles que já foram finalizados), sem a necessidade de abrir arquivos JSON.
-   **Finalização:** O log do terminal exibe, para cada documento em Pós-Envio, o título e a prova definitiva de sua associação, consolidando toda a análise realizada.
