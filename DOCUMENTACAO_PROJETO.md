# Documentação de Intenção do Projeto: Verificador de Normativos

## Para que serve este projeto? (A Visão Geral)

Imagine que grandes empresas, como bancos, precisam seguir milhares de regras e leis (chamadas de "normativos") que são publicadas todos os dias por órgãos do governo (como o Banco Central, ANATEL, Receita Federal, etc.). Perder uma única regra importante pode resultar em multas milionárias e grandes problemas legais.

Este projeto funciona como um **sistema de auditoria completo**.

Seu objetivo é fazer uma verificação 360° da "saúde" da entrega de normativos para um cliente específico, respondendo a três perguntas cruciais:
1.  O que o cliente já tem?
2.  O que ele não tem (e deveria ter)?
3.  Por que ele não tem?

---

## O Fluxo Completo: Explicando a Saída do Terminal

Vamos usar a execução que você realizou como um exemplo prático para entender cada passo do processo.

### Etapa 1: Definindo o Alvo da Auditoria
```
Você quer informar o ID ou o Nome do cliente? ...
Informe o ID do cliente: 62aa15ba5ccad9aa706a2f4d
Informe a origem do normativo ... ANATEL/DOU
Informe a data inicial ... 04/08/2025
```
**O que significa:** Primeiro, dizemos ao sistema quem e o que queremos auditar. Neste caso, definimos o alvo como o cliente "Banco Bradesco S.A." e a fonte das regras como "ANATEL/DOU" para o dia 4 de agosto de 2025.

---

### Etapa 2: A "Pesca" e a Verificação da Taxonomia
```
Buscando normativos para origem 'ANATEL/DOU'... Encontrados 26 normativos.
Status da Taxonomia Automática para o Cliente 'None': {'titulo': '', 'descricao': ''...}
```
**O que significa:**
1.  **A Pesca:** O sistema vai até a fonte (ANATEL/DOU) e "pesca" todas as 26 regras publicadas na data informada.
2.  **Taxonomia Automática:** Em seguida, ele faz uma verificação rápida: "Este cliente tem alguma regra de classificação automática já configurada?". No seu caso, ele encontrou uma regra, mas ela estava sem título e descrição (o primeiro ponto que investigamos). Isso é parte da auditoria: verificar as configurações do cliente.

---

### Etapa 3: A Verificação Principal e o Relatório de Status
```
Iniciando verificação de normativos para o cliente...
===== Relatório de Normativos e Clientes =====
Cliente: Banco Bradesco S.A.
Quantidade de documentos: 11
...
Documentos faltantes para este cliente:
ID: 68903f0bdfe9452a5be53118
... (lista com 15 IDs)
```
**O que significa:** Esta é a etapa central. O sistema pega as 26 regras "pescadas" e as compara com os registros do cliente no nosso banco de dados (`normative_un`).
*   Ele descobre que **11 documentos** já estão corretamente associados ao Bradesco.
*   Ele descobre que **15 documentos** não têm nenhuma associação com o Bradesco. Estes são classificados como **"faltantes"**.
*   O sistema então exibe o relatório, mostrando o resumo (11 recebidos) e a lista de IDs dos 15 "faltantes".

---

### Etapa 4: A Investigação dos Faltantes (O Monitoramento)
```
Iniciando verificação de monitoramento para o cliente com ID '62aa15ba5ccad9aa706a2f4d'...
Verificação de monitoramento concluída e salva em JSON.
```
**O que significa:** Agora, o processo foca nos 15 documentos "faltantes". A pergunta a ser respondida é: "O fato de esses 15 documentos não estarem associados ao Bradesco foi um **erro** do nosso sistema de captura ou foi a **decisão correta**?".

Para isso, ele inicia a auditoria de monitoramento:
*   Ele pega cada um dos 15 documentos.
*   Compara o conteúdo deles com as "regras de monitoramento" (as palavras-chave de interesse) do Bradesco.
*   O resultado dessa investigação profunda é salvo no arquivo `relatorio_monitoramento_...json`. Este arquivo é o laudo técnico que prova, para cada documento, por que a decisão de não capturá-lo foi (neste caso) a correta.

---

## O que este projeto agrega? (O Valor para o Negócio)

Este fluxo completo oferece uma visão 360° da nossa operação para um cliente:

1.  **Visão do Presente:** Mostra o que o cliente já tem e como suas regras automáticas estão configuradas.
2.  **Identificação de Lacunas:** Aponta exatamente quais documentos publicados não foram associados ao cliente.
3.  **Diagnóstico de Causa Raiz:** Vai além de apenas apontar a lacuna e investiga o "porquê", garantindo que nosso sistema de captura está tomando as decisões corretas com base nas regras de negócio do cliente.

Em suma, este projeto é uma ferramenta poderosa de **auditoria, diagnóstico e garantia de qualidade**, assegurando a integridade e a confiança do nosso serviço.
