Documentação de Verificação de Monitoramento e Normativos
Visão Geral
Este projeto realiza o monitoramento e verificação de normativos com base em regras configuráveis para determinar se documentos específicos devem ser capturados. A verificação utiliza tags positivas e tags negativas para filtrar documentos relevantes. O processo inclui o monitoramento de origens específicas e a execução de verificações detalhadas baseadas nas tags, visando facilitar a conformidade regulatória.

Estrutura do Projeto
Principais Scripts
main.py

Script principal de execução do fluxo de verificação de normativos.
Solicita os dados do cliente (ID ou nome), origem e intervalo de datas.
Executa a verificação dos normativos e chama a função de monitoramento.
verificar_monitoramento.py

Executa a verificação de monitoramento para documentos.
Inclui funções para contar tags positivas e negativas em textos de normativos.
Gera um relatório detalhado de verificação, indicando o motivo de captura ou não.
exibir_relatorio.py

Exibe o relatório final de verificação no terminal.
buscar_normativos.py

Busca normativos específicos com base nos parâmetros fornecidos pelo usuário.
verificar_taxonomia.py

Verifica a associação de taxonomia com documentos faltantes.
Estrutura da Coleção monitor
Cada monitor possui os seguintes campos:

un_root: ID do cliente para o qual o monitor foi criado.
filters: Lista de filtros que definem origens, tags positivas e negativas.
origin: Define as origens específicas dos normativos.
tag_positive: Lista de grupos de tags positivas que o monitor deve capturar.
tag_negative: Lista de grupos de tags negativas para exclusão de documentos.
Descrição das Funções Principais
Função obter_cliente_id
python
Copiar código
def obter_cliente_id(cliente_id=None, cliente_nome=None):
Objetivo: Retorna o ID do cliente com base no ID fornecido ou no nome utilizando regex.
Parâmetros:
cliente_id: ID único do cliente (ObjectId do MongoDB).
cliente_nome: Nome do cliente para busca com regex.
Retorno: ID do cliente, ou None se o cliente não for encontrado.
Função buscar_monitores
python
Copiar código
def buscar_monitores(cliente_id):
Objetivo: Busca todos os monitores configurados para um cliente específico.
Parâmetros:
cliente_id: ID do cliente.
Retorno: Lista de documentos de monitoramento associados ao cliente.
Função contar_ocorrencias_tags
python
Copiar código
def contar_ocorrencias_tags(texto, tags):
Objetivo: Conta as ocorrências de cada tag em um texto e retorna um dicionário com os resultados.
Parâmetros:
texto: Texto do normativo.
tags: Lista de tags a serem verificadas.
Retorno: Dicionário contendo o número de ocorrências de cada tag.
Função verificar_documento_por_monitor
python
Copiar código
def verificar_documento_por_monitor(documento, monitor):
Objetivo: Avalia se um documento atende aos critérios de captura de um monitor específico.
Parâmetros:
documento: Dados do documento/normativo.
monitor: Configurações do monitor a serem aplicadas.
Retorno: Dicionário detalhado contendo:
captura_esperada: Booleano indicando se o documento deveria ser capturado.
num_tags_positivas_encontradas: Número de tags positivas encontradas.
num_tags_negativas_encontradas: Número de tags negativas encontradas.
motivo: Motivo pelo qual o documento não foi capturado, se aplicável.
Função verificar_monitoramento
python
Copiar código
def verificar_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
Objetivo: Realiza a verificação de monitoramento para documentos faltantes com base nas regras dos monitores configurados para o cliente.
Parâmetros:
cliente_id: ID do cliente.
origem: Origem do normativo.
data_inicial e data_final: Intervalo de datas.
documentos_faltantes: Lista de documentos que não foram capturados.
Processo:
Itera sobre os documentos faltantes e monitores, verificando se o documento atende aos critérios de captura do monitor.
Função executar_verificacao_monitoramento
python
Copiar código
def executar_verificacao_monitoramento(cliente_id, origem, data_inicial, data_final, documentos_faltantes):
Objetivo: Função principal para executar a verificação de monitoramento a partir do main.py.
Processo Geral de Verificação
Entrada de Dados:

O main.py solicita ID ou nome do cliente, origem e intervalo de datas.
Identifica o cliente por ID ou nome utilizando regex.
Busca de Normativos:

Executa buscar_normativos para localizar normativos que correspondem aos critérios.
Verificação de Normativos para o Cliente:

verificar_normativos_cliente é chamado para verificar os normativos e documentos faltantes para o cliente.
Verificação de Monitoramento:

A função verificar_monitoramento analisa os documentos faltantes de acordo com os monitores configurados.
Contagem de Tags:
tags_positivas e tags_negativas são verificadas no texto do documento.
Gera relatórios de quantas tags foram encontradas, incluindo listas detalhadas de ocorrências.
Geração de Relatório Final:

O relatório final é salvo como JSON, indicando o motivo da captura ou exclusão de cada documento, com porcentagens detalhadas de tags positivas e negativas.
Este documento fornece uma visão completa para auxiliar futuros desenvolvedores na compreensão e manutenção do fluxo de verificação e monitoramento de normativos.

