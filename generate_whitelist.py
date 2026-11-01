import os
import json
import wmi

WHITELIST_PATH = os.path.join("data", "whitelist.json")

def extract_vidpid(dev_id: str) -> str | None:
    """Return USB\\VID_xxxx&PID_xxxx from any PNP/instance ID."""
    if not dev_id:
        return None
    s = dev_id.upper().replace("/", "\\")
    if "USB\\VID_" in s:
        part = s[s.find("USB\\VID_"):].split("\\")[0]
        return part.split("&MI_")[0]
    return None

def normalize_signature(sig: str) -> str:
    return sig.strip().upper()

def generate_whitelist():
    c = wmi.WMI()
    found = set()

    for drive in c.Win32_DiskDrive():
        if (drive.InterfaceType or "").upper() == "USB":
            sig = extract_vidpid(drive.PNPDeviceID)
            if sig:
                norm = normalize_signature(sig)
                if norm not in found:
                    found.add(norm)
                    print(f"[✅] Added: {norm}")
            else:
                print(f"[ℹ️] Skipped (no VID/PID found): {drive.Caption}")

    if not found:
        print("⚠️ No USB devices detected.")
        return

    os.makedirs(os.path.dirname(WHITELIST_PATH), exist_ok=True)
    with open(WHITELIST_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(found), f, indent=2)

    print(f"[💾] Whitelist saved to {WHITELIST_PATH}")
    print(f"✅ Whitelist updated with {len(found)} device(s).")
    print(f"📦 Total entries: {len(found)}")

if __name__ == "__main__":
    generate_whitelist()