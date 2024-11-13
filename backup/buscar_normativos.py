from datetime import datetime, timedelta
from config import coll_norm

def buscar_normativos(origin, data_inicial, data_final):
    """Buscar normativos pela origem e intervalo de data na coleção 'norm'."""
    print(f"Buscando normativos para origem '{origin}' entre {data_inicial} e {data_final}...")

    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")

    # Ajustar data_final para o final do dia (23:59:59) caso seja igual a data_inicial
    if data_inicial == data_final:
        data_final = data_final + timedelta(days=1) - timedelta(seconds=1)
    else:
        # Incluir o próximo dia se o intervalo abranger múltiplos dias
        data_final = data_final + timedelta(days=1)

    # Consulta no MongoDB
    normativos = list(coll_norm.find({
        "origin": origin,
        "issuance_date": {"$gte": data_inicial, "$lt": data_final}
    }))
    print(f"Encontrados {len(normativos)} normativos para origem '{origin}'.")
    return normativos
