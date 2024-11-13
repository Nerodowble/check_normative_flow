# Lógica de Verificação de Taxonomia

Este documento descreve o fluxo estruturado para verificação de taxonomias aplicadas a normativos, garantindo que sejam capturados corretamente. Abaixo está uma visão geral de cada etapa.

## 1. Definir Parâmetros de Busca Inicial

- **Entrada**:
  - Origem dos normativos (ex.: "BACEN").
  - Intervalo de datas para busca dos normativos (ex.: data inicial "2024-11-12", data final "2024-11-12").

## 2. Buscar Normativos na Coleção `coll_norm`

- **Ação**: Consultar a coleção `coll_norm` para encontrar normativos que correspondam à origem e ao intervalo de datas fornecidos.
- **Saída Esperada**: Lista de normativos que atendem aos critérios (ex.: 3 normativos encontrados para "BACEN" na data especificada).

## 3. Verificar Normativos para Clientes na Coleção `coll_normative_un`

- **Para cada normativo encontrado**:
  - Verificar se ele está associado a clientes específicos na coleção `coll_normative_un`.
  - **Campos utilizados**: `un_id` (ID do cliente) e `norm_id` (ID do normativo).
- **Saída Esperada**: Lista de clientes associados a cada normativo, indicando quais clientes devem receber o normativo.

## 4. Iterar pelos Clientes e Verificar Taxonomias

- **Para cada cliente associado ao normativo**:
  - Verificar se o normativo foi capturado com base na taxonomia do cliente.
  - **Detalhes**:
    - Cada cliente possui regras de taxonomia específicas (`routing_rule`), que especificam `tags`, `themes`, e `origins`.
    - Filtrar apenas as `routing_rule` com `deleted_by: null` (indica taxonomias ativas).

## 5. Verificação de Taxonomia com `routing_rule`

- **Para cada regra de taxonomia (`routing_rule`) associada ao cliente**:
  - **Verificar as seguintes condições**:
    - **Tags Positivas (`ptags`)**: Verificar se as tags do normativo correspondem às `ptags` da regra.
    - **Tags Negativas (`ntags`)**: Assegurar que o normativo **não contenha** tags que correspondam às `ntags` da regra.
    - **Tema (`themes`)**: Verificar se o tema do normativo está permitido conforme a regra.
  - **Ação**: Se as `ptags` estiverem presentes e as `ntags` não forem encontradas, a regra de taxonomia captura o normativo.
  - **Saída**: Identificar se o normativo foi capturado pela taxonomia aplicada.

## 6. Registrar o Resultado da Verificação de Taxonomia

- **Critério de Captura**:
  - Se o normativo atender a todas as condições de uma `routing_rule`, ele é considerado capturado pela taxonomia do cliente.
  - Caso contrário, o normativo será marcado como **não capturado** pela taxonomia.
- **Informação de Saída**:
  - Para cada normativo, especificar se foi capturado pela taxonomia do cliente ou se houve uma falha de captura.

## 7. Gerar o Relatório Final

Consolidar os resultados em um relatório detalhado.

- **Para cada cliente**:
  - Listar todos os normativos verificados.
  - Identificar normativos capturados e não capturados pela taxonomia.
  - Exibir detalhes como:
    - ID do normativo
    - Título
    - Tags correspondentes
    - Tema
    - Status de captura pela taxonomia


## 8. Resumo das Etapas da Lógica de Verificação de Taxonomia

- Definir parâmetros de busca inicial (origem, datas).
- Buscar normativos na coll_norm de acordo com os parâmetros.
- Verificar normativos na coll_normative_un para identificar clientes associados.
- Iterar pelos clientes e verificar taxonomias.
- Verificar taxonomia com base nas routing_rule ativas.
- Registrar e consolidar resultados de capturas de taxonomia.
- Gerar o relatório final com detalhes sobre captura e falhas de taxonomia para cada cliente.

### Exemplo de Saída Esperada no Relatório

```plaintext
===== Relatório de Normativos e Clientes =====

Cliente: Legalbot - Vendas
Quantidade de documentos verificados: 3

Taxonomias Capturadas:
- Normativo ID: 123abc, Taxonomia: "Compliance Bancário", Status: Capturado
- Normativo ID: 456def, Taxonomia: "Segurança da Informação", Status: Capturado

Taxonomias Não Capturadas:
- Normativo ID: 789ghi, Motivo: Taxonomia "Compliance Bancário" não capturou este normativo.




