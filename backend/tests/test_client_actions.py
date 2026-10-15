"""Persistent synthetic profile edits and reversible archive actions."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4
from staff_fixtures import TestClient, create_app


class ClientActionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'actions.sqlite3'
        self.client = TestClient(create_app(self.database, seed=False))
        self.client.__enter__()
        self.original = self.client.post('/api/preference-requests', json=dict(
            fictional_client_name='Test Alex River', email='alex@example.com', phone='202-555-0100',
            category='individual', preferred_contact_method='email', fictional_data_only=True,
            session_format='Telehealth', preferred_counselor_id='rachel-kim',
            preferred_date=(date.today() + timedelta(days=7)).isoformat(), preferred_time='Morning',
            time_zone='America/New_York', request_key=str(uuid4()))).json()
        self.path = '/api/inquiries/' + self.original['inquiry_id']
        self.edit = dict(fictional_client_name='Test Alex Updated', category='family',
                         preferred_contact_method='phone', status='reviewing', expected_revision=0,
                         fictional_data_only=True, email='updated@example.org', phone='202-555-0101')

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def record(self):
        return self.client.get(self.path + '/management').json()

    def action(self, name, revision=None):
        return self.client.post(self.path + '/' + name,
                                json=dict(confirmed=True, expected_revision=self.record()['revision'] if revision is None else revision))

    def test_edit_preserves_identity_original_preferences_and_history(self):
        before = self.record()
        response = self.client.post(self.path + '/edit', json=self.edit)
        self.assertEqual(response.status_code, 200, response.text)
        record = response.json()
        for field in ('inquiry_id', 'created_at', 'original_inquiry', 'converted_at', 'portal_status'):
            self.assertEqual(record[field], before[field])
        self.assertEqual(record['fictional_client_name'], 'Test Alex Updated')
        self.assertEqual(record['preferences']['email'], 'updated@example.org')
        self.assertEqual(record['preferences']['phone'], '2025550101')
        self.assertEqual(record['preferences']['preferred_date'], before['preferences']['preferred_date'])
        self.assertEqual(record['history'][:-1], before['history'])
        self.assertEqual(record['history'][-1]['action'], 'Client details updated')
        self.assertEqual(record['revision'], 1)
        self.assertEqual(self.client.get(self.path).json(), self.original)
        # No change -> no fabricated activity or revision bump.
        retry = self.client.post(self.path + '/edit', json=dict(self.edit, expected_revision=1)).json()
        self.assertEqual(retry, record)

    def test_validation_rejects_real_contacts_immutable_and_unsupported_fields(self):
        before = self.record()
        for change in [dict(email='person@gmail.com'), dict(phone='2028675309'),
                       dict(fictional_client_name='Alex River'), dict(category='clinical'),
                       dict(status='established'), dict(created_at='2000-01-01'),
                       dict(converted_at='2000-01-01'), dict(assigned_counselor='x'),
                       dict(fictional_data_only=False), dict(expected_revision=-1)]:
            self.assertEqual(self.client.post(self.path + '/edit', json=dict(self.edit, **change)).status_code, 422)
        self.assertEqual(self.record(), before)
        for action in ('archive', 'restore'):
            for payload in [{}, {'confirmed': False, 'expected_revision': 0},
                            {'confirmed': True, 'expected_revision': 0, 'delete': True}]:
                self.assertEqual(self.client.post(self.path + '/' + action, json=payload).status_code, 422)
        self.assertEqual(self.record(), before)

    def test_stale_or_competing_edits_cannot_overwrite(self):
        def save(_):
            return self.client.post(self.path + '/edit', json=self.edit).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(save, range(2))), [200, 409])
        self.assertEqual(len(self.record()['history']), 2)
        self.assertEqual(self.action('archive', revision=0).status_code, 409)
        self.assertIsNone(self.record()['archived_at'])

    def test_prospective_archive_is_reversible_and_protects_history(self):
        before = self.record()
        archived = self.action('archive').json()
        self.assertIsNotNone(archived['archived_at'])
        self.assertEqual(archived['original_inquiry'], before['original_inquiry'])
        self.assertEqual(self.client.get('/api/prospective-clients').json(), [])
        self.assertEqual(self.client.get('/api/prospective-clients?include_archived=true').json(), [archived])
        self.assertEqual(self.client.get(self.path).json(), self.original)
        self.assertEqual(self.action('archive').status_code, 409)
        self.assertEqual(self.client.post(self.path + '/edit', json=dict(self.edit, expected_revision=1)).status_code, 409)
        self.assertEqual(self.client.post(self.path + '/convert', json={'confirmed': True}).status_code, 409)
        self.assertEqual(self.client.post(self.path + '/portal-status', json={'portal_status': 'Sent'}).status_code, 409)
        restored = self.action('restore').json()
        self.assertIsNone(restored['archived_at'])
        self.assertEqual(self.client.get('/api/prospective-clients').json(), [restored])
        self.assertEqual([e['action'] for e in restored['history']], ['Inquiry created', 'Client archived', 'Client restored'])
        self.assertEqual(self.action('restore').status_code, 409)

    def test_established_archive_edit_and_restore_retain_conversion_and_invitation(self):
        self.client.post(self.path + '/portal-status', json={'portal_status': 'Sent'})
        converted = self.client.post(self.path + '/convert', json={'confirmed': True}).json()
        self.assertEqual(self.client.post(self.path + '/edit', json=self.edit).status_code, 409)
        edited = self.client.post(self.path + '/edit', json=dict(self.edit, expected_revision=converted['revision'])).json()
        archived = self.action('archive').json()
        self.assertEqual(self.client.get('/api/clients').json(), [])
        self.assertEqual(self.client.get('/api/clients?include_archived=true').json(), [archived])
        restored = self.action('restore').json()
        self.assertEqual(restored['converted_at'], converted['converted_at'])
        self.assertEqual(restored['portal_status'], 'Sent')
        self.assertEqual(restored['preferences'], edited['preferences'])
        self.assertEqual(restored['history'][:len(converted['history'])], converted['history'])
        self.assertEqual(self.client.get('/api/clients').json(), [restored])
        self.assertEqual(self.client.get('/api/prospective-clients').json(), [])

    def test_restart_retains_edits_archive_original_and_history(self):
        self.client.post(self.path + '/edit', json=self.edit)
        archived = self.action('archive').json()
        self.client.__exit__(None, None, None)
        self.client = TestClient(create_app(self.database, seed=False))
        self.client.__enter__()
        self.assertEqual(self.record(), archived)
        self.assertEqual(self.client.get('/api/prospective-clients').json(), [])
        self.assertEqual(self.client.get('/api/prospective-clients?include_archived=true').json(), [archived])
        self.assertEqual(self.client.get(self.path).json(), self.original)
        self.assertEqual(self.action('restore').status_code, 200)

    def test_legacy_records_keep_names_and_additive_migration_preserves_rows(self):
        old = self.client.post('/api/inquiries', json=dict(fictional_client_name='Legacy Demo',
            category='general', preferred_contact_method='email', fictional_data_only=True)).json()
        path = '/api/inquiries/' + old['inquiry_id']
        payload = dict(self.edit, fictional_client_name='Legacy Demo', category='family')
        payload.pop('email'); payload.pop('phone')
        response = self.client.post(path + '/edit', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['preferences'])
        # Emulate the previous schema on the original preference inquiry.
        self.client.__exit__(None, None, None)
        with sqlite3.connect(self.database) as db:
            db.execute('DROP TABLE client_record_state')
        self.client = TestClient(create_app(self.database, seed=False))
        self.client.__enter__()
        self.assertEqual(self.client.get(self.path).json(), self.original)
        self.assertEqual(self.record()['revision'], 0)
        self.assertIsNone(self.record()['archived_at'])

    def test_missing_records_invalid_ids_and_no_hard_delete(self):
        for action in ('edit', 'archive', 'restore'):
            payload = self.edit if action == 'edit' else dict(confirmed=True, expected_revision=0)
            self.assertEqual(self.client.post('/api/inquiries/' + str(uuid4()) + '/' + action, json=payload).status_code, 404)
            self.assertEqual(self.client.post('/api/inquiries/not-an-id/' + action, json=payload).status_code, 422)
        self.assertEqual(self.client.delete(self.path).status_code, 405)
