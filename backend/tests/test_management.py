"""Persistent fictional client conversion and independent invitation tracking."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4
from staff_fixtures import TestClient, create_app


class ManagementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'inquiries.sqlite3'
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()
        self.inquiry = self.client.get('/api/inquiries').json()[0]
        self.path = '/api/inquiries/' + self.inquiry['inquiry_id']

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def test_conversion_preserves_original_and_history(self):
        self.assertEqual(len(self.client.get('/api/prospective-clients').json()), 3)
        self.assertEqual(self.client.get('/api/clients').json(), [])
        converted = self.client.post(self.path + '/convert', json={'confirmed': True})
        self.assertEqual(converted.status_code, 200)
        record = converted.json()
        self.assertEqual(record['inquiry_id'], self.inquiry['inquiry_id'])
        self.assertEqual(record['created_at'], self.inquiry['created_at'])
        self.assertIsNotNone(record['converted_at'])
        self.assertEqual([e['action'] for e in record['history']],
                         ['Inquiry created', 'Converted to client'])
        self.assertEqual(len(self.client.get('/api/prospective-clients').json()), 2)
        self.assertEqual(self.client.get('/api/clients').json(), [record])
        self.assertEqual(self.client.get(self.path).json(), self.inquiry)
        self.assertEqual(len(self.client.get('/api/inquiries').json()), 3)
        self.assertEqual(self.client.get(self.path + '/management').json(), record)

    def test_confirmation_and_duplicate_prevention(self):
        for payload in [{}, {'confirmed': False}, {'confirmed': True, 'extra': 'rejected'}]:
            self.assertEqual(self.client.post(self.path + '/convert', json=payload).status_code, 422)
        first = self.client.post(self.path + '/convert', json={'confirmed': True}).json()
        response = self.client.post(self.path + '/convert', json={'confirmed': True})
        self.assertEqual(response.status_code, 409)
        self.assertIn('already', response.json()['detail'])
        self.assertEqual(self.client.get(self.path + '/management').json(), first)

    def test_competing_conversions_only_create_one_event(self):
        def convert(_):
            return self.client.post(self.path + '/convert', json={'confirmed': True}).status_code
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(convert, range(2)))
        self.assertEqual(sorted(results), [200, 409])
        self.assertEqual(len(self.client.get('/api/clients').json()), 1)
        history = self.client.get(self.path + '/management').json()['history']
        self.assertEqual(sum(e['action'] == 'Converted to client' for e in history), 1)

    def test_invitation_before_and_after_conversion_is_independent(self):
        record = self.client.get(self.path + '/management').json()
        self.assertEqual(record['portal_status'], 'Not Sent')
        for status in ['Sent', 'Activated', 'Not Sent', 'Sent']:
            record = self.client.post(self.path + '/portal-status', json={'portal_status': status}).json()
            self.assertEqual(record['portal_status'], status)
            self.assertIsNone(record['converted_at'])
        converted = self.client.post(self.path + '/convert', json={'confirmed': True}).json()
        self.assertEqual(converted['portal_status'], 'Sent')
        self.assertEqual(converted['history'][:-1], record['history'])
        activated = self.client.post(self.path + '/portal-status', json={'portal_status': 'Activated'}).json()
        self.assertEqual(activated['converted_at'], converted['converted_at'])
        self.assertEqual(activated['portal_status'], 'Activated')
        same = self.client.post(self.path + '/portal-status', json={'portal_status': 'Activated'}).json()
        self.assertEqual(same, activated)  # No duplicate history for unchanged tracking.

    def test_restart_persistence(self):
        self.client.post(self.path + '/portal-status', json={'portal_status': 'Sent'})
        record = self.client.post(self.path + '/convert', json={'confirmed': True}).json()
        self.client.__exit__(None, None, None)
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()
        self.assertEqual(self.client.get('/api/clients').json(), [record])
        self.assertEqual(len(self.client.get('/api/prospective-clients').json()), 2)
        self.assertEqual(self.client.get(self.path + '/management').json(), record)

    def test_invalid_updates_missing_records_and_cors(self):
        for payload in [{}, {'portal_status': 'Delivered'}, {'portal_status': 'Sent', 'send': True}]:
            self.assertEqual(self.client.post(self.path + '/portal-status', json=payload).status_code, 422)
        missing = '/api/inquiries/' + str(uuid4())
        self.assertEqual(self.client.get(missing + '/management').status_code, 404)
        self.assertEqual(self.client.post(missing + '/convert', json={'confirmed': True}).status_code, 404)
        self.assertEqual(self.client.post(missing + '/portal-status', json={'portal_status': 'Sent'}).status_code, 404)
        self.assertEqual(self.client.get('/api/inquiries/not-a-uuid/management').status_code, 422)
        response = self.client.post(self.path + '/portal-status', json={'portal_status': 'Sent'},
                                    headers={'Origin': 'http://127.0.0.1:5500'})
        self.assertEqual(response.headers['access-control-allow-origin'], 'http://127.0.0.1:5500')

    def test_existing_phase_two_database_is_preserved(self):
        # Emulate a Phase 2 file with no management tables; migration is additive.
        self.client.__exit__(None, None, None)
        with sqlite3.connect(self.database) as connection:
            connection.execute('DROP TABLE inquiry_history')
            connection.execute('DROP TABLE inquiry_management')
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()
        self.assertEqual(self.client.get(self.path).json(), self.inquiry)
        self.assertEqual(len(self.client.get('/api/prospective-clients').json()), 3)
        self.assertEqual(self.client.get('/api/clients').json(), [])
        self.assertEqual(self.client.get(self.path + '/management').json()['portal_status'], 'Not Sent')
