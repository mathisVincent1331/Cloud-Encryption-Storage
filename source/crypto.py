import os
import base64
import rsa
from cryptography.fernet import Fernet

import config
from auth import is_user_authorized


# RSA Key Management
# This function generates a 2048-bit RSA key at each run.
def generate_rsa_keys():
    config.ensure_directories()

    if not (os.path.exists(config.PUB_KEY_PATH) and os.path.exists(config.PRIV_KEY_PATH)):
        public_key, private_key = rsa.newkeys(2048)
        with open(config.PUB_KEY_PATH, "wb") as pub_file:
            pub_file.write(public_key.save_pkcs1("PEM"))
        with open(config.PRIV_KEY_PATH, "wb") as priv_file:
            priv_file.write(private_key.save_pkcs1("PEM"))
        print("RSA Keys generated.")
    else:
        print("Existing RSA Keys loaded.")


# Load the RSA key which was generated above.
def load_rsa_keys():
    with open(config.PUB_KEY_PATH, "rb") as pub_file:
        public_key = rsa.PublicKey.load_pkcs1(pub_file.read())
    with open(config.PRIV_KEY_PATH, "rb") as priv_file:
        private_key = rsa.PrivateKey.load_pkcs1(priv_file.read())
    return public_key, private_key

# AES Encryption
def generate_aes_key():
    return Fernet.generate_key()


# Function which helps encrypt our files
def encrypt_file(file_path, aes_key):
    f = Fernet(aes_key)
    with open(file_path, "rb") as file:
        encrypted_data = f.encrypt(file.read())

    enc_path = file_path + ".enc"
    with open(enc_path, "wb") as enc_file:
        enc_file.write(encrypted_data)
    print(f"Encrypted file saved as {file_path}.enc")
    return encrypted_data


# At the opposite, this function helps decrypt the files with using AES key
def decrypt_file(encrypted_file_path, aes_key, username):
    if not is_user_authorized(username):
        print("Access Denied: You are not part of the Secure Cloud Storage Group.")
        return

    f = Fernet(aes_key)
    with open(encrypted_file_path, "rb") as enc_file:
        decrypted_data = f.decrypt(enc_file.read())

    original_file_path = encrypted_file_path.replace(".enc", "")
    with open(original_file_path, "wb") as file:
        file.write(decrypted_data)
    print(f"Decrypted file saved as {original_file_path}")

# Encrypt AES key with RSA
def encrypt_aes_key(aes_key, public_key):
    encrypted_key = rsa.encrypt(aes_key, public_key)
    return base64.b64encode(encrypted_key).decode()


# Decrypt AES key with RSA
def decrypt_aes_key(encrypted_aes_key, private_key):
    decoded_key = base64.b64decode(encrypted_aes_key)
    return rsa.decrypt(decoded_key, private_key)