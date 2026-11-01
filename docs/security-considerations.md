# Security Considerations

This project is a learning/academic prototype. The following points should be addressed before relying on it for sensitive data.

1. **Password-based encryption:** Replace the single SHA-256 password hash used for Fernet key derivation with a salted password KDF such as Argon2id or PBKDF2. Store the salt and KDF parameters with a versioned encrypted-file format.
2. **Device identity:** VID/PID identifies a product family, not an individual physical USB device. Consider stronger device-specific identifiers and a clear threat model.
3. **Brute-force control:** Integrate the standalone `BruteForceProtector` into the actual authentication flow and persist/rate-limit attempts appropriately if needed.
4. **Privilege and safety:** Device disabling may require elevated permissions. Test with non-critical devices and provide a reliable recovery/unblock procedure.
5. **Secret management:** Keep password hashes, real whitelists, logs containing device identifiers, and test data out of public version control.
6. **Data integrity and backups:** Never delete originals until decryption has been tested and a separate backup exists.

## Current implementation clarification

The encryption module uses Fernet from `cryptography`; Fernet provides authenticated symmetric encryption. The code derives its Fernet key by applying SHA-256 directly to the password. This is not equivalent to using a dedicated password-based key derivation function.
