import os

FOLDER_ID = "1IHYjHqNVOQbnv-qAJOJNAriHg04ps_q7"

# Repertory paths
CRED_DIR = "../cred"
KEYS_DIR = "../keys"

# Configuration and key file paths
CREDENTIALS_PATH = os.path.join(CRED_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CRED_DIR, "token.pickle")
USERS_PATH = os.path.join(CRED_DIR, "authorized_users.json")

PUB_KEY_PATH = os.path.join(KEYS_DIR, "public.pem")
PRIV_KEY_PATH = os.path.join(KEYS_DIR, "private.pem")

# Ensure directory structure exists
def ensure_directories():
    os.makedirs(CRED_DIR, exist_ok=True)
    os.makedirs(KEYS_DIR, exist_ok=True)