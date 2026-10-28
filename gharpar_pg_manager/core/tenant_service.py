"""Owner actions for tenant records and payments."""
from datetime import date
from database import get_connection
import config
from core.auth import hash_password


def add_tenant(bed_id, name, phone, join_date, deposit, agreed_price, username, password):
    """FEATURE: Add Tenant
    Create a tenant account and save the agreed price supplied by the owner."""
    join_text = _validate_tenant_details(
        name, phone, join_date, deposit, agreed_price, username, password
    )
    password_hash, salt = hash_password(password)
    conn = get_connection()
    try:
        _ensure_bed_is_available(conn, bed_id)
        user_id = _insert_tenant_user(conn, username, password_hash, salt)
        cursor = conn.execute(
            "INSERT INTO tenants (user_id, bed_id, name, phone, join_date, deposit, "
            "agreed_yearly_price, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
            (user_id, bed_id, name.strip(), phone.strip(), join_text, deposit, agreed_price),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _validate_tenant_details(name, phone, join_date, deposit, agreed_price, username, password):
    """FEATURE: Add Tenant
    Validate required fields, money values, and the ISO joining date."""
    if not username.strip() or not password or not name.strip() or not phone.strip():
        raise ValueError("Name, phone, username, and password are required.")
    if type(deposit) is not int or deposit < 0:
        raise ValueError("Deposit must be a non-negative whole number.")
    if type(agreed_price) is not int or agreed_price < 0:
        raise ValueError("Agreed price must be a non-negative whole number.")
    join_text = join_date.isoformat() if isinstance(join_date, date) else str(join_date)
    date.fromisoformat(join_text)
    return join_text


def _ensure_bed_is_available(conn, bed_id):
    """FEATURE: Add Tenant
    Reject adding a tenant when the bed already has an active tenant."""
    row = conn.execute(
        "SELECT id FROM tenants WHERE bed_id = ? AND is_active = 1", (bed_id,)
    ).fetchone()
    if row is not None:
        raise ValueError("This bed already has an active tenant.")


def _insert_tenant_user(conn, username, password_hash, salt):
    """FEATURE: Add Tenant
    Create and return the new tenant user's account ID."""
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, 'tenant')",
        (username.strip(), password_hash, salt),
    )
    return cursor.lastrowid


def vacate_tenant(tenant_id):
    """FEATURE: Vacate Tenant
    Mark the tenant inactive while preserving their account and history."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE tenants SET is_active = 0 WHERE id = ? AND is_active = 1",
            (tenant_id,),
        )
        conn.commit()
    finally:
        conn.close()


def add_payment(tenant_id, amount, paid_on, mode):
    """FEATURE: Record Payment
    Record a valid payment that does not exceed the remaining yearly price."""
    if type(amount) is not int or amount <= 0:
        raise ValueError("Payment amount must be a positive whole number.")
    if mode not in config.PAYMENT_MODES:
        raise ValueError("Payment mode must be cash or upi.")
    paid_text = paid_on.isoformat() if isinstance(paid_on, date) else str(paid_on)
    date.fromisoformat(paid_text)
    conn = get_connection()
    try:
        due_left = _get_tenant_due_left(conn, tenant_id)
        if amount > due_left:
            raise ValueError("Payment cannot exceed the remaining amount due.")
        cursor = conn.execute(
            "INSERT INTO payments (tenant_id, amount, paid_on, mode) VALUES (?, ?, ?, ?)",
            (tenant_id, amount, paid_text, mode),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _get_tenant_due_left(conn, tenant_id):
    """FEATURE: Record Payment
    Return the remaining yearly balance for an existing tenant."""
    row = conn.execute(
        "SELECT agreed_yearly_price FROM tenants WHERE id = ?", (tenant_id,)
    ).fetchone()
    if row is None:
        raise ValueError("Tenant not found.")
    paid = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE tenant_id = ?",
        (tenant_id,),
    ).fetchone()["total"]
    return max(0, row["agreed_yearly_price"] - paid)

