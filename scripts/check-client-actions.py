"""End-to-end client record actions check, using a disposable database.
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
    env = dict(os.environ, ELCCC_DB_PATH=str(Path(temp) / 'actions.sqlite3'))
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
            browser = p.chromium.launch(executable_path=executable, args=['--no-sandbox'])
            page = browser.new_page()
            legacy_profile_components(page)
            staff_login(page)
            page.set_default_timeout(10000)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:5500')
            original = page.request.post('http://127.0.0.1:8000/api/preference-requests', data=dict(
                fictional_client_name='Test Alex River', category='individual', preferred_contact_method='email',
                fictional_data_only=True, email='alex@example.com', phone='202-555-0100',
                session_format='Telehealth', preferred_date='2099-01-01', preferred_time='Morning',
                preferred_counselor_id=None, request_key='d7732f85-d8e2-46e8-9e5e-c6dc47a69e87')).json()
            inquiry_id = original['inquiry_id']
            api = 'http://127.0.0.1:8000/api/inquiries/' + inquiry_id
            page.evaluate("selectDemoRole('Admin');state.activeAdminPanel='prospective';render()")
            page.get_by_label('Search clients', exact=True).fill(inquiry_id)
            row = page.locator('[data-managed-record="' + inquiry_id + '"]')
            profile = page.locator('[data-managed-profile]')

            def close_profile():
                profile.get_by_role('button', name='Close profile', exact=True).click()
                assert profile.count() == 0

            def assert_profile(name):
                profile.get_by_role('heading', name=name + ' profile', exact=True).wait_for()
                assert inquiry_id in profile.inner_text()

            def open_dialog(action):
                row.locator('[data-client-action=' + action + ']').click()
                page.locator('.client-record-dialog h2').wait_for()

            def read_record():
                return page.request.get(api + '/management').json()

            # Single-click name, double-click name or row, keyboard, View and Open profile.
            row.locator('[data-client-name]').click()
            assert_profile('Test Alex River'); close_profile()
            row.locator('[data-client-name]').dblclick()
            assert_profile('Test Alex River'); close_profile()
            row.locator('[role=cell]').nth(2).dblclick()
            assert_profile('Test Alex River'); close_profile()
            row.focus(); page.keyboard.press('Enter')
            assert_profile('Test Alex River'); close_profile()
            row.locator('[data-client-name]').focus(); page.keyboard.press('Enter')
            assert_profile('Test Alex River'); close_profile()
            row.get_by_role('button', name='View', exact=True).click()
            assert_profile('Test Alex River'); close_profile()
            row.get_by_role('button', name='Open profile', exact=True).click()
            assert_profile('Test Alex River')
            initial = read_record()
            # Cancel and Escape leave saved data, filter, profile and activity untouched.
            for cancel in ('button', 'escape'):
                open_dialog('edit')
                page.get_by_label('Full name', exact=True).fill('Test Unsaved Name')
                if cancel == 'button':
                    page.locator('.client-record-dialog').get_by_role('button', name='Cancel', exact=True).click()
                else:
                    page.keyboard.press('Escape')
                assert page.locator('.client-record-dialog').count() == 0
                assert_profile('Test Alex River')
                assert read_record() == initial
                assert page.get_by_label('Search clients', exact=True).input_value() == inquiry_id
            open_dialog('edit')
            page.get_by_label('Email address', exact=True).fill('alex@gmail.com')
            page.get_by_role('button', name='Save Changes', exact=True).click()
            page.locator('.client-record-dialog [role=alert]').get_by_text('Use an example.com', exact=False).wait_for()
            assert read_record() == initial
            page.get_by_label('Email address', exact=True).fill('updated@example.org')
            page.get_by_label('Full name', exact=True).fill('Test Alex Updated')
            page.get_by_label('Counseling category').select_option('family')
            page.get_by_label('Inquiry review status').select_option('reviewing')
            page.get_by_role('button', name='Save Changes', exact=True).click()
            assert_profile('Test Alex Updated')
            assert read_record()['preferences']['email'] == 'updated@example.org'
            assert read_record()['original_inquiry'] == original
            # Network failures retain drafts and do not claim success.
            open_dialog('edit')
            page.get_by_label('Full name', exact=True).fill('Test Failed Save')
            page.route('**/api/inquiries/*/edit', lambda route: route.abort())
            page.get_by_role('button', name='Save Changes', exact=True).click()
            page.locator('.client-record-dialog').get_by_text('Changes were not confirmed saved.', exact=False).wait_for()
            assert page.get_by_label('Full name', exact=True).input_value() == 'Test Failed Save'
            assert read_record()['fictional_client_name'] == 'Test Alex Updated'
            page.unroute('**/api/inquiries/*/edit')
            page.locator('.client-record-dialog').get_by_role('button', name='Cancel', exact=True).click()
            # Stale forms refuse an overwrite after another action changes the record.
            open_dialog('edit')
            page.request.post(api + '/portal-status', data={'portal_status': 'Sent'})
            page.get_by_role('button', name='Save Changes', exact=True).click()
            page.locator('.client-record-dialog').get_by_text('This record changed in another view.', exact=False).wait_for()
            page.locator('.client-record-dialog').get_by_role('button', name='Cancel', exact=True).click()
            # Delete click itself, double-click, and cancelled confirmation cannot archive.
            open_dialog('archive')
            page.get_by_role('button', name='Confirm Archive', exact=True).click()
            assert read_record()['archived_at'] is None
            page.locator('.client-record-dialog').get_by_role('button', name='Cancel', exact=True).click()
            assert row.count() == 1
            open_dialog('archive')
            page.get_by_label('I confirm I want to archive this client record.').check()
            page.get_by_role('button', name='Confirm Archive', exact=True).click()
            page.get_by_text('Client archived. History retained;', exact=False).wait_for()
            assert row.count() == 0
            page.get_by_label('Record visibility', exact=True).select_option('archived')
            row.wait_for()
            assert row.get_by_role('button', name='Edit', exact=True).count() == 0
            open_dialog('restore')
            page.get_by_label('I confirm I want to restore this client record.').check()
            page.get_by_role('button', name='Confirm Restore', exact=True).click()
            page.get_by_text('Client restored to the active directory.', exact=True).wait_for()
            page.get_by_label('Record visibility', exact=True).select_option('active')
            row.wait_for()
            profile.get_by_role('button', name='Convert to Client', exact=True).click()
            page.get_by_role('button', name='Confirm Conversion', exact=True).click()
            page.get_by_role('heading', name='Established Clients', exact=True).wait_for()
            assert_profile('Test Alex Updated')
            converted_at = read_record()['converted_at']
            # Established clients have exactly the same entry points and editable profile.
            close_profile()
            row.locator('[role=cell]').nth(2).dblclick(); assert_profile('Test Alex Updated')
            open_dialog('edit')
            for width in [320, 375, 768, 1440]:
                page.set_viewport_size(dict(width=width, height=900))
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), width
                assert page.locator('.client-record-dialog').evaluate('el => el.scrollWidth <= el.clientWidth + 1'), width
            page.get_by_label('Full name', exact=True).fill('Test Established Client')
            page.get_by_role('button', name='Save Changes', exact=True).click()
            assert_profile('Test Established Client')
            if os.environ.get('QA_SCREENSHOTS'):
                page.set_viewport_size(dict(width=375, height=900))
                page.screenshot(path=str(ROOT / 'work' / 'client-actions-mobile.png'), full_page=True)
            open_dialog('archive')
            page.get_by_label('I confirm I want to archive this client record.').check()
            page.get_by_role('button', name='Confirm Archive', exact=True).click()
            page.get_by_text('Client archived. History retained;', exact=False).wait_for()
            archived = read_record()
            assert archived['converted_at'] == converted_at and archived['portal_status'] == 'Sent'
            # Actual backend restart + full page reload preserve archive, edit and history.
            backend.terminate(); backend.wait(timeout=10)
            backend = start(backend_args, ROOT / 'backend', env, 'http://127.0.0.1:8000/health')
            staff_login(page)
            page.reload()
            page.evaluate("selectDemoRole('Admin');state.activeAdminPanel='established';render()")
            page.get_by_label('Search clients', exact=True).fill(inquiry_id)
            page.get_by_label('Record visibility', exact=True).select_option('archived')
            row.get_by_role('button', name='Open profile', exact=True).click()
            assert_profile('Test Established Client')
            assert read_record() == archived
            assert profile.get_by_role('button', name='Save invitation tracking').is_disabled()
            assert page.request.get(api).json() == original
            open_dialog('restore')
            page.get_by_label('I confirm I want to restore this client record.').check()
            page.get_by_role('button', name='Confirm Restore', exact=True).click()
            page.get_by_text('Client restored to the active directory.', exact=True).wait_for()
            page.get_by_label('Record visibility', exact=True).select_option('active')
            row.wait_for()
            assert read_record()['converted_at'] == converted_at
            assert read_record()['portal_status'] == 'Sent'
            assert not errors, errors
            browser.close()
            print('PASS: both client lists, clickable names, double-click rows/names, Enter, View/Open profile, Cancel/Escape, saved edits, validation/network/stale-edit failures, confirmed archive and restore, responsive forms, original inquiry/history, conversion/invitation, refresh/restart persistence.')
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
