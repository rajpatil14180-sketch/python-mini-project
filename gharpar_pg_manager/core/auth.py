"""Password hashing, verification, and user login."""
import hashlib
import secrets
from database import get_connection


def hash_password(password, salt_hex=None):
    """FEATURE: Password Hashing
    Hash a password using PBKDF2-SHA256 with 100000 rounds."""
    if salt_hex is None:
        salt_hex = secrets.token_hex(16)
    password_bytes = password.encode("utf-8")
    salt_bytes = bytes.fromhex(salt_hex)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password_bytes, salt_bytes, 100000)
    return hash_bytes.hex(), salt_hex


def verify_password(password, hash_hex, salt_hex):
    """FEATURE: Password Hashing
    Return True when the password matches the stored hash and salt."""
    computed_hash, _ = hash_password(password, salt_hex)
    return computed_hash == hash_hex


def login(username, password):
    """FEATURE: Login
    Authenticate a user and reject tenants whose tenancy is inactive."""
    row = _get_user(username)
    if row is None or not verify_password(password, row["password_hash"], row["salt"]):
        return None
    tenant_id = None
    if row["role"] == "tenant":
        tenant_id = _get_active_tenant_id(row["id"])
        if tenant_id is None:
            return None
    return {
        "user_id": row["id"], "username": row["username"],
        "role": row["role"], "tenant_id": tenant_id,
    }


def _get_user(username):
    """FEATURE: Login
    Find the stored account matching the supplied username."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, salt, role FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    return row


def _get_active_tenant_id(user_id):
    """FEATURE: Login
    Return the active tenant record ID for a tenant user, or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM tenants WHERE user_id = ? AND is_active = 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["id"] if row else None
