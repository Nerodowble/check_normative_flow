from pymongo import MongoClient
from bson import ObjectId
import os

# Configurações da URI e certificado
MONGO_URI = "mongodb+srv://lbprod-pri.cuho0.mongodb.net/?authMechanism=MONGODB-X509&authSource=%24external&tls=true"
CERTIFICATE_PATH = "C:\\Users\\willi\\OneDrive\\Documentos\\Acessos\\Acesso ao MongoDB\\X509-cert-4384389572589510418.pem"
DB_NAME = "legalbot_platform"

# Configurando o cliente MongoDB
client = MongoClient(MONGO_URI, tlsCertificateKeyFile=CERTIFICATE_PATH)
db = client[DB_NAME]

# Coleção 'monitor'
monitor_collection = db["monitor"]

# Consulta inicial na coleção 'monitor'
monitor_query = {
    "un_root": ObjectId("6453e226cc18ab8005e7ecb8"),
    "status": 1,
    "filters.origin": "BACEN"
}
monitor_documents = monitor_collection.find(monitor_query)

# Lista para armazenar resultados
results = []

# Iterando sobre os documentos de monitoramento
for monitor_doc in monitor_documents:
    monitor_id = monitor_doc.get("_id")
    monitor_name = monitor_doc.get("name", "N/A")
    filters = monitor_doc.get("filters", [])
    if filters:
        tag_negative = filters[0].get("tag_negative", [])
        tag_positive = filters[0].get("tag_positive", [])
    else:
        tag_negative = []
        tag_positive = []
    
    # Verificar se existem tags negativas e positivas
    negative_words = []
    for tag in tag_negative:
        for value in tag.get("value", []):
            negative_words.extend(value.get("value", []))
    
    positive_words = []
    for tag in tag_positive:
        for value in tag.get("value", []):
            positive_words.extend(value.get("value", []))

    # Acessando a coleção 'norm'
    norm_collection = db["norm"]
    norm_query = {"_id": ObjectId("6735e9ea16b60bc6050bd702")}
    norm_document = norm_collection.find_one(norm_query)

    if norm_document:
        norm_text = norm_document.get("text", "")

        # Procurando palavras negativas no texto do normativo
        for word in negative_words:
            if word.lower() in norm_text.lower():
                results.append(f"MONITORAMENTO ID: {monitor_id} - MONITORAMENTO: {monitor_name} - Palavra negativa encontrada: '{word}'")

        # Procurando palavras positivas no texto do normativo
        for word in positive_words:
            if word.lower() in norm_text.lower():
                results.append(f"MONITORAMENTO ID: {monitor_id} - MONITORAMENTO: {monitor_name} - Palavra positiva encontrada: '{word}'")

# Exibindo os resultados
for result in results:
    print(result)

# Fechar a conexão com o MongoDB
client.close()
