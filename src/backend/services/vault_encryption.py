import hvac
import os
import base64

vault_client = hvac.Client(url=os.getenv("VAULT_ADDR"), token=os.getenv("VAULT_TOKEN"))


def encrypt_value(value: str, key_name: str) -> str:
    value_b64 = base64.b64encode(value.encode('utf-8')).decode('utf-8')

    if not value_b64:
        return None
    encrypted_value = vault_client.secrets.transit.encrypt_data(
        name=key_name, plaintext=value_b64
    )
    return encrypted_value["data"]["ciphertext"]


def decrypt_value(ciphertext: str, key_name: str) -> str:
    if not ciphertext:
        return None

    decrypted_value = vault_client.secrets.transit.decrypt_data(
        name=key_name, ciphertext=ciphertext
    )
    plaintext = bytes.formhex(decrypted_value["data"]["plaintext"])
    return plaintext.decode()
