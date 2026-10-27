# GharPar PG Manager

A beginner-friendly desktop PG management application built with Python's standard library, Tkinter, and SQLite.

## Requirements
- Python 3.10 or newer recommended
- No pip packages required

## Run
1. Open a terminal in this folder.
2. Create/reset the sample database: `python seed_data.py`
3. Start the application: `python main.py`

`seed_data.py` resets the app tables to the demo dataset, so do not run it if you need to keep real tenant/payment records.

## Demo accounts
- Owner: `owner` / `owner123`
- Tenant: `amit` / `tenant123` (other tenants use their first name in lowercase)

## Run tests
`python -m unittest discover -s tests -v`

## Notes
The MVP supports owner and tenant login, PG/bed viewing, tenant financial summaries, maintenance tickets, and announcements. Tenant self-booking and reservations are intentionally excluded.
