"""Local test credentials and short-lived staff sessions, not production identity."""
import hashlib
import tempfile
import json
import os
from pathlib import Path
import secrets
import threading
import time
from typing import Optional
from fastapi import HTTPException, Request

COUNSELORS = [
    ('denice-colson', 'Dr. Denice Colson', False), ('staci-stephens', 'Staci Stephens', True),
    ('melissa-smith', 'Melissa Smith', True), ('jonathan-reeves', 'Jonathan Reeves', True),
    ('rachel-kim', 'Rachel Kim', True), ('amy-parker', 'Amy Parker', True),
    ('brian-holloway', 'Brian Holloway', True), ('sarah-williams', 'Sarah Williams', False),
    ('maria-gonzalez', 'Maria Gonzalez', True), ('kevin-brooks', 'Kevin Brooks', True),
    ('lauren-bennett', 'Lauren Bennett', True), ('thomas-green', 'Thomas Green', True),
]
COOKIE = 'elccc_local_staff'
LOCAL_ORIGINS = {'http://127.0.0.1:5500', 'http://localhost:5500',
                 'http://127.0.0.1:8000', 'http://localhost:8000'}


def credential_path():
    location = str(Path(__file__).resolve().parent.parent)
    folder = 'elccc-local-access-' + hashlib.sha256(location.encode()).hexdigest()[:16]
    return Path(os.environ.get('ELCCC_ACCESS_PATH', str(Path(tempfile.gettempdir()) / folder / 'staff-access.json')))


def local_credentials(path: Optional[Path] = None):
    path = path or credential_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.exists():
        credentials = [{'role': 'administrator', 'counselor_id': None, 'key': secrets.token_urlsafe(32)}]
        credentials += [{'role': 'counselor', 'counselor_id': cid, 'key': secrets.token_urlsafe(32)}
                        for cid, _, _ in COUNSELORS]
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(descriptor, 'w') as stream:
                json.dump(credentials, stream)
    return json.loads(path.read_text())


class StaffSessions:
    def __init__(self, credentials):
        self.credentials = credentials
        self.sessions = {}
        self.attempts = {}
        self.lock = threading.Lock()

    def login(self, key, client):
        now = time.monotonic()
        with self.lock:
            # Bound in-memory rate-limit state; this is a single-process local server.
            self.attempts = {host: entry for host, entry in self.attempts.items() if entry[0] > now - 60}
            start, attempts = self.attempts.get(client, (now, 0))
            if attempts >= 10:
                raise HTTPException(429, 'Too many sign-in attempts. Wait one minute and retry.')
            self.attempts[client] = (start, attempts + 1)
            principal = None
            for item in self.credentials:
                if secrets.compare_digest(key.encode(), item['key'].encode()):
                    principal = {k: item[k] for k in ('role', 'counselor_id')}
            if principal is None:
                raise HTTPException(401, 'Local staff access key not recognized.')
            self.attempts.pop(client, None)
            self.sessions = {token: entry for token, entry in self.sessions.items() if entry[1] > now}
            token = secrets.token_urlsafe(32)
            self.sessions[token] = (principal, now + 8 * 60 * 60)
            return token, principal

    def principal(self, request: Request):
        with self.lock:
            entry = self.sessions.get(request.cookies.get(COOKIE))
            if entry is None or entry[1] <= time.monotonic():
                raise HTTPException(401, 'Open local staff access to continue. Sessions expire after eight hours or a backend restart.')
            return entry[0]

    def logout(self, request):
        with self.lock:
            self.sessions.pop(request.cookies.get(COOKIE), None)


if __name__ == '__main__':
    # Explicit command for the local operator; never called or logged by the server.
    for account in local_credentials():
        print((account['counselor_id'] or 'administrator') + ': ' + account['key'])
