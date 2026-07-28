# BYOK Rules

1. BYOK keys must be stored in sessionStorage only — never localStorage or cookies.
2. Keys must never be logged, persisted to disk, or transmitted to any server.
3. Keys must never enter the Digital Printer or evidence SoT.
4. Hosted BYOK flag must respect `BYOK_HOSTED` env var — no silent cloud fallback.
5. Model override must validate that the model ID is in the allowed list.
6. Authorization headers must use `Bearer` scheme with session key.
