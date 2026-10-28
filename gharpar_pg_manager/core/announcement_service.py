"""Announcement operations for owners and tenants."""
from datetime import datetime
from database import get_connection


def add_announcement(pg_id, message):
    """FEATURE: Add Announcement
    Add a non-empty announcement to a PG."""
    message = message.strip()
    if not message:
        raise ValueError("Announcement cannot be empty.")
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO announcements (pg_id, message, created_at) VALUES (?, ?, ?)",
            (pg_id, message, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_announcements_for_pg(pg_id):
    """FEATURE: List Announcements
    Return announcements newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM announcements WHERE pg_id = ? ORDER BY created_at DESC, id DESC",
        (pg_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_announcement(announcement_id):
    """FEATURE: Delete Announcement
    Delete an announcement by its ID."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
        conn.commit()
    finally:
        conn.close()
