# SecureUSB

**A Windows-focused Python project for USB device monitoring, whitelist-based access control, password authentication, and on-demand file/folder encryption.**

> Academic / learning project. Review the security limitations below before using this with important data or on a production computer.

## Features

- **USB monitoring:** polls Windows Plug and Play devices through WMI.
- **Device authorization:** compares USB vendor/product identifiers (VID/PID) against a local whitelist.
- **Access decisions:** supports automatic blocking or an interactive choice to whitelist, temporarily allow, or block an unrecognized device.
- **Password verification:** stores an administrator password hash using bcrypt.
- **File and folder encryption:** encrypts files using Fernet from the Python `cryptography` package.
- **Brute-force protection module:** includes a standalone attempt/lockout helper (`brute_defense.py`).

## How it is organized

```text
SecureUSB/
├── main.py
├── brute_defense.py
├── generate_whitelist.py
├── requirements.txt
├── modules/
│   ├── __init__.py
│   ├── auth.py
│   ├── detection.py
│   └── aes_crypto.py
├── data/
│   ├── .gitkeep
│   └── whitelist.example.json
├── tools/
│   └── README.md
├── docs/
│   ├── architecture.md
│   └── security-considerations.md
└── screenshots/
    └── README.md
```

Runtime files such as `data/password.hash` and `data/whitelist.json` are created locally and are intentionally not included in this repository.

## Requirements

- Windows (USB monitoring and device disabling rely on Windows WMI and Microsoft's DevCon utility).
- Python 3.10 or newer.
- Administrator privileges may be required for device disabling/enabling.
- A compatible `devcon.exe` installed at `tools/devcon.exe` for the blocking/unblocking feature.

## Setup

1. Install Python 3.10+.
2. Clone the repository:

   ```powershell
   git clone https://github.com/Kaiyumahmed/SecureUSB.git
   cd SecureUSB
   ```

3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Obtain a compatible DevCon utility from the official Microsoft Windows Driver Kit (WDK) documentation and place it at `tools/devcon.exe`. Do not download executables from untrusted sites.

## First-time configuration

Run these commands from the project root:

```powershell
python main.py setpass
python generate_whitelist.py
```

`generate_whitelist.py` records VID/PID signatures for currently connected USB disk drives in `data/whitelist.json`. Review the generated list before enabling automatic blocking.

## Usage

Show available commands:

```powershell
python main.py --help
```

Start USB monitoring (unknown devices are automatically blocked):

```powershell
python main.py monitor --interval 2 --log logs/usb-events.log
```

Start interactive monitoring:

```powershell
python main.py monitor --prompt
```

Show the local whitelist:

```powershell
python main.py whitelist
```

Encrypt a file:

```powershell
python main.py encrypt-file --input sample.txt --output sample.txt.enc
```

Decrypt a file:

```powershell
python main.py decrypt-file --input sample.txt.enc --output sample-restored.txt
```

Encrypt a folder:

```powershell
python main.py encrypt-folder --path .\private-files
```

Decrypt encrypted files in a folder:

```powershell
python main.py decrypt-folder --path .\private-files
```

Add `--delete-original` to an encryption command only when you have verified a separate backup and tested decryption.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the component diagram and responsibilities.

## Security notes and known limitations

- **VID/PID is not a unique device identity.** Different physical devices can share the same vendor/product identifiers. This whitelist is a basic control, not strong device attestation.
- **The current file-encryption key derivation is not a password KDF.** `modules/aes_crypto.py` hashes the password once with SHA-256 and converts it to a Fernet key. For stronger protection, use a salted, deliberately slow KDF (for example, Argon2id or PBKDF2) and a versioned file format. Existing encrypted files would need a migration/compatibility plan before changing this.
- **Brute-force protection is not currently integrated.** `brute_defense.py` defines a standalone helper; the current `modules/auth.py` password verification does not call it.
- **Device blocking depends on DevCon, Windows permissions, and matching device instance IDs.** Test carefully: disabling the wrong device can interrupt hardware.
- **Do not commit** `data/password.hash`, `data/whitelist.json`, logs, real user data, or private keys.
- Keep an independent backup before encrypting or deleting originals.

## Screenshots

Add genuine screenshots of the running application to `screenshots/`. Do not add mock screenshots that imply functionality you have not tested.

## Project status

This repository documents the current implementation. Some security improvements and automated tests are suitable future work.

## Author

**Kaiyumahmed**

## License

No license has been selected yet. Add a license only after deciding how you want others to use, modify, and distribute this project.
