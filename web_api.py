"""Small standard-library HTTP API for the React/Vite frontend.
Run from the project root with: python web_api.py
Uses the existing SQLite database and core services; it does not seed or reset data.
"""
import json
import secrets
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from database import create_tables, get_connection
from core.auth import login
from core.pg_service import get_pgs_for_owner, get_pg_layout, get_pg_summary, get_bed_details
from core.finance import get_tenant_financials
from core.ticket_service import get_tickets_for_pg, update_ticket_status
from core.announcement_service import get_announcements_for_pg, add_announcement

TOKENS = {}


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    raise TypeError(type(value).__name__)


class Handler(BaseHTTPRequestHandler):
    server_version = "GharParAPI/1.1"

    def log_message(self, fmt, *args):
        print("[GharPar API] " + fmt % args)

    def _send(self, status, payload):
        body = json.dumps(payload, default=_json_default).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        if status != 204:
            self.wfile.write(body)

    def _body(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size > 1_000_000:
            raise ValueError("Request body is too large.")
        raw = self.rfile.read(size).decode("utf-8") if size else "{}"
        data = json.loads(raw or "{}")
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")
        return data

    def _user(self):
        token = self.headers.get("Authorization", "").removeprefix("Bearer ")
        return TOKENS.get(token)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        user = self._user()
        if not user:
            return self._send(401, {"error": "Please sign in to continue."})
        if user["role"] != "owner":
            return self._send(403, {"error": "The web workspace currently supports owner accounts."})
        try:
            if path == "/api/me":
                return self._send(200, {"username": user["username"], "role": user["role"]})
            if path == "/api/pgs":
                return self._send(200, get_pgs_for_owner(user["user_id"]))
            parts = path.split("/")
            if len(parts) >= 4 and parts[1:3] == ["api", "pgs"] and parts[3].isdigit():
                pg_id = int(parts[3])
                if not any(p["id"] == pg_id for p in get_pgs_for_owner(user["user_id"])):
                    return self._send(404, {"error": "Property not found."})
                if len(parts) == 5 and parts[4] == "layout":
                    return self._send(200, get_pg_layout(pg_id))
                if len(parts) == 5 and parts[4] == "summary":
                    return self._send(200, get_pg_summary(pg_id))
                if len(parts) == 5 and parts[4] == "tickets":
                    return self._send(200, get_tickets_for_pg(pg_id, include_resolved=True))
                if len(parts) == 5 and parts[4] == "announcements":
                    return self._send(200, get_announcements_for_pg(pg_id))
            if len(parts) == 4 and parts[1:3] == ["api", "beds"] and parts[3].isdigit():
                bed_id = int(parts[3])
                conn = get_connection()
                try:
                    row = conn.execute("SELECT p.owner_id FROM beds b JOIN rooms r ON r.id=b.room_id JOIN pgs p ON p.id=r.pg_id WHERE b.id=?", (bed_id,)).fetchone()
                finally:
                    conn.close()
                if row is None or row["owner_id"] != user["user_id"]:
                    return self._send(404, {"error": "Bed not found."})
                details = get_bed_details(bed_id)
                return self._send(200, details) if details is not None else self._send(404, {"error": "Bed not found."})
            if len(parts) == 4 and parts[1:3] == ["api", "tenants"] and parts[3].isdigit():
                tenant_id = int(parts[3])
                conn = get_connection()
                try:
                    row = conn.execute("SELECT p.owner_id FROM tenants t JOIN beds b ON b.id=t.bed_id JOIN rooms r ON r.id=b.room_id JOIN pgs p ON p.id=r.pg_id WHERE t.id=?", (tenant_id,)).fetchone()
                finally:
                    conn.close()
                if row is None or row["owner_id"] != user["user_id"]:
                    return self._send(404, {"error": "Tenant not found."})
                details = get_tenant_financials(tenant_id)
                return self._send(200, details) if details is not None else self._send(404, {"error": "Tenant not found."})
            return self._send(404, {"error": "Endpoint not found."})
        except (ValueError, TypeError) as exc:
            return self._send(400, {"error": str(exc)})
        except Exception as exc:
            return self._send(500, {"error": str(exc)})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            data = self._body()
            if path == "/api/login":
                result = login(str(data.get("username", "")), str(data.get("password", "")))
                if not result:
                    return self._send(401, {"error": "Incorrect username or password, or account inactive."})
                if result["role"] != "owner":
                    return self._send(403, {"error": "Tenant web access is not available yet. Use the desktop app for tenant accounts."})
                token = secrets.token_urlsafe(32)
                TOKENS[token] = result
                return self._send(200, {"token": token, "user": {"username": result["username"], "role": result["role"]}})
            user = self._user()
            if not user:
                return self._send(401, {"error": "Please sign in to continue."})
            if user["role"] != "owner":
                return self._send(403, {"error": "Owner access required."})
            if path == "/api/logout":
                token = self.headers.get("Authorization", "").removeprefix("Bearer ")
                TOKENS.pop(token, None)
                return self._send(200, {"ok": True})
            parts = path.split("/")
            if len(parts) == 5 and parts[1:3] == ["api", "pgs"] and parts[3].isdigit() and parts[4] == "announcements":
                pg_id = int(parts[3])
                if not any(p["id"] == pg_id for p in get_pgs_for_owner(user["user_id"])):
                    return self._send(404, {"error": "Property not found."})
                announcement_id = add_announcement(pg_id, str(data.get("message", "")))
                return self._send(201, {"id": announcement_id})
            if len(parts) == 5 and parts[1:3] == ["api", "tickets"] and parts[3].isdigit() and parts[4] == "status":
                ticket_id = int(parts[3])
                new_status = str(data.get("status", ""))
                conn = get_connection()
                try:
                    row = conn.execute("SELECT pg_id FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
                finally:
                    conn.close()
                if row is None or not any(p["id"] == row["pg_id"] for p in get_pgs_for_owner(user["user_id"])):
                    return self._send(404, {"error": "Ticket not found."})
                update_ticket_status(ticket_id, new_status)
                return self._send(200, {"ok": True})
            return self._send(404, {"error": "Endpoint not found."})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self._send(400, {"error": str(exc)})
        except Exception as exc:
            return self._send(500, {"error": str(exc)})


def main():
    create_tables()
    host, port = "127.0.0.1", 8765
    print(f"GharPar API running at http://{host}:{port} (Ctrl+C to stop)", flush=True)
    try:
        ThreadingHTTPServer((host, port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nGharPar API stopped.", flush=True)


if __name__ == "__main__":
    main()
