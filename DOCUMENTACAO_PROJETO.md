# Documentação Técnica: Ferramenta de Auditoria de Normativos v2.0

## 1. Intuito e Finalidade

Esta ferramenta é um sistema de **auditoria e diagnóstico de ponta a ponta**, projetado para analisar a integridade da entrega de documentos normativos a um cliente específico. Sua finalidade é responder a três perguntas de negócio cruciais com precisão técnica:

1.  **O Que Foi Entregue?** Quantificar e categorizar todos os normativos associados a um cliente dentro de um escopo definido.
2.  **O Que Não Foi Entregue?** Identificar quais normativos, dentro do mesmo escopo, não foram associados ao cliente.
3.  **Qual a Causa Raiz?** Para cada documento (entregue ou não), determinar o motivo técnico exato da sua associação ou ausência dela, validando a lógica de captura do sistema de produção.

A ferramenta pode operar em dois modos: **Análise Específica** (focada em uma única origem e data) ou **Análise Completa** (executando a auditoria para todas as origens associadas a um cliente para um período de tempo).

---

## 2. Arquitetura e Módulos Principais

O projeto é composto por uma série de módulos Python orquestrados pelo script `main.py`.

-   **`main.py`**: Orquestrador principal. Coleta os parâmetros de entrada (cliente, datas) e o modo de operação (origem específica ou todas). Gerencia o loop de análise e agrega os resultados em um relatório final.
-   **`obter_origens_cliente.py`**: Módulo utilitário que consulta o banco de dados para extrair uma lista única de todas as origens de normativos já associadas a um cliente.
-   **`buscar_normativos.py`**: Consulta a coleção `norm` para "pescar" o conjunto inicial de documentos para uma origem e data específicas.
-   **`verificar_normativos_clientes.py`**: Realiza a análise inicial, separando os normativos em **associados** e **faltantes** e contando os status (Pré-Envio, Pós-Envio, etc.).
-   **`analisar_associados.py`**: Atua como um **orquestrador de diagnóstico** para os documentos associados, determinando o mecanismo de captura e chamando o motor de análise apropriado.
-   **`verificar_monitoramento.py`**: Contém o **motor de análise** para o mecanismo de **Monitoramento**, simulando a correspondência de palavras-chave.
-   **`analisar_taxonomia.py`**: Contém o **motor de análise** para os mecanismos de **Taxonomia/Roteamento** e **Encaminhamento Manual**.
-   **`listar_regras_cliente.py`**: Gera um arquivo JSON (`regras_cliente_...json`) que consolida os dois tipos de regras de negócio ativas para um cliente:
    -   **Regras de Monitoramento:** Captura por palavras-chave, geralmente gerenciada pelo cliente.
    -   **Regras de Roteamento:** Conecta a classificação da taxonomia (criada pela Legalbot) ao cliente.

---

## 3. Fluxo de Execução e Análise Técnica

A execução do `main.py` inicia um fluxo de auditoria robusto e flexível.

### Etapa 1: Definição do Escopo da Auditoria
-   **O que acontece:** O usuário fornece o `cliente_id` e o `range de datas`. Em seguida, escolhe o modo de operação:
    -   **Origem Específica:** O usuário informa uma única origem para a análise.
    -   **Todas as Origens:** O sistema chama `obter_todas_origens` para buscar dinamicamente todas as origens do cliente.
-   **Intuito:** Permitir tanto uma análise rápida e focada quanto uma auditoria completa e automatizada.

### Etapa 2: Loop de Análise por Origem
-   **O que acontece:** O `main.py` itera sobre a lista de origens a serem analisadas. Para cada origem, ele executa um sub-processo de análise completo e silencioso.
-   **Intuito:** Processar de forma sistemática e eficiente um grande volume de análises sem poluir o terminal.
-   **Saída do Terminal:** Apenas uma linha de progresso é exibida para cada origem (ex: `Analisando origem: AGU/DOU...`).

### Etapa 3: Sub-processo de Análise (Para Cada Origem)
Dentro do loop, para cada origem, as seguintes análises são realizadas em memória:
1.  **Busca de Normativos:** Encontra todos os normativos para a origem e data.
2.  **Verificação de Associações:** Separa os documentos em `associados` e `faltantes`.
3.  **Análise de Causa Raiz (Faltantes):** Simula as regras de monitoramento para entender por que os documentos faltantes não foram capturados.
4.  **Análise de Causa Raiz (Associados):** O orquestrador `analisar_associados.py` determina, para cada documento, o mecanismo de captura:
    -   **Monitoramento:** A prova são as tags encontradas.
    -   **Taxonomia/Roteamento:** A prova é a `class`/`subclass` que acionou uma `routing_rule`.
    -   **Encaminhamento Manual:** A prova é a detecção de uma ação de encaminhamento (`forwarded_at`).

### Etapa 4: Agregação e Relatório Final
-   **O que acontece:** Os resultados de cada sub-processo de análise são agregados em uma única estrutura de dados.
-   **Intuito:** Consolidar todas as informações da auditoria em um único local.
-   **Finalização:** Ao final do loop, um único arquivo JSON é gerado: `relatorio_completo_[ID_CLIENTE]_[DATA].json`. Este arquivo contém a análise detalhada para cada origem processada, servindo como o artefato final e completo da auditoria.
