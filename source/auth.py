import os
import json
import config

# This function loads users who are authorized to access the drive.
# Authorized users are contained in a JSON file.
def load_authorized_users():
    config.ensure_directories()

    if os.path.exists(config.USERS_PATH):
        with open(config.USERS_PATH, "r") as file:
            return json.load(file)
    return {}


# This function allows to check is a person trying to
# connect is from the group or not.
# Return true is the username is valid, false otherwise.
def is_user_authorized(username):
    authorized_users = load_authorized_users()
    return username in authorized_users