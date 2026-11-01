# modules/aes_crypto.py
from cryptography.fernet import Fernet
import base64
import hashlib

def derive_key(password: str) -> bytes:
    # Derive a Fernet-compatible key from password
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_file(input_path: str, output_path: str, password: str, delete_original=False):
    key = derive_key(password)
    fernet = Fernet(key)

    with open(input_path, 'rb') as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    with open(output_path, 'wb') as f:
        f.write(encrypted)

    print(f"[🔒] Encrypted: {output_path}")

    if delete_original:
        import os
        os.remove(input_path)
        print(f"[🧹] Deleted original: {input_path}")

def decrypt_file(input_path: str, output_path: str, password: str):
    key = derive_key(password)
    fernet = Fernet(key)

    with open(input_path, 'rb') as f:
        encrypted = f.read()

    try:
        decrypted = fernet.decrypt(encrypted)
    except Exception:
        print("[⛔] Decryption failed. Wrong password or corrupted file.")
        return False

    with open(output_path, 'wb') as f:
        f.write(decrypted)

    print(f"[🔓] Decrypted: {output_path}")
    return True

def encrypt_folder(folder_path: str, password: str, delete_original=False):
    import os
    from pathlib import Path

    for file in Path(folder_path).glob("*"):
        if file.is_file() and not file.name.endswith(".enc"):
            input_path = str(file)
            output_path = input_path + ".enc"
            encrypt_file(input_path, output_path, password, delete_original)

def decrypt_folder(folder_path: str, password: str):
    import os
    from pathlib import Path

    key = derive_key(password)
    fernet = Fernet(key)

    for file in Path(folder_path).glob("*.enc"):
        input_path = str(file)
        output_path = input_path.replace(".enc", ".dec")

        with open(input_path, 'rb') as f:
            encrypted = f.read()

        try:
            decrypted = fernet.decrypt(encrypted)
        except Exception:
            print(f"[⛔] Failed to decrypt: {input_path}")
            continue

        with open(output_path, 'wb') as f:
            f.write(decrypted)

        print(f"[🔓] Decrypted: {output_path}")