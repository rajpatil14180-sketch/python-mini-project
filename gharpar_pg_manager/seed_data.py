"""Seed script for the sample data described in docs/SPEC.md."""
from datetime import date, timedelta
import config
from database import create_tables, get_connection
from core.auth import hash_password
from core.pricing import calculate_agreed_price, get_installment_schedule


_TENANT_NAMES = [
    "Amit Sharma", "Priya Patel", "Rahul Deshmukh", "Sneha Kulkarni",
    "Vikram Joshi", "Neha Gupta", "Arjun Singh", "Kavita Reddy",
    "Rohan Mehta", "Meera Nair", "Deepak Patil",
]
_PG_DATA = [
    ("Sunrise PG", "12 MG Road, Panchavati, Nashik, Maharashtra"),
    ("Green Nest PG", "45 College Lane, Gangapur, Nashik, Maharashtra"),
]
_BASE_PRICES = [
    [(230000, 220000), (210000, 200000), (150000, 140000), (135000, 125000)],
    [(225000, 215000), (205000, 195000), (160000, 150000), (140000, 130000)],
]
_OCCUPANTS = [
    (0, "R1A", -25, "up_to_date", 0), (0, "R1B", -10, "late_3", 1),
    (0, "R2A", 0, "late_1", 2), (0, "R3A", 12, "up_to_date", 3),
    (0, "R3B", 33, "ahead", 4), (0, "R4A", 62, "late_1", 5),
    (1, "R1A", -18, "up_to_date", 6), (1, "R2A", 4, "late_1", 7),
    (1, "R2B", 28, "up_to_date", 8), (1, "R3A", 47, "late_1", 9),
    (1, "R4A", 80, "up_to_date", 10),
]
_TICKETS = [
    (0, "Plumbing", "Leaking tap in bathroom", "High", "Open", 2, None),
    (1, "Wi-Fi", "Internet speed very slow", "Medium", "In Progress", 7, None),
    (2, "Cleaning", "Common area needs cleaning", "Low", "Resolved", 15, 5),
    (3, "Electrical", "Fan not working properly", "High", "Open", 1, None),
    (6, "Furniture", "Broken chair in room", "Medium", "Open", 5, None),
    (7, "Plumbing", "Shower not draining well", "Low", "In Progress", 12, None),
    (8, "Wi-Fi", "Cannot connect to network", "High", "Resolved", 20, 10),
    (9, "Other", "Noisy neighbours complaint", "Medium", "Open", 8, None),
]


def insert_users(cursor):
    """FEATURE: Seed Data
    Insert the owner account and eleven tenant accounts."""
    owner_hash, owner_salt = hash_password("owner123")
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
        ("owner", owner_hash, owner_salt, "owner"),
    )
    owner_id = cursor.lastrowid
    tenant_users = []
    for full_name in _TENANT_NAMES:
        username = full_name.split()[0].lower()
        tenant_users.append(_insert_tenant_user(cursor, username, full_name))
    return owner_id, tenant_users


def _insert_tenant_user(cursor, username, full_name):
    """FEATURE: Seed Data
    Insert one sample tenant account and return its profile details."""
    password_hash, salt = hash_password("tenant123")
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
        (username, password_hash, salt, "tenant"),
    )
    index = _TENANT_NAMES.index(full_name)
    phone = f"98765{43210 + index:05d}"
    return cursor.lastrowid, full_name, phone


def insert_pgs_rooms_beds(cursor, owner_id):
    """FEATURE: Seed Data
    Insert both PGs with four rooms and two beds per room."""
    pg_ids = []
    bed_map = {}
    for pg_idx, (name, address) in enumerate(_PG_DATA):
        cursor.execute(
            "INSERT INTO pgs (owner_id, name, address) VALUES (?, ?, ?)",
            (owner_id, name, address),
        )
        pg_id = cursor.lastrowid
        pg_ids.append(pg_id)
        for room_no, prices in enumerate(_BASE_PRICES[pg_idx], start=1):
            _insert_room_beds(cursor, pg_idx, pg_id, room_no, prices, bed_map)
    return pg_ids, bed_map


def _insert_room_beds(cursor, pg_idx, pg_id, room_no, prices, bed_map):
    """FEATURE: Seed Data
    Insert one room and its A and B beds with configured prices."""
    cursor.execute(
        "INSERT INTO rooms (pg_id, room_no, has_attached_bath) VALUES (?, ?, ?)",
        (pg_id, room_no, int(room_no <= 2)),
    )
    room_id = cursor.lastrowid
    for label, price in zip(("A", "B"), prices):
        cursor.execute(
            "INSERT INTO beds (room_id, label, base_yearly_price) VALUES (?, ?, ?)",
            (room_id, label, price),
        )
        bed_map[(pg_idx, f"R{room_no}{label}")] = (cursor.lastrowid, price)


def insert_tenant_with_payments(cursor, user_id, bed_id, full_name, phone,
                                join_date, base_price, pay_state, today):
    """FEATURE: Seed Data
    Insert a tenant and the payments for the requested sample payment state."""
    agreed_price = calculate_agreed_price(base_price, join_date)
    schedule = get_installment_schedule(agreed_price, join_date)
    cursor.execute(
        "INSERT INTO tenants (user_id, bed_id, name, phone, join_date, deposit, "
        "agreed_yearly_price, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
        (user_id, bed_id, full_name, phone, join_date.isoformat(), 10000, agreed_price),
    )
    tenant_id = cursor.lastrowid
    due_count = sum(1 for due_date, _ in schedule if due_date <= today)
    pay_count = _get_pay_count(pay_state, due_count)
    _insert_scheduled_payments(cursor, tenant_id, schedule, pay_count)
    return tenant_id


def _get_pay_count(pay_state, due_count):
    """FEATURE: Seed Data
    Calculate how many installments the sample tenant has paid."""
    if pay_state == "up_to_date":
        return due_count
    if pay_state == "ahead":
        return min(due_count + 1, 12)
    if pay_state == "late_1":
        return max(0, due_count - 1)
    if pay_state == "late_3":
        return max(0, due_count - 3)
    return 0


def _insert_scheduled_payments(cursor, tenant_id, schedule, pay_count):
    """FEATURE: Seed Data
    Insert each paid installment with its scheduled due date."""
    for index in range(pay_count):
        due_date, amount = schedule[index]
        mode = "upi" if index % 2 == 0 else "cash"
        cursor.execute(
            "INSERT INTO payments (tenant_id, amount, paid_on, mode) VALUES (?, ?, ?, ?)",
            (tenant_id, amount, due_date.isoformat(), mode),
        )


def insert_all_tenants(cursor, tenant_users, pg_ids, bed_map, today):
    """FEATURE: Seed Data
    Insert the eleven tenants listed in the project specification."""
    tenant_data = []
    for pg_idx, bed_key, offset, pay_state, user_index in _OCCUPANTS:
        user_id, full_name, phone = tenant_users[user_index]
        bed_id, base_price = bed_map[(pg_idx, bed_key)]
        join_date = config.COLLEGE_START_DATE + timedelta(days=offset)
        tenant_id = insert_tenant_with_payments(
            cursor, user_id, bed_id, full_name, phone, join_date,
            base_price, pay_state, today,
        )
        tenant_data.append((tenant_id, pg_ids[pg_idx], full_name))
    return tenant_data


def insert_tickets(cursor, tenant_data, today):
    """FEATURE: Seed Data
    Insert eight maintenance tickets with varied ages and statuses."""
    for t_idx, cat, desc, urgency, status, age, resolved_age in _TICKETS:
        tenant_id, pg_id, _ = tenant_data[t_idx]
        created_at = (today - timedelta(days=age)).isoformat()
        resolved_at = (today - timedelta(days=resolved_age)).isoformat() if resolved_age else None
        cursor.execute(
            "INSERT INTO tickets (tenant_id, pg_id, category, description, urgency, status, "
            "created_at, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tenant_id, pg_id, cat, desc, urgency, status, created_at, resolved_at),
        )


def insert_announcements(cursor, pg_ids, today):
    """FEATURE: Seed Data
    Insert two announcements for each PG."""
    items = [
        (pg_ids[0], "Monthly maintenance scheduled for common areas.", 3),
        (pg_ids[0], "New Wi-Fi router installed. Contact admin for password.", 1),
        (pg_ids[1], "Water supply off on Sunday for tank cleaning.", 5),
        (pg_ids[1], "Please maintain silence during exam period.", 2),
    ]
    for pg_id, message, age in items:
        created_at = (today - timedelta(days=age)).isoformat()
        cursor.execute(
            "INSERT INTO announcements (pg_id, message, created_at) VALUES (?, ?, ?)",
            (pg_id, message, created_at),
        )


def main():
    """FEATURE: Seed Data
    Reset the sample tables and insert all sample records."""
    create_tables()
    conn = get_connection()
    for table in ("payments", "tickets", "announcements", "tenants", "beds", "rooms", "pgs", "users"):
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
    _populate_database()
    _print_summary()


def _populate_database():
    """FEATURE: Seed Data
    Insert all sample data in one database transaction."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()
    owner_id, tenant_users = insert_users(cursor)
    pg_ids, bed_map = insert_pgs_rooms_beds(cursor, owner_id)
    tenant_data = insert_all_tenants(cursor, tenant_users, pg_ids, bed_map, today)
    insert_tickets(cursor, tenant_data, today)
    insert_announcements(cursor, pg_ids, today)
    conn.commit()
    conn.close()


def _print_summary():
    """FEATURE: Seed Data
    Print the counts created by the seed script."""
    conn = get_connection()
    counts = {}
    for table in ("pgs", "rooms", "beds", "tenants", "tickets", "announcements"):
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()
    print(f"Database '{config.DB_NAME}' created successfully.")
    print("  Owner:         1 (owner / owner123)")
    for table, count in counts.items():
        print(f"  {table.title():14} {count}")


if __name__ == "__main__":
    main()
