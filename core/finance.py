"""Tenant financial calculations using whole rupees and ISO dates."""
from datetime import date
from database import get_connection
from core.pricing import get_installment_schedule


def get_tenant_financials(tenant_id, today=None):
    """FEATURE: Tenant Financials
    Return payment totals, installment status, and newest-first payment history."""
    if today is None:
        today = date.today()
    tenant, payment_rows = _load_financial_records(tenant_id)
    if tenant is None:
        return None
    payments, total_paid = _make_payment_history(payment_rows)
    return _calculate_financials(tenant, payments, total_paid, today)


def _load_financial_records(tenant_id):
    """FEATURE: Tenant Financials
    Load a tenant record and its payments from SQLite."""
    conn = get_connection()
    tenant = conn.execute(
        "SELECT id, name, join_date, agreed_yearly_price FROM tenants WHERE id = ?",
        (tenant_id,),
    ).fetchone()
    payments = []
    if tenant is not None:
        payments = conn.execute(
            "SELECT amount, paid_on, mode FROM payments "
            "WHERE tenant_id = ? ORDER BY paid_on DESC, id DESC",
            (tenant_id,),
        ).fetchall()
    conn.close()
    return tenant, payments


def _make_payment_history(payment_rows):
    """FEATURE: Tenant Financials
    Convert payment rows to dictionaries and total their amounts."""
    payments = []
    total_paid = 0
    for row in payment_rows:
        payments.append({
            "amount": row["amount"], "paid_on": row["paid_on"], "mode": row["mode"]
        })
        total_paid += row["amount"]
    return payments, total_paid


def _calculate_financials(tenant, payments, total_paid, today):
    """FEATURE: Tenant Financials
    Calculate expected payments, overdue balance, remaining balance, and next due."""
    join_date = date.fromisoformat(tenant["join_date"])
    agreed_price = tenant["agreed_yearly_price"]
    schedule = get_installment_schedule(agreed_price, join_date)
    expected = _expected_amount(schedule, today)
    next_due = _next_due_date(schedule, total_paid)
    overdue = max(0, expected - total_paid)
    return {
        "tenant_id": tenant["id"], "name": tenant["name"],
        "join_date": tenant["join_date"], "agreed_yearly_price": agreed_price,
        "total_paid": total_paid, "due_left": max(0, agreed_price - total_paid),
        "expected_till_today": expected, "overdue_amount": overdue,
        "next_due_date": next_due, "status": "overdue" if overdue > 0 else "ok",
        "payments": payments,
    }


def _expected_amount(schedule, today):
    """FEATURE: Tenant Financials
    Sum installments due on or before the selected date."""
    expected = 0
    for due_date, amount in schedule:
        if due_date <= today:
            expected += amount
    return expected


def _next_due_date(schedule, total_paid):
    """FEATURE: Tenant Financials
    Return the first installment date not covered by cumulative payments."""
    cumulative = 0
    for due_date, amount in schedule:
        cumulative += amount
        if cumulative > total_paid:
            return due_date.isoformat()
    return None
