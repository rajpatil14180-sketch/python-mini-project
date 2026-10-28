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


## Web UI prototype

The first React + TypeScript UI prototype lives in `web/`. It demonstrates the intended Airbnb-inspired owner workspace, simple floor-plan grid, bed detail panel, and owner-defined monthly rent presentation. This prototype currently uses sample display data; it does not yet read from or write to the SQLite database. The existing Python/Tkinter application remains the current connected application until the API and database migration are implemented and tested.

To run the prototype, install Node.js, open PowerShell in `web`, run `npm install`, then run `npm run dev`.

Monthly rent calculation helpers are in `core/monthly_rent.py`. They are currently additive and tested independently; the existing annual-price database and services have not yet been migrated. Do not treat this first milestone as a complete rent-system migration.
