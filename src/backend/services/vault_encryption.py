import hvac
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

vault_client = hvac.Client(url='http://localhost:8200', token=os.getenv("VAULT_TOKEN"))


def encrypt_value(value: str, key_name: str) -> str:
    value_b64 = base64.b64encode(value.encode('utf-8')).decode('utf-8')

    if not value_b64:
        return None
    encrypted_value = vault_client.secrets.transit.encrypt_data(
        name=key_name, plaintext=value_b64
    )
    return encrypted_value["data"]["ciphertext"]

def batch_encrypt(texts: list[str], key_name: str) -> list[str]:
    """Encrypt multiple texts in a single Vault API call"""
    batch_input = [{"plaintext": base64.b64encode(txt.encode()).decode()} for txt in texts]
    
    response = requests.post(
        f"{VAULT_ADDR}/v1/transit/encrypt/{key_name}",
        headers={"X-Vault-Token": VAULT_TOKEN},
        json={"batch_input": batch_input}
    )
    response.raise_for_status()
    return [item["ciphertext"] for item in response.json()["data"]["batch_results"]]

def decrypt_value(ciphertext: str, key_name: str) -> str:
    if not ciphertext:
        return None

    decrypted_value = vault_client.secrets.transit.decrypt_data(
        name=key_name, ciphertext=ciphertext
    )
    plaintext = bytes.formhex(decrypted_value["data"]["plaintext"])
    return plaintext.decode()
