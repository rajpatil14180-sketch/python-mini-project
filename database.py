"""Database connection and table creation for the PG Manager app."""
import sqlite3
import config


_TABLE_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('owner', 'tenant'))
    )""",
    """CREATE TABLE IF NOT EXISTS pgs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL REFERENCES users(id),
        name TEXT NOT NULL,
        address TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pg_id INTEGER NOT NULL REFERENCES pgs(id),
        room_no INTEGER NOT NULL,
        has_attached_bath INTEGER NOT NULL CHECK(has_attached_bath IN (0, 1))
    )""",
    """CREATE TABLE IF NOT EXISTS beds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL REFERENCES rooms(id),
        label TEXT NOT NULL,
        base_yearly_price INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        bed_id INTEGER REFERENCES beds(id),
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        join_date TEXT NOT NULL,
        deposit INTEGER NOT NULL,
        agreed_yearly_price INTEGER NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1))
    )""",
    """CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL REFERENCES tenants(id),
        amount INTEGER NOT NULL,
        paid_on TEXT NOT NULL,
        mode TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL REFERENCES tenants(id),
        pg_id INTEGER NOT NULL REFERENCES pgs(id),
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        urgency TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        resolved_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pg_id INTEGER NOT NULL REFERENCES pgs(id),
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""",
]


def get_connection(db_name=None):
    """FEATURE: Database Setup
    Open SQLite with foreign keys enabled and rows accessible by column name."""
    if db_name is None:
        db_name = config.DB_NAME
    conn = sqlite3.connect(db_name, uri=db_name.startswith("file:"))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(db_name=None):
    """FEATURE: Database Setup
    Create the eight tables and partial unique index if they do not exist."""
    conn = get_connection(db_name)
    cursor = conn.cursor()
    for statement in _TABLE_STATEMENTS:
        cursor.execute(statement)
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS one_active_tenant_per_bed "
        "ON tenants(bed_id) WHERE is_active = 1 AND bed_id IS NOT NULL"
    )
    conn.commit()
    conn.close()
