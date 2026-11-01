import wmi
import os
import json
import subprocess

WHITELIST_PATH = os.path.join('data', 'whitelist.json')
DEVCON_PATH = os.path.join('tools', 'devcon.exe')

def load_whitelist(path=WHITELIST_PATH):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def normalize_signature(sig: str) -> str:
    """Normalize VID/PID signature to uppercase."""
    return sig.strip().upper()

def add_to_whitelist(sig: str, path=WHITELIST_PATH) -> bool:
    """Add normalized signature to whitelist.json if not already present."""
    sig = normalize_signature(sig)
    current = {normalize_signature(s) for s in load_whitelist(path)}
    if sig in current:
        return False
    current.add(sig)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(sorted(current), f, indent=2)
        return True
    except Exception:
        return False

def extract_vidpid(dev_id: str) -> str | None:
    """Return USB\\VID_xxxx&PID_xxxx from any PNP/instance ID."""
    if not dev_id:
        return None
    s = dev_id.upper().replace("/", "\\")
    if "USB\\VID_" in s:
        part = s[s.find("USB\\VID_"):].split("\\")[0]
        return part.split("&MI_")[0]
    return None

def detect_usb_devices():
    c = wmi.WMI()
    whitelist = load_whitelist()
    detected_ids = []
    whitelist_sigs = {w.upper() for w in whitelist}

    for drive in c.Win32_DiskDrive():
        if not is_probably_usb_drive(drive):
            continue

        pnp_id = drive.PNPDeviceID
        sig = extract_vidpid(pnp_id)
        detected_ids.append(sig or pnp_id)

        print(f"🔌 Drive: {drive.Caption}")
        print(f"🆔 Sig:   {sig or 'N/A'}")

        if sig and sig in whitelist_sigs:
            print("✅ Authorized\n")
        else:
            print("⛔ Unauthorized\n")

    return detected_ids

def is_probably_usb_drive(drive):
    caption = (drive.Caption or "").lower()
    interface = (drive.InterfaceType or "").upper()
    model = (drive.Model or "").lower()
    return interface == "USB" or "usb" in caption or "usb" in model

def resolve_targets(instance_id: str):
    """Return list of possible devcon targets for disable/enable."""
    targets = []
    sig = extract_vidpid(instance_id)
    c = wmi.WMI()
    for dev in c.Win32_PnPEntity():
        if dev.PNPDeviceID and sig and sig in dev.PNPDeviceID.upper():
            targets.append(dev.PNPDeviceID)
    return targets

def _run_devcon(args):
    proc = subprocess.run([DEVCON_PATH] + args, capture_output=True, text=True)
    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    return proc.returncode, out

def block_device(instance_id: str):
    targets = resolve_targets(instance_id)
    sig = extract_vidpid(instance_id)

    for t in targets:
        rc, out = _run_devcon(["disable", f"@{t}"])
        if "disabled" in out.lower():
            print(f"[🔒] Blocked instance: {t}")
            return

    if sig:
        rc, out = _run_devcon(["disable", f"*{sig}*"])
        if "disabled" in out.lower():
            print(f"[🔒] Blocked all devices with: {sig}")
            return

    print("[❌] Devcon failed to disable device(s).")

def unblock_device(instance_id: str):
    targets = resolve_targets(instance_id)
    sig = extract_vidpid(instance_id)

    for t in targets:
        rc, out = _run_devcon(["enable", f"@{t}"])
        if "enabled" in out.lower():
            print(f"[🔓] Unblocked instance: {t}")
            return

    if sig:
        rc, out = _run_devcon(["enable", f"*{sig}*"])
        if "enabled" in out.lower():
            print(f"[🔓] Unblocked all devices with: {sig}")
            return

    print("[❌] Devcon failed to enable device(s).")