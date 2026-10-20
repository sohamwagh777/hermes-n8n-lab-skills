#!/usr/bin/env python3
"""Mock enrichment API for HERMES-LAB n8n practice (lab 06).
GET /enrich?email=<addr>  -> 200 {"email","company","seniority","score","source"}
Deterministic by email domain. Unknown domains -> 404 {"error":"unknown_domain"}.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DOMAINS = {
    "acme.com": {"company": "Acme Corp", "seniority": "mid", "score": 61},
    "globex.io": {"company": "Globex International", "seniority": "senior", "score": 84},
    "initech.dev": {"company": "Initech", "seniority": "junior", "score": 33},
}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/enrich":
            self._send(404, {"error": "no_route", "path": u.path})
            return
        qs = parse_qs(u.query)
        email = (qs.get("email") or [""])[0].strip().lower()
        if "@" not in email:
            self._send(400, {"error": "bad_email", "email": email})
            return
        domain = email.split("@", 1)[1]
        rec = DOMAINS.get(domain)
        if rec is None:
            self._send(404, {"error": "unknown_domain", "domain": domain})
            return
        self._send(200, {"email": email, **rec, "source": "mock-enrich-v1"})

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[mock-enrich]", fmt % args, flush=True)

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8899), H).serve_forever()
