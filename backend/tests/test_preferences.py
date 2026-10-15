"""Synthetic preference requests remain attached to the original inquiry."""
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from staff_fixtures import TestClient, create_app


class PreferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'test.sqlite3'
        self.client = TestClient(create_app(self.database, seed=False))
        self.client.__enter__()
        self.payload = dict(fictional_client_name='Test Alex River', email='alex@example.com',
                            phone='202-555-0100', category='individual', preferred_contact_method='email',
                            fictional_data_only=True, session_format='Telehealth', preferred_counselor_id=None,
                            preferred_date=(date.today() + timedelta(days=7)).isoformat(), preferred_time='Morning',
                            time_zone='America/New_York', request_key=str(uuid4()))

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def save(self, payload=None):
        return self.client.post('/api/preference-requests', json=payload or self.payload)

    def test_contact_and_preferences_are_saved_under_original_id(self):
        response = self.save()
        self.assertEqual(response.status_code, 201, response.text)
        inquiry = response.json()
        path = '/api/inquiries/' + inquiry['inquiry_id']
        self.assertEqual(self.client.get(path).json(), inquiry)
        record = self.client.get(path + '/management').json()
        self.assertEqual(record['preferences']['email'], 'alex@example.com')
        self.assertEqual(record['preferences']['phone'], '2025550100')
        self.assertIsNone(record['preferences']['preferred_counselor_id'])
        self.assertEqual(record['preferences']['preferred_date'], self.payload['preferred_date'])
        self.assertEqual(len(record['history']), 1)
        self.assertNotIn('appointment', record)
        self.assertNotIn('email', inquiry)  # Legacy inquiry response stays unchanged.

    def test_rejects_real_contacts_and_invalid_preferences_without_saving(self):
        for change in [dict(fictional_client_name='Alex River'), dict(email='alex@gmail.com'),
                       dict(phone='202-867-5309'), dict(preferred_date='2000-01-01'),
                       dict(preferred_time='09:00'), dict(session_format='Other'),
                       dict(time_zone='UTC'), dict(preferred_counselor_id='unknown'),
                       dict(clinical_notes='not accepted'), dict(fictional_data_only=False)]:
            response = self.save(dict(self.payload, **change))
            self.assertEqual(response.status_code, 422, response.text)
            self.assertIn('detail', response.json())
        self.assertEqual(self.client.get('/api/inquiries').json(), [])

    def test_retries_return_same_inquiry_and_changed_retries_conflict(self):
        first = self.save().json()
        retry = self.save()
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(retry.json(), first)
        self.assertEqual(self.save(dict(self.payload, category='family')).status_code, 409)
        self.assertEqual(len(self.client.get('/api/inquiries').json()), 1)

    def test_same_names_are_not_merged(self):
        first = self.save().json()
        second = self.save(dict(self.payload, request_key=str(uuid4()))).json()
        self.assertNotEqual(first['inquiry_id'], second['inquiry_id'])
        self.assertEqual(len(self.client.get('/api/inquiries').json()), 2)

    def test_conversion_portal_history_and_restart_preserve_request_details(self):
        inquiry = self.save(dict(self.payload, preferred_counselor_id='rachel-kim')).json()
        path = '/api/inquiries/' + inquiry['inquiry_id']
        self.client.post(path + '/portal-status', json={'portal_status': 'Sent'})
        before = self.client.get(path + '/management').json()
        record = self.client.post(path + '/convert', json={'confirmed': True}).json()
        self.assertEqual(record['preferences'], before['preferences'])
        self.assertIsNone(record['assigned_counselor_id'])  # A preferred counselor is never an assignment.
        self.assertEqual(record['history'][:-1], before['history'])
        self.assertEqual(record['created_at'], inquiry['created_at'])
        self.assertEqual(self.client.post(path + '/convert', json={'confirmed': True}).status_code, 409)
        self.client.__exit__(None, None, None)
        self.client = TestClient(create_app(self.database, seed=False))
        self.client.__enter__()
        self.assertEqual(self.client.get('/api/clients').json(), [record])
        self.assertEqual(self.client.get('/api/prospective-clients').json(), [])
        self.assertEqual(self.save().status_code, 409)  # Existing key, changed preference.
