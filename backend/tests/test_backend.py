from datetime import datetime
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import UUID, uuid4
from staff_fixtures import TestClient, create_app


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'inquiries.sqlite3'
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()
        self.payload = dict(fictional_client_name='Demo Robin Orchard', category='couples',
                            preferred_contact_method='email', fictional_data_only=True)

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def test_health_and_browser_demo(self):
        self.assertEqual(self.client.get('/health').json()['database'], 'ok')
        response = self.client.get('/demo')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers['content-type'])
        self.assertIn('DEVELOPMENT DEMO', response.text)
        self.assertIn('not HIPAA-ready', response.text)
        self.assertEqual(self.client.get('/').url.path, '/demo')

    def test_create_list_retrieve_and_metadata(self):
        response = self.client.post('/api/inquiries', json=self.payload)
        self.assertEqual(response.status_code, 201)
        inquiry = response.json()
        UUID(inquiry['inquiry_id'])
        self.assertIsNotNone(datetime.fromisoformat(inquiry['created_at'].replace('Z', '+00:00')).tzinfo)
        self.assertEqual(inquiry['status'], 'new')
        self.assertEqual(inquiry['fictional_client_name'], self.payload['fictional_client_name'])
        self.assertIn(inquiry, self.client.get('/api/inquiries').json())
        self.assertEqual(self.client.get('/api/inquiries/' + inquiry['inquiry_id']).json(), inquiry)
        second = self.client.post('/api/inquiries', json=self.payload).json()
        self.assertNotEqual(inquiry['inquiry_id'], second['inquiry_id'])

    def test_persistence_and_seed_not_duplicated_after_restart(self):
        samples = self.client.get('/api/inquiries').json()
        self.assertEqual(len(samples), 3)
        inquiry = self.client.post('/api/inquiries', json=self.payload).json()
        self.client.__exit__(None, None, None)
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()
        saved = self.client.get('/api/inquiries').json()
        self.assertEqual(len(saved), 4)
        for record in samples + [inquiry]:
            self.assertIn(record, saved)

    def test_validation_does_not_save_invalid_data(self):
        invalid = [{'fictional_client_name': ''}, {'fictional_client_name': '   '},
                   {'fictional_client_name': 'a'}, {'fictional_client_name': 'a' * 81},
                   {'category': 'diagnosis'}, {'preferred_contact_method': 'fax'},
                   {'fictional_data_only': False}, {'email': 'not-collected'},
                   {'status': 'closed'}, {'created_at': '2026-01-01'}]
        for patch in invalid:
            with self.subTest(patch=patch):
                response = self.client.post('/api/inquiries', json=self.payload | patch)
                self.assertEqual(response.status_code, 422)
                self.assertIn('Invalid inquiry', response.json()['detail'])
                self.assertTrue(response.json()['errors'])
        missing = self.payload.copy()
        del missing['fictional_data_only']
        self.assertEqual(self.client.post('/api/inquiries', json=missing).status_code, 422)
        self.assertEqual(self.client.post('/api/inquiries', content='{broken',
                         headers={'content-type': 'application/json'}).status_code, 422)
        self.assertEqual(len(self.client.get('/api/inquiries').json()), 3)

    def test_not_found_and_invalid_id(self):
        response = self.client.get('/api/inquiries/' + str(uuid4()))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Inquiry not found', response.json()['detail'])
        self.assertEqual(self.client.get('/api/inquiries/not-a-uuid').status_code, 422)

    def test_whitespace_and_sql_are_handled_as_data(self):
        name = "  Demo O'Brien'); DROP TABLE inquiries; --  "
        response = self.client.post('/api/inquiries', json=self.payload | {'fictional_client_name': name})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['fictional_client_name'], name.strip())
        self.assertEqual(len(self.client.get('/api/inquiries').json()), 4)

    def test_local_cors_and_disallowed_origins(self):
        for origin in ['http://127.0.0.1:5500', 'http://localhost:5500']:
            preflight = self.client.options('/api/inquiries', headers={
                'Origin': origin, 'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'content-type'})
            self.assertEqual(preflight.status_code, 200)
            self.assertEqual(preflight.headers['access-control-allow-origin'], origin)
            self.assertEqual(preflight.headers['access-control-allow-credentials'], 'true')
            saved = self.client.post('/api/inquiries', json=self.payload, headers={'Origin': origin})
            self.assertEqual(saved.status_code, 201)
            self.assertEqual(saved.headers['access-control-allow-origin'], origin)
            listed = self.client.get('/api/inquiries', headers={'Origin': origin})
            self.assertEqual(listed.headers['access-control-allow-origin'], origin)
        for origin in ['https://elcccdev.github.io', 'http://127.0.0.1:5501', 'https://example.com']:
            response = self.client.options('/api/inquiries', headers={
                'Origin': origin, 'Access-Control-Request-Method': 'POST'})
            self.assertEqual(response.status_code, 400)
            self.assertNotIn('access-control-allow-origin', response.headers)

    def test_database_errors_and_no_cors_access(self):
        with sqlite3.connect(self.database) as connection:
            connection.execute('DROP TABLE inquiries')
        response = self.client.get('/api/inquiries')
        self.assertEqual(response.status_code, 503)
        self.assertIn('Local database unavailable', response.json()['detail'])
        self.assertEqual(self.client.get('/health').status_code, 503)
        response = self.client.options('/api/inquiries', headers={
            'Origin': 'https://elcccdev.github.io', 'Access-Control-Request-Method': 'POST'})
        self.assertNotIn('access-control-allow-origin', response.headers)


if __name__ == '__main__':
    unittest.main()
