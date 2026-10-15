"""End-to-end public preference request check, using a disposable database.
Requires Playwright + Chromium, backend dev dependencies, free ports 5500/8000.
BACKEND_PYTHON may select the backend virtualenv interpreter.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright
from browser_support import configure_staff, staff_login, legacy_profile_components

ROOT = Path(__file__).resolve().parent.parent
processes = []


def start(args, cwd, env, url):
    process = subprocess.Popen(args, cwd=cwd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    processes.append(process)
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError(process.stderr.read().decode())
        try:
            urllib.request.urlopen(url, timeout=1).close()
            return process
        except OSError:
            time.sleep(.1)
    raise RuntimeError('Server failed to start: ' + url)


with tempfile.TemporaryDirectory() as temp:
    env = dict(os.environ, ELCCC_DB_PATH=str(Path(temp) / 'test.sqlite3'))
    backend_args = [os.environ.get('BACKEND_PYTHON', sys.executable), '-m', 'uvicorn', 'app.main:app',
                    '--host', '127.0.0.1', '--port', '8000']
    configure_staff(env, temp)
    try:
        backend = start(backend_args, ROOT / 'backend', env, 'http://127.0.0.1:8000/health')
        start([sys.executable, 'scripts/serve-local.py', '--port', '5500'], ROOT, env,
              'http://127.0.0.1:5500')
        with sync_playwright() as p:
            executable = os.environ.get('CHROMIUM_PATH')
            if not executable and Path('/usr/bin/chromium').exists():
                executable = '/usr/bin/chromium'
            browser = p.chromium.launch(executable_path=executable,
                                        args=['--no-sandbox'])
            page = browser.new_page()
            legacy_profile_components(page)
            staff_login(page)
            page.set_default_timeout(10000)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:5500')
            page.get_by_role('button', name='Explore Services or Request Care', exact=True).click()
            assert 'historical' not in page.locator('main').inner_text().lower()
            page.get_by_role('button', name='Request Counseling', exact=True).click()
            dialog = page.locator('.preference-modal')
            assert dialog.locator('select').count() == 0  # No CRM name dropdown.
            page.get_by_label('Full name', exact=True).fill('Test Alex River')
            page.get_by_label('Email address', exact=True).fill('alex@gmail.com')
            page.get_by_label('Phone number', exact=True).fill('202-555-0100')
            page.get_by_role('button', name='Continue', exact=True).click()
            dialog.get_by_text('Use an example.com, example.org, or example.net email in this preview.', exact=True).wait_for()
            page.get_by_label('Email address', exact=True).fill('alex@example.com')
            page.get_by_role('button', name='Continue', exact=True).click()
            page.get_by_label('Counseling type', exact=True).select_option('couples')
            page.get_by_label('Preferred session format', exact=True).select_option('In-person')
            page.get_by_role('button', name='Back', exact=True).click()
            assert page.get_by_label('Full name', exact=True).input_value() == 'Test Alex River'
            page.get_by_role('button', name='Continue', exact=True).click()
            assert page.get_by_label('Counseling type', exact=True).input_value() == 'couples'
            page.get_by_role('button', name='Continue', exact=True).click()
            page.get_by_label('Preferred counselor (optional)', exact=True).select_option('')
            page.get_by_role('button', name='Continue', exact=True).click()
            assert 'not bookable slots' in dialog.inner_text()
            page.get_by_label('Preferred date', exact=True).fill('2099-01-01')
            page.get_by_label('Preferred time period', exact=True).select_option('Afternoon')
            page.get_by_role('button', name='Continue', exact=True).click()
            assert 'alex@example.com' in dialog.inner_text()
            # Check narrow and large screens while preserving the same draft.
            for width in [320, 375, 768, 1440]:
                page.set_viewport_size(dict(width=width, height=900))
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), width
                assert dialog.evaluate('el => el.scrollWidth <= el.clientWidth + 1'), width
            page.get_by_label('I confirm all contact details are synthetic test data.', exact=True).check()
            # A failed request keeps the draft and cannot claim success.
            page.route('**/api/preference-requests', lambda route: route.abort())
            page.get_by_role('button', name='Submit preference request', exact=True).click()
            dialog.get_by_text('Request was not confirmed saved.', exact=False).wait_for()
            assert page.evaluate('state.bookingSubmitted') is False
            page.unroute('**/api/preference-requests')
            page.get_by_label('I confirm all contact details are synthetic test data.', exact=True).check()
            page.get_by_role('button', name='Submit preference request', exact=True).click()
            page.get_by_role('heading', name='Request received', exact=True).wait_for()
            inquiry_id = page.evaluate('state.lastSavedInquiryId')
            assert inquiry_id and 'No appointment is booked' in dialog.inner_text()
            assert page.evaluate('state.demoRequests[0].appointment') is None
            assert page.evaluate('state.demoRequests[0].counselorId') is None
            draft = page.evaluate('state.preferenceDraft')
            assert draft['name'] == 'Test Alex River'
            # Backend retry protection covers uncertain responses without matching on name.
            payload = dict(fictional_client_name=draft['name'], email=draft['email'], phone=draft['phone'],
                           category=draft['category'], preferred_contact_method='email', fictional_data_only=True,
                           session_format=draft['session_format'], preferred_counselor_id=None,
                           preferred_date=draft['preferred_date'], preferred_time=draft['preferred_time'],
                           time_zone='America/New_York', request_key=draft['request_key'])
            retry = page.request.post('http://127.0.0.1:8000/api/preference-requests', data=payload)
            assert retry.status == 200 and retry.json()['inquiry_id'] == inquiry_id
            page.get_by_role('button', name='Return to services', exact=True).click()
            page.evaluate("selectDemoRole('Admin');state.activeAdminPanel='prospective';render()")
            page.get_by_label('Search clients', exact=True).fill(inquiry_id)
            page.locator('[data-management-open]').click()
            profile = page.locator('[data-managed-profile]')
            profile.get_by_text('alex@example.com', exact=False).wait_for()
            assert '2099-01-01' in profile.inner_text()
            assert 'No preference' in profile.inner_text()
            page.get_by_label('Portal invitation status').select_option('Sent')
            page.get_by_role('button', name='Save invitation tracking', exact=True).click()
            page.get_by_text('Invitation tracking saved locally.', exact=False).wait_for()
            page.get_by_role('button', name='Convert to Client', exact=True).click()
            page.get_by_role('button', name='Confirm Conversion', exact=True).click()
            page.get_by_role('heading', name='Established Clients', exact=True).wait_for()
            profile.get_by_text('alex@example.com', exact=False).wait_for()
            # Both browser refresh and actual Uvicorn restart retain the shared record.
            backend.terminate()
            backend.wait(timeout=10)
            backend = start(backend_args, ROOT / 'backend', env, 'http://127.0.0.1:8000/health')
            staff_login(page)
            page.reload()
            page.evaluate("selectDemoRole('Admin');state.activeAdminPanel='established';render()")
            page.get_by_label('Search clients', exact=True).fill(inquiry_id)
            page.locator('[data-management-open]').click()
            profile.get_by_text('alex@example.com', exact=False).wait_for()
            assert 'Converted to client' in profile.inner_text()
            assert page.get_by_label('Portal invitation status').input_value() == 'Sent'
            assert page.locator('[data-request-preferences]').count() == 1
            assert not errors, errors
            browser.close()
            print('PASS: guided public contact/preferences/review, no CRM dropdown or fake slots, validation, back navigation, four widths, failed save/retry, unique ID, CRM details, invitation tracking, conversion, browser refresh and backend restart persistence.')
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
