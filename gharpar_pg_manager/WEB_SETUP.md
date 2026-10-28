# GharPar PG Manager — Web UI setup

This project keeps the existing Python/Tkinter app and SQLite business logic, and adds an optional React/Vite owner web workspace.

## Requirements
- Python 3.10+ (standard-library backend; no Python packages required)
- Node.js with npm

## Start the web version on Windows
Open two PowerShell windows in the extracted `gharpar_pg_manager` folder.

### PowerShell window 1 — Python API
```powershell
cd "C:\path\to\gharpar_pg_manager"
py web_api.py
```
Keep this window open while using the web UI.

### PowerShell window 2 — React frontend
```powershell
cd "C:\path\to\gharpar_pg_manager\web"
npm install
npm run dev
```
Open the local URL Vite prints (normally `http://127.0.0.1:5173`).

## Demo login
If you are using the included demo database, the owner account is:
- Username: `owner`
- Password: `owner123`

The web API uses the existing `pg.db` and does not automatically reset or reseed it. If you have a database you want to preserve, back it up before replacing the project files. Do not run `seed_data.py` unless you intentionally want to create/reset demo data.

## Notes
- The web workspace currently supports owner accounts. Tenant login remains in the existing desktop application.
- The UI includes the owner overview, property blueprint, maintenance ticket status updates, and announcements.
- The API binds to `127.0.0.1:8765`; Vite proxies `/api` requests to it.
