import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
load_dotenv()

collection_name="contexiq_testing_mode"
qdrant_api_key=os.getenv('QDRANT_API_KEY')

client = QdrantClient(
    url="https://60ef5bf6-1994-4134-a1b7-f64738daac50.europe-west3-0.gcp.cloud.qdrant.io:6333", 
    api_key=qdrant_api_key,
)

client.create_payload_index(
    collection_name=collection_name,
    field_name="user_id",
    field_schema="keyword",
)

