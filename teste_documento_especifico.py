import json
from bson import ObjectId
from config import coll_monitor  # Importar a coleção diretamente
from analisar_associados import analisar_associacao_documento
from listar_regras_cliente import json_converter

def teste_especifico():
    """
    Script de teste para depurar a análise de um único documento.
    Primeiro, ele exibe a estrutura de um monitor específico para análise.
    """
    # --- Parâmetros de Teste ---
    # Usando um ID de documento diferente para testar o fluxo.
    documento_id_teste = "68903f0bdfe9452a5be53091"
    cliente_id_teste = "62aa15ba5ccad9aa706a2f4d"
    # -------------------------

    print("=" * 60)
    print(f"Iniciando teste de análise para o documento ID: {documento_id_teste}")
    print("=" * 60)

    print(f"Cliente ID: {cliente_id_teste}")
    print("=" * 60)

    # Chama a função de análise diretamente
    resultado_analise = analisar_associacao_documento(documento_id_teste, cliente_id_teste)

    print("\n--- Resultado da Análise ---")
    print(json.dumps(resultado_analise, indent=4, ensure_ascii=False, default=json_converter))
    print("--- Fim do Resultado ---\n")

if __name__ == "__main__":
    teste_especifico()