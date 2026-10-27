# PG MANAGER — SPEC (single source of truth)

## 1. What this is
Desktop app in plain Python (tkinter + sqlite3) for a college mini project.
One owner manages 2 PGs. Tenants and owner log in on the same laptop; the
account role decides which screens open. Each PG is a 4 BHK: 4 rooms, 2 beds
per room. Rooms 1 and 2 have an attached bathroom; rooms 3 and 4 share one
common washroom.

## 2. HARD RULES FOR THE AI (obey in every task)
R1. Standard library only: sqlite3, hashlib, secrets, datetime, calendar,
    tkinter, tkinter.ttk, tkinter.messagebox, unittest. No pip installs.
    (PyInstaller is used only in the final packaging step, when I ask.)
R2. Names in this file (files, tables, columns, functions, dict keys) are
    contracts. Never rename or add anything not listed here.
R3. If something is unspecified, do NOT guess. Write "# TODO(ask): ..." and
    tell me in your reply.
R4. Edit ONLY the files named in the current task.
R5. Money = whole rupees as int. Never float. Dates stored as 'YYYY-MM-DD' text.
R6. Every function starts with a docstring whose first line is
    "FEATURE: <feature name>" (names from docs/FEATURE_MAP.md), followed by one
    plain-English sentence. Comments must be simple enough for a beginner.
R7. Beginner style: simple functions under 30 lines, no decorators, no
    clever one-liners. Classes only for tkinter screens (Frame subclasses).
R8. UI files never import sqlite3 or run SQL. They call core/ functions only.
R9. Never say something works unless you ran it. Paste the real terminal output.
R10. At the end of every task, update docs/FEATURE_MAP.md with a table row per
     feature: feature | what the user sees | file | function(s).

## 3. Files
Root: main.py, config.py, database.py, seed_data.py, README.md
core/: auth.py, pricing.py, finance.py, pg_service.py, tenant_service.py,
       ticket_service.py, announcement_service.py
ui/: app.py, widgets.py, login_screen.py, owner_pg_list.py, owner_pg_view.py,
     blueprint_panel.py, bed_detail_window.py, add_tenant_window.py,
     owner_tickets_panel.py, owner_announcements_panel.py, tenant_home.py,
     tenant_tickets.py
tests/: test_pricing.py, test_finance.py, test_services.py
docs/: SPEC.md, FEATURE_MAP.md, VIVA_NOTES.md

## 4. config.py constants
DB_NAME = "pg.db"
COLLEGE_START_DATE = date(2026, 8, 1)
LATE_JOIN_DISCOUNTS = [(0, 0), (30, 5), (60, 10), (90, 15), (999999, 20)]
  meaning: days_late <= first number -> discount percent is the second number
BED_BORDER_COLOURS = {"empty": "#2e9e5b", "occupied": "#2b6cb0", "overdue": "#c53030"}
TICKET_CATEGORIES = ["Plumbing","Electrical","Wi-Fi","Cleaning","Furniture","Other"]
TICKET_URGENCIES = ["Low","Medium","High"]
TICKET_STATUSES = ["Open","In Progress","Resolved"]
PAYMENT_MODES = ["cash","upi"]

## 5. Database (SQLite, foreign keys ON for every connection)
users(id, username UNIQUE, password_hash, salt, role)  role in owner/tenant
pgs(id, owner_id->users, name, address)
rooms(id, pg_id->pgs, room_no, has_attached_bath 0/1)
beds(id, room_id->rooms, label, base_yearly_price)
tenants(id, user_id->users, bed_id->beds, name, phone, join_date, deposit,
        agreed_yearly_price, is_active 0/1)
payments(id, tenant_id->tenants, amount, paid_on, mode)
tickets(id, tenant_id->tenants, pg_id->pgs, category, description, urgency,
        status, created_at, resolved_at NULL allowed)
announcements(id, pg_id->pgs, message, created_at)
Partial unique index: one ACTIVE tenant per bed
  CREATE UNIQUE INDEX one_active_tenant_per_bed ON tenants(bed_id)
  WHERE is_active = 1 AND bed_id IS NOT NULL;
"Occupied" is NEVER stored; it is derived from an active tenant on the bed.

## 6. Money rules
Late-join price:
  days_late = (join_date - COLLEGE_START_DATE).days
  discount % from LATE_JOIN_DISCOUNTS (first row where days_late <= limit)
  agreed_price = base * (100 - pct) // 100, then rounded DOWN to nearest 100
  The agreed price is stored on the tenant at join time and never recomputed.
Installments:
  installment = agreed_price // 12; the remainder is added to the LAST one.
  Installment k (1..12) is due on join_date + (k-1) months, same day of month;
  if that month is shorter, use the month's last day.
  total_paid = sum of payments
  expected_till_today = sum of installments whose due date <= today
  overdue_amount = max(0, expected_till_today - total_paid)
  due_left = max(0, agreed_price - total_paid)
  next_due_date = due date of the first installment not fully covered by
                  total_paid (None if all covered)
  A tenant is OVERDUE when overdue_amount > 0.
A payment larger than due_left is rejected (ValueError). Amount must be > 0.

## 7. Function contracts (core/)
auth.py
  hash_password(password, salt_hex=None) -> (hash_hex, salt_hex)   # pbkdf2_hmac sha256, 100000 rounds
  verify_password(password, hash_hex, salt_hex) -> bool
  login(username, password) -> {"user_id","username","role","tenant_id"} or None
     (inactive tenants cannot log in; tenant_id is None for owner)
pricing.py
  add_months(d, n) -> date
  get_late_join_discount_percent(join_date) -> int
  calculate_agreed_price(base_price, join_date) -> int
  get_installment_schedule(agreed_price, join_date) -> list of 12 (due_date, amount)
finance.py
  get_tenant_financials(tenant_id, today=None) -> dict with keys:
    tenant_id, name, join_date, agreed_yearly_price, total_paid, due_left,
    expected_till_today, overdue_amount, next_due_date, status ("ok"/"overdue"),
    payments (list of dicts: amount, paid_on, mode; newest first)
pg_service.py
  get_pgs_for_owner(owner_id) -> list of dicts: id, name, address,
    total_beds, occupied_beds, overdue_tenants
  get_pg_layout(pg_id) -> list of rooms: {room_id, room_no, has_attached_bath,
    beds: [{bed_id, label, base_yearly_price, status ("empty"/"occupied"/"overdue"),
    tenant_id, tenant_name}]}
  get_bed_details(bed_id) -> {bed, room_no, pg_name, tenant (dict or None),
    financials (dict or None)}
  get_pg_summary(pg_id) -> {total_beds, occupied_beds, total_expected,
    total_collected, total_overdue}
tenant_service.py
  add_tenant(bed_id, name, phone, join_date, deposit, agreed_price, username,
             password) -> tenant_id   (ValueError if bed already has an active tenant)
  vacate_tenant(tenant_id) -> None   (is_active = 0; history kept)
  add_payment(tenant_id, amount, paid_on, mode) -> payment_id
ticket_service.py
  create_ticket(tenant_id, category, description, urgency) -> ticket_id
  get_tickets_for_pg(pg_id, include_resolved=False) -> list, oldest first, each
    with age_in_days, tenant_name, room_no, bed_label
  get_tickets_for_tenant(tenant_id) -> list, newest first
  update_ticket_status(ticket_id, new_status) -> None
announcement_service.py
  add_announcement(pg_id, message) -> id
  get_announcements_for_pg(pg_id) -> list, newest first
  delete_announcement(announcement_id) -> None

## 8. Screens (ui/)
Login -> by role:
OWNER: PG list (card per PG) -> PG view. PG view = blueprint area on the left,
  right-side task bar with 3 buttons: Blueprint | Tickets | Announcements.
  Blueprint = grid of room boxes; each room shows its 2 beds as rectangles with
  a coloured border (empty/occupied/overdue) plus tenant name and a text label.
  Common washroom shown as a labelled box. Click a bed:
    - occupied/overdue: popup with profile, join date, agreed yearly price,
      payments with dates, total paid, due left, next due date, overdue amount;
      buttons: Record Payment, Vacate.
    - empty: popup with bed info and an Add Tenant button; the form pre-fills
      the late-join price (editable).
  Tickets = unresolved tickets oldest first with age in days and status change.
  Announcements = post a notice, list notices, delete a notice.
TENANT: Home = my room and bed, agreed yearly price, installments status,
  payment history, and the PG's announcements. Second tab = Raise Ticket + My Tickets.

## 9. Sample data (seed_data.py; dates relative to COLLEGE_START_DATE or today)
Owner: owner / owner123. Tenants: password tenant123, username = first name lowercase.
PGs: "Sunrise PG", "Green Nest PG" (Nashik addresses).
Base prices, bed A / bed B:
  Sunrise:    R1 230000/220000, R2 210000/200000, R3 150000/140000, R4 135000/125000
  Green Nest: R1 225000/215000, R2 205000/195000, R3 160000/150000, R4 140000/130000
Occupied beds (join offset in days from COLLEGE_START_DATE, payment state):
  Sunrise (6): R1A -25 up_to_date | R1B -10 late_3 | R2A 0 late_1 |
               R3A +12 up_to_date | R3B +33 ahead | R4A +62 late_1
  Green Nest (5): R1A -18 up_to_date | R2A +4 late_1 | R2B +28 up_to_date |
               R3A +47 late_1 | R4A +80 up_to_date
Payment states: up_to_date = pays all installments due; ahead = due + 1;
  late_1 = due - 1; late_3 = due - 3 (never below 0).
  Each payment is dated on its installment's due date.
Agreed price for each tenant = calculate_agreed_price(base, join_date). Deposit 10000.
Indian names, fake 10-digit phone numbers. Join dates must not be after today.
8 tickets across both PGs, ages 1 to 20 days, mixed categories/urgencies/statuses.
2 announcements per PG.
