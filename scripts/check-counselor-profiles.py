"""End-to-end dedicated profile and counselor assignment check, using a disposable database.
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
from browser_support import configure_staff, staff_login, ADMIN_KEY, RACHEL_KEY, MELISSA_KEY

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
    env = dict(os.environ, ELCCC_DB_PATH=str(Path(temp) / 'profiles.sqlite3'))
    configure_staff(env, temp)
    backend_args = [os.environ.get('BACKEND_PYTHON', sys.executable), '-m', 'uvicorn', 'app.main:app',
                    '--host', '127.0.0.1', '--port', '8000']
    try:
        backend = start(backend_args, ROOT / 'backend', env, 'http://127.0.0.1:8000/health')
        start([sys.executable, 'scripts/serve-local.py', '--port', '5500'], ROOT, env,
              'http://127.0.0.1:5500')
        with sync_playwright() as p:
            executable = os.environ.get('CHROMIUM_PATH')
            if not executable and Path('/usr/bin/chromium').exists():
                executable = '/usr/bin/chromium'
            browser = p.chromium.launch(executable_path=executable, args=['--no-sandbox'])
            context = browser.new_context()
            context.set_default_timeout(12000)
            errors = []
            context.on('page', lambda page: page.on('pageerror', lambda error: errors.append(str(error))))
            directory = context.new_page()
            directory.goto('http://127.0.0.1:5500/?workspace=clients')
            directory.get_by_label('Local staff access key').fill(ADMIN_KEY)
            directory.get_by_role('button', name='Open staff workspace', exact=True).click()
            directory.get_by_label('Search clients', exact=True).wait_for()
            # Anonymous public request creates only its own synthetic inquiry, not a booking/assignment.
            anonymous = browser.new_context()
            public = anonymous.new_page()
            public.goto('http://127.0.0.1:5500')
            saved = public.request.post('http://127.0.0.1:8000/api/preference-requests', data=dict(
                fictional_client_name='Test Alex River', category='individual', preferred_contact_method='email',
                fictional_data_only=True, email='alex@example.com', phone='202-555-0100',
                session_format='Telehealth', preferred_date='2099-01-01', preferred_time='Morning',
                preferred_counselor_id='rachel-kim', request_key='d7732f85-d8e2-46e8-9e5e-c6dc47a69e87')).json()
            inquiry_id = saved['inquiry_id']
            api = 'http://127.0.0.1:8000/api/inquiries/' + inquiry_id
            assert public.request.get(api + '/management').status == 401
            for path in ['/backend/data/inquiries.sqlite3', '/backend/app/main.py', '/.git/config', '/work/', '/scripts/browser_support.py']:
                assert public.request.get('http://127.0.0.1:5500' + path).status == 404
            public.goto('http://127.0.0.1:5500/?client=' + inquiry_id)
            public.get_by_label('Local staff access key').wait_for()
            assert 'Test Alex River' not in public.locator('main').inner_text()
            directory.get_by_role('button', name='Refresh client lists').click()
            directory.get_by_label('Search clients', exact=True).fill(inquiry_id)
            row = directory.locator('[data-managed-record="' + inquiry_id + '"]')
            row.wait_for()
            original_url = directory.url
            # Intake is a first-class work area, immediately after Overview.
            navigation = directory.get_by_role('navigation', name='Admin work areas')
            assert navigation.locator('button').all_text_contents()[:2] == ['Overview', 'Intake']
            navigation.get_by_role('button', name='Overview', exact=True).click()
            directory.get_by_role('button', name='Review Intake', exact=True).click()
            directory.get_by_role('heading', name='Intake', exact=True).wait_for()
            directory.get_by_role('button', name='Review Intake for Test Alex River', exact=True).wait_for()
            directory.get_by_role('button', name='Clients', exact=True).click()
            row.wait_for()
            toolbar = directory.get_by_role('group', name='Selected client actions')
            assert toolbar.get_by_role('button', name='View', exact=True).is_disabled()
            # Switching records and lists never leaves a hidden record active.
            other = directory.request.post('http://127.0.0.1:8000/api/inquiries', data={
                'fictional_client_name': 'Test Bailey River', 'category': 'individual',
                'preferred_contact_method': 'email', 'fictional_data_only': True})
            assert other.status == 201
            other_id = other.json()['inquiry_id']
            directory.get_by_role('button', name='Refresh client lists', exact=True).click()
            directory.get_by_label('Search clients', exact=True).fill('Test ')
            other_row = directory.locator('[data-managed-record="' + other_id + '"]')
            row.locator('h3').click()
            other_row.locator('h3').click()
            assert other_row.get_attribute('data-selected') == 'true'
            assert row.get_attribute('data-selected') == 'false'
            assert 'Test Bailey River' in toolbar.inner_text()
            directory.get_by_role('button', name='Established Clients', exact=True).click()
            directory.get_by_role('button', name='Prospective Clients', exact=True).click()
            assert toolbar.get_by_role('button', name='View', exact=True).is_disabled()
            directory.get_by_label('Search clients', exact=True).fill(inquiry_id)
            assert row.locator('button').count() == 0
            row.locator('h3').click()
            assert row.get_attribute('data-selected') == 'true'
            row.locator('h3').click()
            assert row.get_attribute('data-selected') == 'false'
            assert all(not button.is_enabled() for button in toolbar.get_by_role('button').all())
            row.locator('[data-select-client]').check()
            directory.get_by_label('Search clients', exact=True).fill('Test Alex')
            assert toolbar.get_by_role('button', name='View', exact=True).is_disabled()
            directory.get_by_label('Search clients', exact=True).fill(inquiry_id)
            row.focus(); directory.keyboard.press('Space')
            assert 'Test Alex River' in toolbar.inner_text()
            assert row.get_attribute('data-selected') == 'true'
            with context.expect_page() as selected_popup:
                toolbar.get_by_role('button', name='View', exact=True).focus()
                directory.keyboard.press('Enter')
            selected_popup.value.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            selected_popup.value.close()
            toolbar.get_by_role('button', name='Edit', exact=True).click()
            directory.get_by_role('heading', name='Edit client details', exact=True).wait_for()
            directory.keyboard.press('Escape')
            toolbar.get_by_role('button', name='Archive', exact=True).click()
            directory.get_by_role('heading', name='Archive client record', exact=True).wait_for()
            directory.keyboard.press('Escape')
            assert directory.request.get(api + '/management').json()['archived_at'] is None
            for width in [320, 375, 768, 1280]:
                directory.set_viewport_size(dict(width=width, height=900))
                assert directory.locator('header').get_by_role('button', name='Sign Out', exact=True).is_visible()
                assert 'Administrator' in directory.locator('.staff-navigation').inner_text()
                assert not directory.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), width
                if os.environ.get('QA_SCREENSHOTS') and width in [375, 1280]:
                    directory.screenshot(path=str(ROOT / 'work' / ('client-directory-' + str(width) + '.png')), full_page=True)
            directory.set_viewport_size(dict(width=1280, height=900))

            def open_profile(action):
                page_count = len(context.pages)
                with context.expect_page() as popup:
                    row.locator('[data-select-client]').uncheck()
                    if action == 'name':
                        row.locator('h3').click()
                    elif action == 'keyboard':
                        row.focus(); directory.keyboard.press('Enter')
                    else:
                        row.locator('[data-select-client]').check()
                    toolbar.get_by_role('button', name='View', exact=True).click()
                page = popup.value
                page.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
                assert page.url == 'http://127.0.0.1:5500/?client=' + inquiry_id
                assert len(context.pages) == page_count + 1
                assert directory.url == original_url
                assert directory.get_by_label('Search clients', exact=True).input_value() == inquiry_id
                assert directory.locator('[data-managed-profile]').count() == 0
                return page

            for action in ['name', 'keyboard', 'View']:
                page = open_profile(action)
                page.close(); directory.bring_to_front(); row.wait_for()
            profile = open_profile('View')
            for title in ['Overview', 'Contact Information', 'Counseling Preferences', 'Intake', 'Appointments', 'Activity History']:
                profile.get_by_role('navigation', name='Client profile sections').get_by_role('link', name=title, exact=True).wait_for()
            assert profile.locator('[data-assignment-form]').count() == 0
            assert 'Convert this inquiry' in profile.locator('[data-counselor-assignment]').inner_text()
            sections = profile.get_by_role('navigation', name='Client profile sections')
            assert sections.get_by_role('link').all_text_contents()[:2] == ['Overview', 'Intake']
            assert profile.locator('#saved-onboarding-progress').get_attribute('value') == '1'
            sections.get_by_role('link', name='Intake', exact=True).click()
            profile.wait_for_function("document.querySelector('#profile-intake').getBoundingClientRect().top < 60")
            assert profile.locator('#profile-intake [data-onboarding-checklist]').is_visible()
            assert profile.locator('#profile-intake').evaluate('el => el.previousElementSibling.id') == 'profile-overview'
            profile.get_by_role('button', name='Convert to Client', exact=True).click()
            profile.get_by_role('group', name='Confirm client conversion').get_by_text('This moves the record', exact=False).wait_for()
            profile.get_by_role('button', name='Cancel Conversion', exact=True).click()
            assert profile.request.get(api + '/management').json()['converted_at'] is None
            profile.get_by_role('button', name='Convert to Client', exact=True).click()
            profile.get_by_role('button', name='Confirm Conversion', exact=True).click()
            profile.locator('[data-assignment-form]').wait_for()
            assert profile.get_by_label('Assign counselor', exact=True).input_value() == ''
            assert 'Requested preference: Rachel Kim' in profile.locator('[data-counselor-assignment]').inner_text()
            # Confirmation and Cancel work independently of preferred counselor.
            assert profile.get_by_role('button', name='Convert to Client', exact=True).count() == 0
            assert profile.locator('#saved-onboarding-progress').get_attribute('value') == '2'
            converted = profile.request.get(api + '/management').json()
            assert len([e for e in converted['history'] if e['action'] == 'Converted to client']) == 1
            assert profile.request.post(api + '/convert', data={'confirmed': True}).status == 409
            assert profile.request.get(api + '/management').json() == converted
            profile.get_by_label('Assign counselor', exact=True).select_option('rachel-kim')
            profile.get_by_role('button', name='Review Assignment Change', exact=True).click()
            directory.bring_to_front(); profile.bring_to_front()
            profile.get_by_role('group', name='Confirm counselor assignment').wait_for()
            profile.get_by_role('button', name='Cancel Assignment Change', exact=True).click()
            assert directory.request.get(api + '/management').json()['assigned_counselor_id'] is None
            assert profile.get_by_label('Assign counselor').locator('option[value=denice-colson]').get_attribute('disabled') is not None, profile.evaluate('state.staffCounselors')
            profile.get_by_label('Assign counselor', exact=True).select_option('rachel-kim')
            profile.get_by_role('button', name='Review Assignment Change', exact=True).click()
            profile.get_by_role('button', name='Confirm Assignment Change', exact=True).click()
            profile.get_by_text('Counselor assignment saved.', exact=True).wait_for()
            assert profile.locator('#saved-onboarding-progress').get_attribute('value') == '3'
            profile.get_by_label('Portal invitation status', exact=True).select_option('Sent')
            profile.get_by_role('button', name='Save invitation tracking', exact=True).click()
            profile.get_by_text('Invitation tracking saved locally.', exact=False).wait_for()
            assert profile.locator('#saved-onboarding-progress').get_attribute('value') == '4'
            profile.reload()
            profile.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            assert profile.locator('#saved-onboarding-progress').get_attribute('value') == '4'
            if os.environ.get('QA_SCREENSHOTS'):
                profile.set_viewport_size(dict(width=375, height=900))
                profile.get_by_role('link', name='Intake', exact=True).click()
                profile.wait_for_function("document.querySelector('#profile-intake').getBoundingClientRect().top < 60")
                profile.screenshot(path=str(ROOT / 'work' / 'intake-checklist-mobile.png'))
                profile.set_viewport_size(dict(width=1280, height=900))
            profile.get_by_label('Portal invitation status', exact=True).select_option('Not Sent')
            profile.get_by_role('button', name='Save invitation tracking', exact=True).click()
            profile.get_by_text('Invitation tracking saved locally.', exact=False).wait_for()
            assert profile.locator('#saved-onboarding-progress').get_attribute('value') == '3'

            assert 'Rachel Kim' in profile.locator('.profile-heading').inner_text()
            profile.reload()
            profile.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            assert profile.get_by_label('Assign counselor', exact=True).input_value() == 'rachel-kim'
            assert inquiry_id in profile.url
            profile.get_by_role('button', name='Edit', exact=True).click()
            profile.get_by_label('Full name', exact=True).fill('Test Unsaved Name')
            directory.bring_to_front(); profile.bring_to_front()
            assert profile.get_by_label('Full name', exact=True).input_value() == 'Test Unsaved Name'
            profile.get_by_role('button', name='Cancel', exact=True).click()
            profile.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            profile.get_by_role('button', name='Edit', exact=True).click()
            profile.get_by_label('Email address', exact=True).fill('updated@example.org')
            profile.get_by_role('button', name='Save Changes', exact=True).click()
            profile.locator('#profile-contact').get_by_text('updated@example.org', exact=False).wait_for()
            assert profile.get_by_label('Assign counselor', exact=True).input_value() == 'rachel-kim'
            # Actual counselor session sees its caseload and only its assigned profile.
            counselor_context = browser.new_context()
            counselor_context.set_default_timeout(12000)
            counselor_context.on('page', lambda page: page.on('pageerror', lambda error: errors.append(str(error))))
            counselor = counselor_context.new_page()
            counselor.goto('http://127.0.0.1:5500/?workspace=counselor')
            counselor.get_by_label('Local staff access key').fill(RACHEL_KEY)
            counselor.get_by_role('button', name='Open staff workspace', exact=True).click()
            counselor.get_by_role('heading', name='Counselor Dashboard', exact=True).wait_for()
            counselor.get_by_role('button', name='Test Alex River', exact=True).wait_for()
            assert counselor.locator('.metric-card').first.locator('strong').inner_text() == '1'
            with counselor_context.expect_page() as popup:
                counselor.get_by_role('button', name='Open profile', exact=True).click()
            read_only = popup.value
            read_only.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            assert read_only.get_by_role('button', name='Edit', exact=True).count() == 0
            assert read_only.locator('[data-assignment-form]').count() == 0
            assert counselor.request.post(api + '/assignment', data=dict(confirmed=True,
                expected_revision=0, counselor_id=None)).status == 403
            other = counselor_context.new_page()
            other.goto('http://127.0.0.1:5500/?client=00000000-0000-0000-0000-000000000000')
            other.get_by_text('Could not open this client profile.', exact=False).wait_for()
            assert other.get_by_role('heading', name='Test Alex River', exact=True).count() == 0
            other.close()
            # Change then remove assignment, each confirmed, with immediate ownership checks.
            profile.bring_to_front()
            profile.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            profile.get_by_label('Assign counselor', exact=True).select_option('melissa-smith')
            profile.get_by_role('button', name='Review Assignment Change', exact=True).click()
            profile.get_by_role('button', name='Confirm Assignment Change', exact=True).click()
            profile.get_by_text('Counselor assignment saved.', exact=True).wait_for()
            assert counselor.request.get(api + '/management').status == 404
            profile.get_by_label('Assign counselor', exact=True).select_option('')
            profile.get_by_role('button', name='Review Assignment Change', exact=True).click()
            profile.get_by_role('button', name='Confirm Assignment Change', exact=True).click()
            profile.get_by_text('Counselor assignment saved.', exact=True).wait_for()
            assert directory.request.get(api + '/management').json()['assigned_counselor_id'] is None
            profile.get_by_label('Assign counselor', exact=True).select_option('rachel-kim')
            profile.get_by_role('button', name='Review Assignment Change', exact=True).click()
            profile.get_by_role('button', name='Confirm Assignment Change', exact=True).click()
            profile.get_by_text('Counselor assignment saved.', exact=True).wait_for()
            for width in [320, 375, 768, 1440]:
                profile.set_viewport_size(dict(width=width, height=900))
                assert not profile.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), width
                profile.get_by_role('navigation', name='Client profile sections').get_by_role('link', name='Activity History', exact=True).click()
                assert profile.locator('#profile-activity').is_visible()
            if os.environ.get('QA_SCREENSHOTS'):
                profile.screenshot(path=str(ROOT / 'work' / 'dedicated-client-profile.png'), full_page=True)
            profile.get_by_role('button', name='Archive', exact=True).click()
            profile.get_by_label('I confirm I want to archive this client record.').check()
            profile.get_by_role('button', name='Confirm Archive', exact=True).click()
            profile.locator('.archive-banner').wait_for()
            assert profile.get_by_role('button', name='Edit', exact=True).count() == 0
            assert profile.locator('[data-assignment-form]').count() == 0
            assert profile.get_by_role('button', name='Save invitation tracking').is_disabled()
            assert counselor.request.get(api + '/management').status == 404
            profile.get_by_role('button', name='Restore', exact=True).click()
            profile.get_by_label('I confirm I want to restore this client record.').check()
            profile.get_by_role('button', name='Confirm Restore', exact=True).click()
            profile.get_by_label('Assign counselor', exact=True).wait_for()
            before = directory.request.get(api + '/management').json()
            # Restart invalidates sessions, not saved assignment or stable URLs.
            backend.terminate(); backend.wait(timeout=10)
            backend = start(backend_args, ROOT / 'backend', env, 'http://127.0.0.1:8000/health')
            profile.reload()
            profile.get_by_label('Local staff access key').wait_for()
            profile.get_by_label('Local staff access key').fill(ADMIN_KEY)
            profile.get_by_role('button', name='Open staff workspace', exact=True).click()
            profile.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            assert profile.get_by_label('Assign counselor', exact=True).input_value() == 'rachel-kim'
            assert profile.request.get(api + '/management').json() == before
            assert profile.url.split('#')[0].endswith('?client=' + inquiry_id)
            profile.get_by_role('link', name='Back to Clients', exact=True).click()
            profile.get_by_role('heading', name='Established Clients', exact=True).wait_for()
            assert directory.url == original_url
            profile.get_by_label('Search clients', exact=True).fill(inquiry_id)
            profile.locator('[data-select-client]').check()
            established_toolbar = profile.get_by_role('group', name='Selected client actions')
            for action in ['View', 'Edit', 'Archive']:
                assert established_toolbar.get_by_role('button', name=action, exact=True).is_enabled()
            # Filtering away the selected row clears the toolbar rather than targeting a hidden record.
            profile.get_by_label('Search clients', exact=True).fill('no matching synthetic client')
            assert established_toolbar.get_by_role('button', name='View', exact=True).is_disabled()
            profile.get_by_label('Search clients', exact=True).fill(inquiry_id)
            with context.expect_page() as popup:
                profile.locator('[data-select-client]').check()
                established_toolbar.get_by_role('button', name='View', exact=True).click()
            established_tab = popup.value
            established_tab.get_by_role('heading', name='Test Alex River', exact=True).wait_for()
            assert '?workspace=clients' in profile.url
            # Shared-cookie sign-out clears another profile on focus instead of revealing cached details.
            profile.bring_to_front()
            # A failed logout remains visible and keeps the active session.
            profile.route('**/api/staff/logout', lambda route: route.fulfill(status=503, content_type='application/json', body='{"detail":"Synthetic logout outage"}'))
            profile.get_by_role('button', name='Sign Out', exact=True).click()
            profile.get_by_role('alert').filter(has_text='Could not sign out').wait_for()
            assert 'Administrator' in profile.locator('.staff-navigation').inner_text()
            profile.unroute('**/api/staff/logout')
            profile.get_by_role('button', name='Sign Out', exact=True).click()
            profile.get_by_role('button', name="I'm an Administrator", exact=True).wait_for()
            assert '?client=' not in profile.url
            assert profile.request.get(api + '/management').status == 401
            established_tab.bring_to_front()
            established_tab.get_by_label('Local staff access key').wait_for()
            assert 'Test Alex River' not in established_tab.locator('main').inner_text()
            assert not errors, errors
            browser.close()
            print('PASS: protected stable profile URLs, toolbar-only new-tab profiles, row click and keyboard selection/deselection, original directory preserved, six sections, edit/cancel/save/archive/restore, preferred versus assigned counselor, confirmed assignment/change/removal, scoped counselor caseload and read-only profiles, blocked anonymous access/files, Intake navigation, selected toolbars in both lists, keyboard selection and new-tab View, canceled Edit/Archive, filter isolation, header at four widths, failed/successful logout, refresh and actual restart with reauthentication.')
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate(); process.wait(timeout=10)
