# app/db/cosmos_db.py
from azure.cosmos import CosmosClient, PartitionKey
from flask import current_app

def get_cosmos_client():
    """Retorna o CosmosClient configurado."""
    endpoint = current_app.config["COSMOS_ENDPOINT"]
    key = current_app.config["COSMOS_KEY"]
    return CosmosClient(endpoint, credential=key)

def get_cosmos_container():
    """Retorna o container que vamos usar para produtos."""
    client = get_cosmos_client()
    database_name = current_app.config["COSMOS_DATABASE_NAME"]
    container_name = current_app.config["COSMOS_CONTAINER_NAME"]

    # Recupera (ou cria) o banco
    database = client.get_database_client(database_name)

    # Recupera (ou cria) o container
    container = database.get_container_client(container_name)

    return container
