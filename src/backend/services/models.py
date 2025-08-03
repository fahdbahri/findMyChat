import os
import hashlib
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
from datetime import datetime
from .vault_encryption import encrypt_value

load_dotenv()

# Configure Elasticsearch connection
es = Elasticsearch(os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200"))

if not es.ping():
    raise Exception("Elasticsearch is not running")

# Index configurations
users_index = "users"
messages_index = "messages"

def setup_indices():
    """Create indices if they don't exist"""
    try:
        if not es.indices.exists(index=users_index):
            user_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "hashed_email": {"type": "keyword"},
                        "encrypted_email": {"type": "keyword"},
                        "encrypted_phone": {"type": "keyword"},
                        "created_at": {"type": "date"}
                    }
                }
            }
            es.indices.create(index=users_index, body=user_mapping)
            print(f"Created index {users_index}")

        if not es.indices.exists(index=messages_index):
            message_mapping = {
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "encrypted_message": {"type": "text"},
                        "embeddings": {"type": "dense_vector", "dims": 768},
                        "created_at": {"type": "date"}
                    }
                }
            }
            es.indices.create(index=messages_index, body=message_mapping)
            print(f"Created index {messages_index}")
    except Exception as e:
        print(f"Error setting up indices: {e}")
        raise


def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()

def user_email_lookup(hashed_email: str) -> bool:
    try:
        query = {
            "query": {
                "term": {
                    "hashed_email": hashed_email
                }
            }
        }
        response = es.search(index=users_index, body=query, size=1)
        hits = response["hits"]["hits"]
        if hits:
            return hits[0]["_source"]["id"]
    except Exception as e:
        print(f"Error looking up user: {e}")
        return False

def store_user_email(hashed_email: str, email: str) -> str:
    try:
        encrypted_email = encrypt_value(email, "user-email")
        
        # Generate a new ID for each user
        user_id = hashlib.sha1(f"{email}{datetime.now()}".encode()).hexdigest()
        
        user_doc = {
            "id": user_id,
            "hashed_email": hashed_email,
            "encrypted_email": encrypted_email,
            "encrypted_phone": "",
            "created_at": datetime.utcnow()
        }

        es.index(index=users_index, id=user_id, body=user_doc)
        print(f"User {email} added to the database")
        return user_id
    except Exception as e:
        print(f"Error storing user email: {e}")
        raise

def store_user_phone(user_id: str, phone_number: str):
    try:
        encrypted_phone = encrypt_value(phone_number, "user-phone")
        
        update_body = {
            "doc": {
                "encrypted_phone": encrypted_phone,
                "updated_at": datetime.utcnow()
            }
        }
        
        es.update(index=users_index, id=user_id, body=update_body)
        print(f"Phone number added for user {user_id}")
    except Exception as e:
        print(f"Error storing user phone: {e}")
        raise

def store_message(batch):

    actions = [ 
              {
                  "_index": messages_index,
                  "_id": user_id,
                  "_source": {
                      "user_id": user_id,
                      "encrypted_message": encrypted_message,
                      "embeddings": embeddings_list,
                      "created_at": datetime.utcnow()
                      }
                  }
              for user_id, encrypted_message, embeddings_list in batch
        ]


    try:
        helpers.bulk(es, actions)
        print(f"Messages stored for user {user_id}")
    except Exception as e:
        print(f"Error storing messages: {e}")
        raise
        
