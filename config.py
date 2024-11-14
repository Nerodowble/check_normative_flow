import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

# Configurações específicas
DB_NAME = 'legalbot_platform'
UN_ROOT_AUTOSERVICE = "6036a15d57e70eceeadc2b55"  # ID específico do cliente AUTOSERVICE

# Referências para coleções
db = client[DB_NAME]
coll_norm = db['norm']
coll_normative_un = db['normative_un']
coll_un = db['un']
coll_routing_rule = db['routing_rule']  # Adicionado para acessar a coleção de regras de roteamento
coll_monitor = db['monitor']
