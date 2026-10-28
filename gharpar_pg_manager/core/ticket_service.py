"""Maintenance ticket operations."""
from datetime import date, datetime
from database import get_connection
import config


def create_ticket(tenant_id, category, description, urgency):
    """FEATURE: Create Ticket
    Create an open ticket using the PG assigned to the tenant."""
    if category not in config.TICKET_CATEGORIES:
        raise ValueError("Invalid ticket category.")
    if urgency not in config.TICKET_URGENCIES:
        raise ValueError("Invalid ticket urgency.")
    if not description.strip():
        raise ValueError("Description cannot be empty.")
    conn = get_connection()
    try:
        pg_id = _get_tenant_pg_id(conn, tenant_id)
        created_at = datetime.now().isoformat(timespec="seconds")
        cursor = conn.execute(
            "INSERT INTO tickets (tenant_id, pg_id, category, description, urgency, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'Open', ?)",
            (tenant_id, pg_id, category, description.strip(), urgency, created_at),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _get_tenant_pg_id(conn, tenant_id):
    """FEATURE: Create Ticket
    Find the PG assigned to an active tenant."""
    row = conn.execute(
        "SELECT r.pg_id FROM tenants t JOIN beds b ON b.id = t.bed_id "
        "JOIN rooms r ON r.id = b.room_id WHERE t.id = ? AND t.is_active = 1",
        (tenant_id,),
    ).fetchone()
    if row is None:
        raise ValueError("An active tenant with an assigned bed is required.")
    return row["pg_id"]


def get_tickets_for_pg(pg_id, include_resolved=False):
    """FEATURE: Owner Tickets
    Return PG tickets oldest first with tenant, bed, and age details."""
    conn = get_connection()
    query = (
        "SELECT tickets.*, tenants.name AS tenant_name, rooms.room_no, beds.label AS bed_label "
        "FROM tickets JOIN tenants ON tenants.id = tickets.tenant_id "
        "LEFT JOIN beds ON beds.id = tenants.bed_id "
        "LEFT JOIN rooms ON rooms.id = beds.room_id WHERE tickets.pg_id = ? "
    )
    if not include_resolved:
        query += "AND tickets.status != 'Resolved' "
    query += "ORDER BY tickets.created_at ASC, tickets.id ASC"
    rows = conn.execute(query, (pg_id,)).fetchall()
    conn.close()
    today = date.today()
    result = []
    for row in rows:
        item = dict(row)
        created = datetime.fromisoformat(item["created_at"]).date()
        item["age_in_days"] = max(0, (today - created).days)
        result.append(item)
    return result


def get_tickets_for_tenant(tenant_id):
    """FEATURE: Tenant Tickets
    Return one tenant's tickets newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tickets WHERE tenant_id = ? ORDER BY created_at DESC, id DESC",
        (tenant_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_ticket_status(ticket_id, new_status):
    """FEATURE: Update Ticket
    Update a ticket status and its resolution timestamp."""
    if new_status not in config.TICKET_STATUSES:
        raise ValueError("Invalid ticket status.")
    resolved_at = datetime.now().isoformat(timespec="seconds") if new_status == "Resolved" else None
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE tickets SET status = ?, resolved_at = ? WHERE id = ?",
            (new_status, resolved_at, ticket_id),
        )
        conn.commit()
    finally:
        conn.close()
