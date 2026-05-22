"""
Utility for generating secure share tokens.
"""

import secrets
import string


def generate_share_token(length: int = 32) -> str:
    """
    Generate a secure random token for shareable links.

    Args:
        length: Token length

    Returns:
        URL-safe random token
    """
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))
