# auth_client.py
"""
Authenticator client for COMP2001 CW2.
"""

import os
import requests


AUTH_URL = os.getenv(
    "AUTH_URL",
    "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users",
)


def verify_credentials(email: str, password: str) -> bool:
    """
    Returns True if authenticator accepts the credentials, otherwise False.
    Safe: returns False on any network/timeout error.
    """
    if not email or not password:
        return False

    payload = {"email": email, "password": password}

    try:
        resp = requests.post(AUTH_URL, json=payload, timeout=10)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def _cli_test():
    """
    Simple manual test runner for screenshots.
    Reads AUTH_EMAIL / AUTH_PASSWORD from env if available,
    otherwise uses known lab test credentials (ONLY for local testing).
    """
    email = os.getenv("AUTH_EMAIL") or "tim@plymouth.ac.uk"
    password = os.getenv("AUTH_PASSWORD") or "COMP2001!"

    ok = verify_credentials(email, password)

    print("=== COMP2001 Authenticator Test ===")
    print("URL:", AUTH_URL)
    print("Email:", email)
    print("Result:", "AUTHENTICATION SUCCESS" if ok else "AUTHENTICATION FAILED")


if __name__ == "__main__":
    _cli_test()
