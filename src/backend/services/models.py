import os
import hashlib
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
from datetime import datetime
from .vault_encryption import encrypt_value 

load_dotenv()

# Configure Elasticsearch connection
es = Elasticsearch(os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"))

if not es.ping():
    raise Exception("Elasticsearch is not running")

# Index configurations
USERS_INDEX = "users"
MESSAGES_INDEX = "messages"

def setup_indices():
    """Create indices with proper settings and mappings"""
    try:
        # Users index
        if not es.indices.exists(index=USERS_INDEX):
            es.indices.create(
                index=USERS_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "hashed_email": {"type": "keyword"},
                            "encrypted_email": {"type": "keyword"},
                            "encrypted_phone": {"type": "keyword"},
                            "created_at": {"type": "date"}
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0  # Better for local development
                    }
                }
            )

        # Messages index
        if not es.indices.exists(index=MESSAGES_INDEX):
            es.indices.create(
                index=MESSAGES_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "encrypted_message": {"type": "text"},
                            "embeddings": {
                                "type": "dense_vector",
                                "dims": 384,
                                "index": False  # Better for your use case
                            },
                            "created_at": {"type": "date"}
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }
            )
    except Exception as e:
        print(f"Index setup error: {e}")
        raise

def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()

def user_email_lookup(hashed_email: str) -> str | None:
    try:
        response = es.search(
            index=USERS_INDEX,
            body={
                "query": {"term": {"hashed_email": hashed_email}},
                "_source": ["id"]
            },
            size=1
        )
        if response["hits"]["hits"]:
            return response["hits"]["hits"][0]["_source"]["id"]
        return None
    except Exception as e:
        print(f"User lookup error: {e}")
        return None

def store_user_email(hashed_email: str, email: str) -> str:
    try:
        user_id = hashlib.sha1(f"{email}{datetime.now()}".encode()).hexdigest()
        encrypted_email = encrypt_value(email, "user-email")
        
        es.index(
            index=USERS_INDEX,
            id=user_id,
            document={
                "id": user_id,
                "hashed_email": hashed_email,
                "encrypted_email": encrypted_email,
                "encrypted_phone": "",
                "created_at": datetime.utcnow()
            }
        )
        return user_id
    except Exception as e:
        print(f"User storage error: {e}")
        raise

def store_user_phone(phone_number: str, user_id: str):
    try:
        encrypted_phone = encrypt_value(phone_number, "user-phone")
        
        update_body = {
            "doc": {
                "encrypted_phone": encrypted_phone
            }
        }
        
        es.update(index=USERS_INDEX, id=user_id, body=update_body)
        print(f"Phone number added for user {user_id}")
    except Exception as e:
        print(f"Error storing user phone: {e}")
        raise

def store_messages(batch: list[tuple]) -> bool:
    """Store messages in bulk with error handling"""
    if not batch:
        return False
        
    actions = [
        {
            "_index": MESSAGES_INDEX,
            "_source": {
                "user_id": user_id,
                "encrypted_message": encrypted_message,
                "embeddings": embeddings_list,
                "created_at": datetime.utcnow().isoformat()
            }
        }
        for user_id, encrypted_message, embeddings_list in batch
    ]
    
    try:
        helpers.bulk(es, actions)
        return True
    except Exception as e:
        print(f"Bulk insert error: {e}")
        return False
