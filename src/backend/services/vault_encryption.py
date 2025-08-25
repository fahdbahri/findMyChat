import hvac
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

vault_client = hvac.Client(url="http://vault:8200", token=os.getenv("VAULT_TOKEN"))


def encrypt_value(value: str, key_name: str) -> str:
    value_b64 = base64.b64encode(value.encode("utf-8")).decode("utf-8")

    if not value_b64:
        return None
    encrypted_value = vault_client.secrets.transit.encrypt_data(
        name=key_name, plaintext=value_b64
    )
    return encrypted_value["data"]["ciphertext"]


def batch_encrypt(texts: list[str], key_name: str) -> list[str]:
    """Encrypt multiple texts in a single Vault API call"""
    batch_input = [
        {"plaintext": base64.b64encode(txt.encode()).decode()} for txt in texts
    ]

    response = requests.post(
        f"{VAULT_ADDR}/v1/transit/encrypt/{key_name}",
        headers={"X-Vault-Token": VAULT_TOKEN},
        json={"batch_input": batch_input},
    )
    response.raise_for_status()
    return [item["ciphertext"] for item in response.json()["data"]["batch_results"]]


def batch_decrypt(ciphertexts: list[str], key_name: str) -> list[str]:
    """Decrypt multiple ciphertexts in a single Vault API call"""
    if not ciphertexts:
        return []

    batch_input = [{"ciphertext": ct} for ct in ciphertexts]

    response = requests.post(
        f"{VAULT_ADDR}/v1/transit/decrypt/{key_name}",
        headers={"X-Vault-Token": VAULT_TOKEN},
        json={"batch_input": batch_input},
    )
    response.raise_for_status()

    results = []
    for item in response.json()["data"]["batch_results"]:
        plaintext_b64 = item.get("plaintext")
        if plaintext_b64:
            results.append(base64.b64decode(plaintext_b64).decode("utf-8"))
        else:
            results.append(None)

    return results
