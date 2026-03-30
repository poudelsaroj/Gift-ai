"""Security-related helpers."""

from copy import deepcopy
from typing import Any

SENSITIVE_KEYS = {"api_key", "password", "token", "secret"}


def redact_config(data: dict[str, Any]) -> dict[str, Any]:
    """Return a redacted copy of a config dict."""
    redacted = deepcopy(data)
    for key, value in redacted.items():
        if isinstance(value, dict):
            redacted[key] = redact_config(value)
        elif key.lower() in SENSITIVE_KEYS and value is not None:
            redacted[key] = "***REDACTED***"
    return redacted

