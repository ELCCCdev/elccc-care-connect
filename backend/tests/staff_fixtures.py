"""Explicit synthetic staff credentials for disposable test databases only."""
from fastapi.testclient import TestClient as BaseClient
from app.main import create_app as factory

ADMIN_KEY = 'synthetic-administrator-test-key-only'
RACHEL_KEY = 'synthetic-rachel-test-key-only'
MELISSA_KEY = 'synthetic-melissa-test-key-only'
CREDENTIALS = [dict(role='administrator', counselor_id=None, key=ADMIN_KEY),
               dict(role='counselor', counselor_id='rachel-kim', key=RACHEL_KEY),
               dict(role='counselor', counselor_id='melissa-smith', key=MELISSA_KEY)]


def create_app(*args, **kwargs):
    return factory(*args, **kwargs, staff_credentials=CREDENTIALS)


class TestClient(BaseClient):
    def __enter__(self):
        result = super().__enter__()
        response = self.post('/api/staff/login', json={'key': ADMIN_KEY})
        assert response.status_code == 200, response.text
        return result
