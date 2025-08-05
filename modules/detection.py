import wmi
import json
import os

WHITELIST_PATH = os.path.join('data', 'whitelist.json')

def load_whitelist():
    try:
        with open(WHITELIST_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def is_authorized(device, whitelist):
    device_id = device.PNPDeviceID
    return device_id in whitelist

def detect_usb_devices():
    c = wmi.WMI()
    whitelist = load_whitelist()

    for device in c.Win32_USBHub():
        print(f"🔌 Device: {device.Name}")
        print(f"🆔 ID: {device.PNPDeviceID}")
        if is_authorized(device, whitelist):
            print("✅ Authorized\n")
        else:
            print("⛔ Unauthorized\n")