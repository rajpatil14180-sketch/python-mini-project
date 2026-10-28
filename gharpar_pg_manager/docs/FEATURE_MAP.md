# Feature Map

| Feature | What the user sees | File | Function(s) |
|---|---|---|---|
| Application Startup | Desktop application opens | `main.py` | `main` |
| Application Window | Main app window and navigation container | `ui/app.py` | `GharParApp.__init__` |
| Login Screen | Username and password form | `ui/login_screen.py` | `LoginScreen.__init__`, `LoginScreen.submit` |
| Login Navigation | Owner and tenant see their own home screen | `ui/app.py` | `show_login`, `show_owner_list`, `login_success` |
| Password Hashing | Passwords are stored as salted PBKDF2 hashes | `core/auth.py` | `hash_password`, `verify_password` |
| Login | Valid account is authenticated; inactive tenants are rejected | `core/auth.py` | `login` |
| Database Setup | Required SQLite tables and active-bed index exist | `database.py` | `get_connection`, `create_tables` |
| Late-Join Pricing | Suggested yearly price reflects the configured discount | `core/pricing.py` | `get_late_join_discount_percent`, `calculate_agreed_price` |
| Installment Schedule | Yearly price is split into 12 monthly due dates | `core/pricing.py` | `add_months`, `get_installment_schedule` |
| Tenant Financials | Paid, expected, remaining, overdue, next due date, and payment history | `core/finance.py` | `get_tenant_financials` |
| Owner PG List | Owner sees each PG, occupancy, and overdue tenant count | `core/pg_service.py`, `ui/owner_pg_list.py` | `get_pgs_for_owner`, `OwnerPGList` |
| Owner PG View | Blueprint on the left and task buttons on the right | `core/pg_service.py`, `ui/owner_pg_view.py` | `get_pg_summary`, `OwnerPGView` |
| PG Summary | Total beds, occupancy, expected, collected, and overdue totals | `core/pg_service.py` | `get_pg_summary` |
| PG Blueprint | Room and bed grid with empty, occupied, and overdue border colours | `core/pg_service.py`, `ui/blueprint_panel.py` | `get_pg_layout`, `BlueprintPanel.refresh`, `BlueprintPanel.open_bed` |
| Bed Details | Bed profile, tenant profile, finance, and payment history in a Frame-based screen hosted in a Tkinter window | `core/pg_service.py`, `ui/bed_detail_window.py`, `ui/blueprint_panel.py` | `get_bed_details`, `BedDetailWindow`, `BlueprintPanel.open_bed` |
| Add Tenant | Owner creates tenant login and tenancy with an editable agreed price in a Frame-based screen | `core/tenant_service.py`, `ui/add_tenant_window.py`, `ui/bed_detail_window.py` | `add_tenant`, `AddTenantWindow.save`, `BedDetailWindow.add_tenant` |
| Record Payment | Owner records a positive whole-rupee payment with ISO date and allowed mode through a form | `core/tenant_service.py`, `ui/bed_detail_window.py` | `add_payment`, `BedDetailWindow.record_payment` |
| Vacate Tenant | Owner releases a bed while preserving tenant history | `core/tenant_service.py`, `ui/bed_detail_window.py` | `vacate_tenant`, `BedDetailWindow.vacate` |
| Create Ticket | Tenant creates a maintenance ticket using category and urgency dropdowns plus a description field | `core/ticket_service.py`, `ui/tenant_tickets.py` | `create_ticket`, `TenantTickets.raise_ticket` |
| Owner Tickets | Owner sees unresolved tickets oldest first and their age | `core/ticket_service.py`, `ui/owner_tickets_panel.py` | `get_tickets_for_pg`, `OwnerTicketsPanel.refresh` |
| Tenant Tickets | Tenant sees their ticket history | `core/ticket_service.py`, `ui/tenant_tickets.py` | `get_tickets_for_tenant`, `TenantTickets.refresh` |
| Update Ticket | Owner changes ticket status | `core/ticket_service.py`, `ui/owner_tickets_panel.py` | `update_ticket_status`, `OwnerTicketsPanel.update_selected` |
| Add Announcement | Owner posts a non-empty notice for a PG using a form | `core/announcement_service.py`, `ui/owner_announcements_panel.py` | `add_announcement`, `OwnerAnnouncementsPanel.add` |
| Owner Announcements | Owner manages notices in the PG task panel | `ui/owner_announcements_panel.py` | `OwnerAnnouncementsPanel.__init__`, `refresh`, `add`, `delete` |
| List Announcements | Owner and tenant see PG notices newest first | `core/announcement_service.py`, `ui/owner_announcements_panel.py`, `ui/tenant_home.py` | `get_announcements_for_pg`, `OwnerAnnouncementsPanel.refresh`, `TenantHome` |
| Delete Announcement | Owner deletes a notice | `core/announcement_service.py`, `ui/owner_announcements_panel.py` | `delete_announcement`, `OwnerAnnouncementsPanel.delete` |
| Tenant Home | Tenant sees room, bed, price, finance, payments, announcements, and tickets | `core/pg_service.py`, `ui/tenant_home.py` | `get_tenant_home_details`, `TenantHome` |
| Seed Data | Sample owner, 11 tenants, PGs, rooms, beds, tickets, and notices | `seed_data.py` | `main`, `insert_users`, `_insert_tenant_user`, `insert_pgs_rooms_beds`, `_insert_room_beds`, `insert_tenant_with_payments`, `_get_pay_count`, `_insert_scheduled_payments`, `insert_all_tenants`, `insert_tickets`, `insert_announcements`, `_populate_database`, `_print_summary` |
| UI Helpers | Reusable table and frame helpers | `ui/widgets.py` | `clear_frame`, `make_treeview` |
| Pricing Tests | Discount tier boundaries, month-end clamping, leap-year dates, installment count, and remainder are checked | `tests/test_pricing.py` | `PricingTests` methods |
| Finance Tests | Overdue totals, fully paid status, next due date, and password verification are checked | `tests/test_finance.py` | `FinanceTests` methods |
| Service Tests | Tenant, payment, PG layout, ticket status, announcement, and invalid-input behaviour are checked | `tests/test_services.py` | `ServiceTests` methods |
| Reservations and tenant self-booking | Not included in the MVP | — | — |

## TODO for specification clarification

- `docs/SPEC.md` does not define a core function contract for finding a tenant's PG, room, and bed for the Tenant Home screen. The existing `get_tenant_home_details` helper remains in use until that contract is clarified.
- R2 says not to add unlisted function names, while R7 asks for short beginner-friendly functions. Existing private helpers are used to keep functions short. Confirm whether private helpers are allowed before removing or renaming them.
