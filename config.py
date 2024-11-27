import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Dados de conexão a partir do .env
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
uri = f"mongodb+srv://{username}:{password}@lbprod-pri.cuho0.mongodb.net/?tls=true"

try:
    # Criar cliente MongoDB
    client = MongoClient(uri)
    print("Conexão com o MongoDB realizada com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    exit(1)

# Referência ao banco de dados e coleções
db = client['legalbot_platform']
coll_norm = db['norm']
coll_normative_un = db['normative_un']
coll_un = db['un']
coll_routing_rule = db['routing_rule']
coll_monitor = db['monitor']
