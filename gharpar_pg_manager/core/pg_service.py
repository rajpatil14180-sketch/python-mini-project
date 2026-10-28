"""Read-only queries for PGs, rooms, beds, and summaries."""
from datetime import date
from database import get_connection
from core.finance import get_tenant_financials


def get_pgs_for_owner(owner_id):
    """FEATURE: Owner PG List
    Return the owner's PGs with bed counts and overdue tenant counts."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT p.id, p.name, p.address, COUNT(b.id) AS total_beds, "
        "SUM(CASE WHEN t.id IS NOT NULL THEN 1 ELSE 0 END) AS occupied_beds "
        "FROM pgs p LEFT JOIN rooms r ON r.pg_id = p.id "
        "LEFT JOIN beds b ON b.room_id = r.id "
        "LEFT JOIN tenants t ON t.bed_id = b.id AND t.is_active = 1 "
        "WHERE p.owner_id = ? GROUP BY p.id ORDER BY p.id",
        (owner_id,),
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        item = dict(row)
        item["total_beds"] = item["total_beds"] or 0
        item["occupied_beds"] = item["occupied_beds"] or 0
        item["overdue_tenants"] = _count_overdue_tenants(item["id"], date.today())
        results.append(item)
    return results


def _count_overdue_tenants(pg_id, today):
    """FEATURE: Owner PG List
    Count active tenants in a PG who have overdue payments."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT t.id FROM tenants t JOIN beds b ON b.id = t.bed_id "
        "JOIN rooms r ON r.id = b.room_id WHERE r.pg_id = ? AND t.is_active = 1",
        (pg_id,),
    ).fetchall()
    conn.close()
    count = 0
    for row in rows:
        info = get_tenant_financials(row["id"], today)
        if info and info["overdue_amount"] > 0:
            count += 1
    return count


def get_pg_layout(pg_id):
    """FEATURE: PG Blueprint
    Return nested room and bed details with current occupancy status."""
    conn = get_connection()
    rooms = conn.execute(
        "SELECT id AS room_id, room_no, has_attached_bath FROM rooms "
        "WHERE pg_id = ? ORDER BY room_no",
        (pg_id,),
    ).fetchall()
    result = []
    for room in rooms:
        beds = _get_room_beds(conn, room["room_id"])
        result.append({
            "room_id": room["room_id"],
            "room_no": room["room_no"],
            "has_attached_bath": room["has_attached_bath"],
            "beds": beds,
        })
    conn.close()
    return result


def _get_room_beds(conn, room_id):
    """FEATURE: PG Blueprint
    Return bed details and derived status for one room."""
    rows = conn.execute(
        "SELECT b.id AS bed_id, b.label, b.base_yearly_price, "
        "t.id AS tenant_id, t.name AS tenant_name "
        "FROM beds b LEFT JOIN tenants t ON t.bed_id = b.id AND t.is_active = 1 "
        "WHERE b.room_id = ? ORDER BY b.label",
        (room_id,),
    ).fetchall()
    beds = []
    for row in rows:
        item = dict(row)
        item["status"] = "empty"
        if item["tenant_id"] is not None:
            info = get_tenant_financials(item["tenant_id"])
            item["status"] = "overdue" if info["overdue_amount"] > 0 else "occupied"
        beds.append(item)
    return beds


def get_bed_details(bed_id):
    """FEATURE: Bed Details
    Return the bed, room, PG, active tenant, and tenant financial details."""
    data = _load_bed_row(bed_id)
    if data is None:
        return None
    tenant = _tenant_dict(data) if data["tenant_id"] is not None else None
    financials = get_tenant_financials(data["tenant_id"]) if tenant else None
    bed = {
        "bed_id": data["bed_id"], "label": data["label"],
        "base_yearly_price": data["base_yearly_price"],
    }
    return {
        "bed": bed, "room_no": data["room_no"], "pg_name": data["pg_name"],
        "tenant": tenant, "financials": financials,
    }


def _load_bed_row(bed_id):
    """FEATURE: Bed Details
    Load one bed and its active tenant profile fields."""
    conn = get_connection()
    row = conn.execute(
        "SELECT b.id AS bed_id, b.label, b.base_yearly_price, r.room_no, "
        "r.has_attached_bath, p.name AS pg_name, t.id AS tenant_id, "
        "t.name AS tenant_name, t.phone, t.join_date, t.deposit, t.agreed_yearly_price "
        "FROM beds b JOIN rooms r ON r.id = b.room_id "
        "JOIN pgs p ON p.id = r.pg_id "
        "LEFT JOIN tenants t ON t.bed_id = b.id AND t.is_active = 1 "
        "WHERE b.id = ?",
        (bed_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _tenant_dict(data):
    """FEATURE: Bed Details
    Select the tenant profile fields shown in the bed details popup."""
    return {
        "tenant_id": data["tenant_id"],
        "name": data["tenant_name"],
        "phone": data["phone"],
        "join_date": data["join_date"],
        "deposit": data["deposit"],
        "agreed_yearly_price": data["agreed_yearly_price"],
    }


def get_pg_summary(pg_id, today=None):
    """FEATURE: PG Summary
    Return the total beds, occupancy, expected payments, collections, and overdue."""
    if today is None:
        today = date.today()
    conn = get_connection()
    rows = conn.execute(
        "SELECT b.id AS bed_id, t.id AS tenant_id FROM rooms r "
        "JOIN beds b ON b.room_id = r.id "
        "LEFT JOIN tenants t ON t.bed_id = b.id AND t.is_active = 1 "
        "WHERE r.pg_id = ?",
        (pg_id,),
    ).fetchall()
    conn.close()
    totals = {"total_beds": len(rows), "occupied_beds": 0,
              "total_expected": 0, "total_collected": 0, "total_overdue": 0}
    for row in rows:
        if row["tenant_id"] is None:
            continue
        totals["occupied_beds"] += 1
        info = get_tenant_financials(row["tenant_id"], today)
        totals["total_expected"] += info["expected_till_today"]
        totals["total_collected"] += info["total_paid"]
        totals["total_overdue"] += info["overdue_amount"]
    return totals


# TODO(ask): SPEC does not define a core function for finding a tenant's bed and PG.
# This existing helper is used by the tenant dashboard until that contract is clarified.
def get_tenant_home_details(tenant_id):
    """FEATURE: Tenant Home
    Return the tenant's PG, room, and bed details for the tenant dashboard."""
    conn = get_connection()
    row = conn.execute(
        "SELECT t.id AS tenant_id, t.name, t.phone, t.join_date, "
        "b.id AS bed_id, b.label, r.room_no, p.id AS pg_id, p.name AS pg_name "
        "FROM tenants t LEFT JOIN beds b ON b.id = t.bed_id "
        "LEFT JOIN rooms r ON r.id = b.room_id "
        "LEFT JOIN pgs p ON p.id = r.pg_id WHERE t.id = ?",
        (tenant_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
