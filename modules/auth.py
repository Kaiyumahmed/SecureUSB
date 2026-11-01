import bcrypt
import getpass
import json

PASSWORD_FILE = 'data/password.hash'

def set_password():
    password = getpass.getpass("Set a new password: ")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(PASSWORD_FILE, 'wb') as f:
        f.write(hashed)
    print("Password set successfully.")

def verify_password():
    try:
        with open(PASSWORD_FILE, 'rb') as f:
            stored_hash = f.read()
    except FileNotFoundError:
        print("No password set. Run with --setpass to create one.")
        return False

    password = getpass.getpass("Enter password to allow access: ")
    return bcrypt.checkpw(password.encode(), stored_hash)