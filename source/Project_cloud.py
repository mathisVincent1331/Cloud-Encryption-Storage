import os
import re

import config
import auth
import crypto
import drive_service



def main() :
    config.ensure_directories()
    crypto.generate_rsa_keys()
    pub_key, priv_key = crypto.load_rsa_keys()

    # Generate session AES key
    aes_key = crypto.generate_aes_key()
    encrypted_aes_key = crypto.encrypt_aes_key(aes_key, pub_key)
    decrypted_aes_key = crypto.decrypt_aes_key(encrypted_aes_key, priv_key)

    while True:
        print("\n--- Secure Cloud Storage ---")
        print("1 - Upload a file")
        print("2 - Download a file")
        print("0 - Quit")
        
        client_choice = input("Enter choice: ").strip()
        while not re.fullmatch("[0-2]", client_choice):
            client_choice = input("Invalid option. Enter 0, 1, or 2: ").strip()

        if client_choice == "0":
            print("--- End of the program ---")
            break

        username = input("Enter your username: ").strip()

        if not auth.is_user_authorized(username):
            print("Unauthorized user. Access denied.")
            continue

        file_input = input("Please enter a file path or file name: ").strip()
        service = drive_service.authenticate_google_drive()

        if client_choice == "1":
            if not os.path.exists(file_input):
                print(f"Error: Local file '{file_input}' not found.")
                continue
            crypto.encrypt_file(file_input, aes_key)
            drive_service.upload_to_drive(file_input + ".enc", service)

        elif client_choice == "2":
            target_enc_name = os.path.basename(file_input)
            if not target_enc_name.endswith(".enc"):
                target_enc_name += ".enc"

            file_id = drive_service.get_file_id_by_name(target_enc_name, service)
            if file_id:
                drive_service.download_and_decrypt_from_drive(
                    file_id, service, decrypted_aes_key, username
                )


# Main Execution
if __name__ == "__main__":
    main()