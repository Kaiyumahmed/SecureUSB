# main.py
import argparse
import sys
import time
import os
from datetime import datetime
import getpass
import wmi

# Local modules
from modules.detection import (
    load_whitelist,
    extract_vidpid,
    block_device,
    unblock_device,
    add_to_whitelist,
    normalize_signature,
)
from modules.auth import set_password as auth_set_password, verify_password as auth_verify_password
from modules.aes_crypto import (
    encrypt_file,
    decrypt_file,
    encrypt_folder,
    decrypt_folder,
)

# ------------- Utilities -------------

def make_logger(log_path: str | None):
    """Return a logger callable that writes timestamped lines to file (and stdout)."""
    if not log_path:
        def _log(msg: str):
            print(msg)
        return _log

    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    def _log(msg: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            print(f"[⚠️] Failed to write log: {e}")
    return _log

def load_whitelist_set():
    """Load whitelist as an uppercase set of VID/PID signatures."""
    return {s.upper() for s in load_whitelist()}

# ------------- Monitoring -------------

def monitor_usb(interval: int, prompt_on_unauthorized: bool, log_path: str | None):
    log = make_logger(log_path)
    log("🔍 Monitoring USB devices...")

    c = wmi.WMI()
    whitelist = load_whitelist_set()
    if not whitelist:
        log("⚠️ Whitelist is empty. Run your whitelist generator first to avoid over-blocking.")

    seen = set()
    temp_allow = set()

    while True:
        current = set()
        for dev in c.Win32_PnPEntity():
            pid = getattr(dev, "PNPDeviceID", None)
            if not pid:
                continue
            upid = pid.upper()
            if "USB\\VID_" not in upid:
                continue

            sig = extract_vidpid(upid)
            if not sig:
                continue

            current.add((sig, pid))

        for sig, full_id in current - seen:
            label = f"{sig}"
            if sig in whitelist or sig in temp_allow:
                log(f"[+] USB connected: {label} ✅ Authorized")
            else:
                log(f"[+] USB connected: {label} ⛔ Unauthorized")
                if prompt_on_unauthorized:
                    try:
                        choice = input("Approve device? [w]hitelist / [t]emporary / [b]lock (default b): ").strip().lower()
                    except EOFError:
                        choice = "b"

                    if choice.startswith("w"):
                        if auth_verify_password():
                            norm_sig = normalize_signature(sig)
                            if add_to_whitelist(norm_sig):
                                whitelist.add(norm_sig)
                                log(f"[✅] Whitelisted: {label}")
                            else:
                                log(f"[ℹ] Already whitelisted: {label}")
                        else:
                            log("[⛔] Password verification failed. Blocking device.")
                            block_device(full_id)

                    elif choice.startswith("t"):
                        if auth_verify_password():
                            temp_allow.add(sig)
                            log(f"[🔓] Temporarily allowed this session: {label}")
                        else:
                            log("[⛔] Password verification failed. Blocking device.")
                            block_device(full_id)

                    else:
                        log("[🔒] Blocking device.")
                        block_device(full_id)
                else:
                    log("[🔒] Auto-blocking unauthorized device.")
                    block_device(full_id)

        for sig, full_id in seen - current:
            log(f"[-] USB disconnected: {sig}")
            if sig in temp_allow:
                temp_allow.discard(sig)

        seen = current
        time.sleep(interval)

# ------------- AES File/Folder Ops -------------

def cmd_encrypt_file(args):
    password = args.password or getpass.getpass("Password for encryption: ")
    encrypt_file(args.input, args.output, password, delete_original=args.delete_original)

def cmd_decrypt_file(args):
    password = args.password or getpass.getpass("Password for decryption: ")
    ok = decrypt_file(args.input, args.output, password)
    if not ok:
        sys.exit(1)

def cmd_encrypt_folder(args):
    password = args.password or getpass.getpass("Password for encryption: ")
    encrypt_folder(args.path, password, delete_original=args.delete_original)

def cmd_decrypt_folder(args):
    password = args.password or getpass.getpass("Password for decryption: ")
    decrypt_folder(args.path, password)

# ------------- Auth -------------

def cmd_set_password(_args):
    auth_set_password()

# ------------- Whitelist helpers -------------

def cmd_show_whitelist(_args):
    wl = load_whitelist()
    if not wl:
        print("Whitelist is empty.")
    else:
        print("Whitelist signatures:")
        for s in wl:
            print(f" - {s}")

# ------------- CLI -------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="SecureUSB",
        description="USB access control and on-demand encryption."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("monitor", help="Monitor USB devices and enforce whitelist.")
    m.add_argument("--interval", type=int, default=2, help="Polling interval in seconds (default: 2).")
    m.add_argument("--prompt", action="store_true", help="Prompt for temporary allow on unauthorized devices.")
    m.add_argument("--log", type=str, default=None, help="Path to append event logs.")
    m.set_defaults(func=lambda a: monitor_usb(a.interval, a.prompt, a.log))

    sp = sub.add_parser("setpass", help="Set or update the administrative password.")
    sp.set_defaults(func=cmd_set_password)

    wl = sub.add_parser("whitelist", help="Show current whitelist signatures.")
    wl.set_defaults(func=cmd_show_whitelist)

    ef = sub.add_parser("encrypt-file", help="Encrypt a single file.")
    ef.add_argument("--input", "-i", required=True, help="Path to input file.")
    ef.add_argument("--output", "-o", required=True, help="Path to output encrypted file.")
    ef.add_argument("--password", "-p", help="Encryption password (omit to prompt securely).")
    ef.add_argument("--delete-original", "-D", action="store_true", help="Delete original file after encryption.")
    ef.set_defaults(func=cmd_encrypt_file)

    df = sub.add_parser("decrypt-file", help="Decrypt a single file.")
    df.add_argument("--input", "-i", required=True, help="Path to encrypted file.")
    df.add_argument("--output", "-o", required=True, help="Path to output decrypted file.")
    df.add_argument("--password", "-p", help="Decryption password (omit to prompt securely).")
    df.set_defaults(func=cmd_decrypt_file)

    enf = sub.add_parser("encrypt-folder", help="Encrypt all non-.enc files in a folder.")
    enf.add_argument("--path", "-P", required=True, help="Folder path.")
    enf.add_argument("--password", "-p", help="Encryption password (omit to prompt securely).")
    enf.add_argument("--delete-original", "-D", action="store_true", help="Delete originals after encryption.")
    enf.set_defaults(func=cmd_encrypt_folder)

    defo = sub.add_parser("decrypt-folder", help="Decrypt all .enc files in a folder.")
    defo.add_argument("--path", "-P", required=True, help="Folder path.")
    defo.add_argument("--password", "-p", help="Decryption password (omit to prompt securely).")
    defo.set_defaults(func=cmd_decrypt_folder)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    except Exception as e:
        print(f"[❌] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()