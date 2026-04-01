"""Security-related helpers."""

from copy import deepcopy
from typing import Any

SENSITIVE_KEY_FRAGMENTS = ("api_key", "private_key", "public_key", "password", "token", "secret")


def redact_config(data: dict[str, Any]) -> dict[str, Any]:
    """Return a redacted copy of a config dict."""
    redacted = deepcopy(data)
    for key, value in redacted.items():
        if isinstance(value, dict):
            redacted[key] = redact_config(value)
        elif any(fragment in key.lower() for fragment in SENSITIVE_KEY_FRAGMENTS) and value is not None:
            redacted[key] = "***REDACTED***"
    return redacted

