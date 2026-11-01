
flowchart TD
    A[main.py CLI] --> B[USB Monitoring]
    B --> C[WMI Device Enumeration]
    C --> D[VID/PID Extraction]
    D --> E{Device in Whitelist?}

    E -->|Yes| F[Allow Device]
    E -->|No| G{Interactive Prompt Enabled?}

    G -->|No| H[Automatic Blocking]
    G -->|Yes| I{User Decision}

    I -->|Whitelist| J[Password Verification]
    I -->|Temporary Allow| K[Password Verification]
    I -->|Block| H

    J -->|Success| L[Update Whitelist]
    J -->|Failure| H

    K -->|Success| M[Temporary Session Allow]
    K -->|Failure| H

    H --> N[DevCon Disable Command]

    A --> O[Authentication Module]
    O --> P[bcrypt Password Hash]

    A --> Q[File and Folder Encryption]
    Q --> R[Fernet Encryption/Decryption]

    A --> S[brute_defense.py]
    S --> T[Standalone Lockout Helper]
