"""Assignment ownership, local staff authorization and durable caseloads."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest
from fastapi.testclient import TestClient as AnonymousClient
from staff_fixtures import TestClient, create_app, ADMIN_KEY, RACHEL_KEY, MELISSA_KEY


class AssignmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'clients.sqlite3'
        self.client = TestClient(create_app(self.database, seed=False))
        self.client.__enter__()
        self.inquiry = self.client.post('/api/inquiries', json=dict(fictional_client_name='Test Alex River',
            category='individual', preferred_contact_method='email', fictional_data_only=True)).json()
        self.path = '/api/inquiries/' + self.inquiry['inquiry_id']

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def record(self):
        return self.client.get(self.path + '/management').json()

    def convert(self):
        return self.client.post(self.path + '/convert', json={'confirmed': True}).json()

    def assign(self, counselor='rachel-kim', revision=None):
        if revision is None:
            revision = self.record()['revision']
        return self.client.post(self.path + '/assignment', json=dict(confirmed=True,
            counselor_id=counselor, expected_revision=revision))

    def sign_in(self, key):
        self.assertEqual(self.client.post('/api/staff/login', json={'key': key}).status_code, 200)

    def test_assignment_confirmation_established_eligibility_and_no_implicit_assignment(self):
        self.assertEqual(self.assign().status_code, 409)
        converted = self.convert()
        self.assertIsNone(converted['assigned_counselor_id'])
        for payload in [{}, {'confirmed': False, 'counselor_id': 'rachel-kim', 'expected_revision': 1},
                        {'confirmed': True, 'expected_revision': 1},
                        {'confirmed': True, 'counselor_id': 'rachel-kim', 'expected_revision': 1, 'role': 'administrator'}]:
            self.assertEqual(self.client.post(self.path + '/assignment', json=payload).status_code, 422)
        for counselor in ['unknown', 'denice-colson', 'sarah-williams']:
            self.assertEqual(self.assign(counselor).status_code, 422)
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE counselors SET active = 0 WHERE counselor_id = 'melissa-smith'")
        self.assertEqual(self.assign('melissa-smith').status_code, 422)
        self.assertEqual(self.record(), converted)

    def test_assign_change_remove_preserve_original_conversion_and_history(self):
        converted = self.convert()
        first = self.assign().json()
        self.assertEqual(first['assigned_counselor_id'], 'rachel-kim')
        self.assertEqual(first['history'][:-1], converted['history'])
        self.assertEqual(first['history'][-1]['action'], 'Counselor assignment updated')
        self.assertEqual(self.assign().json(), first)  # No-change updates do not invent activity.
        second = self.assign('melissa-smith').json()
        cleared = self.assign(None).json()
        self.assertIsNone(cleared['assigned_counselor_id'])
        for record in [first, second, cleared]:
            self.assertEqual(record['original_inquiry'], self.inquiry)
            self.assertEqual(record['inquiry_id'], self.inquiry['inquiry_id'])
            self.assertEqual(record['created_at'], self.inquiry['created_at'])
            self.assertEqual(record['converted_at'], converted['converted_at'])
        self.assertEqual(cleared['revision'], 4)
        self.assertEqual(len(cleared['history']), 5)

    def test_competing_assignments_and_stale_edit_versions(self):
        converted = self.convert()
        with ThreadPoolExecutor(max_workers=2) as pool:
            codes = list(pool.map(lambda cid: self.assign(cid, converted['revision']).status_code,
                                  ['rachel-kim', 'melissa-smith']))
        self.assertEqual(sorted(codes), [200, 409])
        self.assertEqual(len(self.record()['history']), 3)
        self.assertEqual(self.assign(None, converted['revision']).status_code, 409)

    def test_counselor_ownership_and_admin_only_mutations(self):
        self.convert(); self.assign()
        self.sign_in(RACHEL_KEY)
        own = self.client.get('/api/counselors/rachel-kim/clients').json()
        self.assertEqual(own['active_count'], 1)
        self.assertEqual(own['clients'][0]['inquiry_id'], self.inquiry['inquiry_id'])
        self.assertEqual(self.client.get(self.path + '/management').status_code, 200)
        self.assertEqual(self.client.get(self.path).status_code, 200)
        for path in ['/api/inquiries', '/api/clients', '/api/prospective-clients', '/api/counselors/melissa-smith/clients']:
            self.assertEqual(self.client.get(path).status_code, 403)
        for action in ['assignment', 'convert', 'edit', 'archive', 'restore', 'portal-status']:
            self.assertEqual(self.client.post(self.path + '/' + action, json={}).status_code, 403)
        self.sign_in(MELISSA_KEY)
        self.assertEqual(self.client.get('/api/counselors/melissa-smith/clients').json()['active_count'], 0)
        self.assertEqual(self.client.get(self.path + '/management').status_code, 404)
        self.assertEqual(self.client.get(self.path, headers={'X-Role': 'administrator'}).status_code, 404)
        self.sign_in(ADMIN_KEY); self.assign('melissa-smith')
        self.sign_in(RACHEL_KEY)
        self.assertEqual(self.client.get(self.path + '/management').status_code, 404)
        self.assertEqual(self.client.get('/api/counselors/rachel-kim/clients').json()['active_count'], 0)
        self.sign_in(MELISSA_KEY)
        self.assertEqual(self.client.get(self.path + '/management').status_code, 200)

    def test_anonymous_cannot_read_records_and_foreign_origin_cannot_write(self):
        anonymous = AnonymousClient(self.client.app)
        for path in ['/api/inquiries', '/api/clients', '/api/prospective-clients', self.path,
                     self.path + '/management', '/api/counselors', '/api/counselors/rachel-kim/clients']:
            response = anonymous.get(path)
            self.assertEqual(response.status_code, 401, response.text)
            self.assertNotIn('Test Alex River', response.text)
            self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertEqual(anonymous.post('/api/inquiries', json=dict(fictional_client_name='Test Public Request',
            category='general', preferred_contact_method='email', fictional_data_only=True)).status_code, 201)
        self.assertEqual(self.client.post(self.path + '/convert', json={'confirmed': True},
                                         headers={'Origin': 'https://example.com'}).status_code, 403)
        self.assertEqual(anonymous.post('/api/staff/login', json={'key': ADMIN_KEY},
                                        headers={'Origin': 'https://elcccdev.github.io'}).status_code, 403)

    def test_archived_removed_from_caseload_and_cannot_be_assigned(self):
        self.convert(); self.assign()
        record = self.record()
        self.client.post(self.path + '/archive', json={'confirmed': True, 'expected_revision': record['revision']})
        self.assertEqual(self.assign(None).status_code, 409)
        self.assertEqual(self.client.get('/api/counselors/rachel-kim/clients').json()['active_count'], 0)
        self.sign_in(RACHEL_KEY)
        self.assertEqual(self.client.get(self.path + '/management').status_code, 404)
        self.sign_in(ADMIN_KEY)
        archived = self.record()
        self.client.post(self.path + '/restore', json={'confirmed': True, 'expected_revision': archived['revision']})
        self.assertEqual(self.record()['assigned_counselor_id'], 'rachel-kim')
        self.assertEqual(self.client.get('/api/counselors/rachel-kim/clients').json()['active_count'], 1)

    def test_restart_retains_assignment_but_old_session_is_rejected(self):
        self.convert(); self.assign()
        before = self.record()
        old_cookies = dict(self.client.cookies)
        self.client.__exit__(None, None, None)
        self.client = TestClient(create_app(self.database, seed=False))
        self.client.__enter__()
        anonymous = AnonymousClient(self.client.app, cookies=old_cookies)
        self.assertEqual(anonymous.get(self.path + '/management').status_code, 401)
        self.assertEqual(self.record(), before)
        self.assertEqual(self.client.get('/api/counselors/rachel-kim/clients').json()['active_count'], 1)

    def test_local_session_cookie_logout_and_rate_limit(self):
        response = self.client.post('/api/staff/login', json={'key': ADMIN_KEY})
        cookie = response.headers['set-cookie'].lower()
        self.assertIn('httponly', cookie); self.assertIn('samesite=strict', cookie)
        self.assertEqual(self.client.post('/api/staff/logout').status_code, 200)
        self.assertEqual(self.client.get('/api/staff/session').status_code, 401)
        for _ in range(10):
            self.assertEqual(self.client.post('/api/staff/login', json={'key': 'wrong-key'}).status_code, 401)
        self.assertEqual(self.client.post('/api/staff/login', json={'key': 'wrong-key'}).status_code, 429)

    def test_inactive_staff_account_is_denied(self):
        self.convert(); self.assign(); self.sign_in(RACHEL_KEY)
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE counselors SET active = 0 WHERE counselor_id = 'rachel-kim'")
        self.assertEqual(self.client.get('/api/staff/session').status_code, 403)
        self.assertEqual(self.client.get(self.path + '/management').status_code, 403)
