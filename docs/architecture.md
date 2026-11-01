
# SecureUSB Architecture

## System Architecture Diagram

```mermaid
flowchart TD
    A["main.py CLI"] --> B["USB Monitoring"]
    B --> C["WMI Device Enumeration"]
    C --> D["VID/PID Extraction"]
    D --> E{"Device in Whitelist?"}

    E -->|Yes| F["Allow Device"]
    E -->|No| G{"Interactive Prompt Enabled?"}

    G -->|No| H["Automatic Blocking"]
    G -->|Yes| I{"User Decision"}

    I -->|Whitelist| J["Password Verification"]
    I -->|Temporary Allow| K["Password Verification"]
    I -->|Block| H

    J -->|Success| L["Update Local Whitelist"]
    J -->|Failure| H

    K -->|Success| M["Temporary Session Allow"]
    K -->|Failure| H

    H --> N["DevCon Disable Command"]

    A --> O["Authentication Module"]
    O --> P["bcrypt Password Hash"]

    A --> Q["File and Folder Encryption"]
    Q --> R["Fernet Encryption/Decryption"]

    A --> S["brute_defense.py"]
    S --> T["Standalone Lockout Helper"]

    style A fill:#1d4ed8,color:#fff,stroke:#60a5fa
    style E fill:#854d0e,color:#fff,stroke:#fbbf24
    style I fill:#854d0e,color:#fff,stroke:#fbbf24
    style H fill:#991b1b,color:#fff,stroke:#f87171
    style F fill:#166534,color:#fff,stroke:#4ade80
    style L fill:#166534,color:#fff,stroke:#4ade80
    style M fill:#166534,color:#fff,stroke:#4ade80
```

## Component Description

| Component | Responsibility |
|---|---|
| main.py | Main application and CLI |
| detection.py | USB detection and device control |
| auth.py | Password authentication |
| aes_crypto.py | File and folder encryption |
| brute_defense.py | Brute-force protection helper |
| generate_whitelist.py | USB whitelist generation |
