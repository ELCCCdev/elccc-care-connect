"""Integration check. Needs backend dev dependencies and Playwright/Chromium.
Run from repository root: python scripts/check-backend-integration.py
Ports 5500, 5501, and 8000 must be free. Uses a temporary database only.
"""
import json
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright
from browser_support import open_selected_profile, configure_staff, staff_login, legacy_profile_components

ROOT = Path(__file__).resolve().parent.parent
processes = []
BACKEND_PYTHON = os.environ.get('BACKEND_PYTHON', sys.executable)


def start(args, cwd, env, url):
    process = subprocess.Popen(args, cwd=cwd, env=env, stdout=subprocess.DEVNULL,
                               stderr=subprocess.PIPE)
    processes.append(process)
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError(process.stderr.read().decode())
        try:
            with urllib.request.urlopen(url, timeout=1):
                return process
        except OSError:
            time.sleep(.1)
    raise RuntimeError('Server failed to start: ' + url)


def stop(process):
    if process.poll() is None:
        process.terminate()
        process.wait(timeout=10)


with tempfile.TemporaryDirectory() as temp:
    env = os.environ.copy()
    env['ELCCC_DB_PATH'] = str(Path(temp) / 'inquiries.sqlite3')
    configure_staff(env, temp)
    try:
        backend = start([BACKEND_PYTHON, '-m', 'uvicorn', 'app.main:app', '--host',
                         '127.0.0.1', '--port', '8000'], ROOT / 'backend', env,
                        'http://127.0.0.1:8000/health')
        for port in [5500, 5501]:
            start([sys.executable, 'scripts/serve-local.py', '--port', str(port)],
                  ROOT, env, 'http://127.0.0.1:' + str(port))
        with sync_playwright() as p:
            executable = os.environ.get('CHROMIUM_PATH')
            if not executable and Path('/usr/bin/chromium').exists():
                executable = '/usr/bin/chromium'
            browser = p.chromium.launch(executable_path=executable, args=['--no-sandbox'])
            page = browser.new_page()
            legacy_profile_components(page)
            staff_login(page)
            errors, posts = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: posts.append(json.loads(request.post_data))
                    if request.method == 'POST' and '/api/inquiries' in request.url else None)

            def open_form():
                page.evaluate("state.view='client';state.demoRole='Client';state.bookingCounselor=counselors.find(c=>c.id==='rachel-kim');state.bookingSubmitted=false;state.inquirySaveError='';render()")

            def open_admin():
                page.evaluate("state.bookingCounselor=null;selectDemoRole('Admin');state.activeAdminPanel='appointments';render()")
                archive = page.get_by_text('Saved inquiry archive', exact=True)
                if not archive.evaluate('el => el.parentElement.open'):
                    archive.click()

            page.goto('http://127.0.0.1:5500')
            for pathway, category in [('Anxiety', 'individual'), ('Grief', 'individual'),
                                      ('Marriage', 'couples'), ('Children', 'family')]:
                mapped = page.evaluate("pathway => inquiryPayload({get:key => ({name:'Jordan Demo', concern:pathway, preferred_contact_method:'email', fictional_data_only:'on'})[key]})", pathway)
                assert mapped['category'] == category
            open_form()
            page.get_by_label('Support pathway').select_option('Marriage')
            page.get_by_label('Preferred contact method (preference only)').select_option('phone')
            page.get_by_label('I confirm this is a test record and contains no real patient information.').check()
            page.get_by_role('button', name='Submit Request', exact=True).click()
            page.locator('.confirmation').get_by_text('Saved to the local development database.', exact=False).wait_for()
            assert posts == [dict(fictional_client_name='Jordan Demo', category='couples',
                                  preferred_contact_method='phone', fictional_data_only=True)], posts
            assert page.evaluate('state.demoRequests.length') == 1
            page.get_by_role('button', name='Open Admin CRM', exact=True).click()
            page.get_by_text('Saved inquiry archive', exact=True).click()
            panel = page.locator('[data-saved-inquiries]')
            panel.get_by_text('4 saved inquiries.', exact=True).wait_for()
            assert 'Jordan Demo' in panel.inner_text()
            inquiry_id = page.evaluate('state.lastSavedInquiryId')
            assert page.locator('[aria-label="Admin work areas"] button').all_text_contents() == ['Overview','Intake','Clients','Appointments','Care Journey','Reports']
            assert page.locator('[data-admin-panel=settings]').count() == 0
            # Phase 3: independent invitation tracking, confirmed conversion, and history.
            page.get_by_role('button', name='Clients', exact=True).click()
            page.get_by_role('button', name='Established Clients', exact=True).click()
            page.get_by_text('No established clients yet.', exact=True).wait_for()
            page.get_by_role('button', name='Prospective Clients', exact=True).click()
            page.get_by_text('4 prospective clients.', exact=True).wait_for()
            page.get_by_label('Search clients', exact=True).fill(inquiry_id)
            assert page.locator('[data-managed-record]').count() == 1
            page.get_by_label('Search clients', exact=True).fill('No fictional match')
            page.get_by_text('No clients match the current filters.', exact=True).wait_for()
            page.get_by_role('button', name='Clear filters', exact=True).click()
            page.get_by_label('Sort clients', exact=True).select_option('za')
            names = page.locator('[data-managed-record] h3').all_text_contents()
            assert names == sorted(names, reverse=True)
            page.get_by_label('Sort clients', exact=True).select_option('newest')
            page.get_by_role('button', name='Name', exact=True).click()
            assert page.get_by_label('Sort clients', exact=True).input_value() == 'az'
            page.get_by_role('button', name='Name', exact=True).click()
            assert page.get_by_label('Sort clients', exact=True).input_value() == 'za'
            assert page.get_by_role('columnheader', name='Name', exact=True).get_attribute('aria-sort') == 'descending'
            page.get_by_role('button', name='Last Activity', exact=True).click()
            assert page.get_by_label('Sort clients', exact=True).input_value() == 'recent'
            records = page.request.get('http://127.0.0.1:8000/api/prospective-clients').json()
            expected = sorted(records, key=lambda r: (-int(datetime.fromisoformat(max(e['occurred_at'] for e in r['history']).replace('Z', '+00:00')).timestamp() * 1000), r['inquiry_id']))
            actual = page.locator('[data-managed-record]').evaluate_all('els => els.map(el => el.dataset.managedRecord)')
            assert actual == [r['inquiry_id'] for r in expected]
            activity_header = page.get_by_role('button', name='Last Activity', exact=True)
            activity_header.focus()
            activity_header.press('Enter')
            assert page.get_by_label('Sort clients', exact=True).input_value() == 'oldest'
            assert page.get_by_role('columnheader', name='Last Activity', exact=True).get_attribute('aria-sort') == 'ascending'

            page.get_by_label('Inquiry category', exact=True).select_option('couples')
            assert page.locator('[data-managed-record]').count() == 1
            page.get_by_label('Onboarding status', exact=True).select_option('Sent')
            assert page.locator('[data-managed-record]').count() == 0
            page.get_by_role('button', name='Clear filters', exact=True).click()
            page.get_by_label('Assigned counselor', exact=True).select_option('unassigned')
            assert page.locator('[data-managed-record]').count() == 4
            page.get_by_label('Client status', exact=True).select_option('established')
            page.get_by_text('No established clients yet.', exact=True).wait_for()
            page.get_by_label('Client status', exact=True).select_option('prospective')
            page.get_by_role('button', name='Clear filters', exact=True).click()

            open_selected_profile(page, inquiry_id)
            profile = page.locator('[data-managed-profile]')
            profile.get_by_text('Not converted to client.', exact=True).wait_for()
            profile.get_by_text('Planned services', exact=True).first.click()
            profile.locator('[data-onboarding-step="questionnaire"]').get_by_text('Not available', exact=True).wait_for()
            profile.get_by_role('button', name='Open intake checklist', exact=True).click()
            page.get_by_label('Preferred session time', exact=True).select_option('Evening')
            page.get_by_label('Orientation checklist', exact=True).select_option('Reviewed')
            page.get_by_role('button', name='Submit Intake Checklist', exact=True).click()
            open_admin()
            page.get_by_role('button', name='Clients', exact=True).click()
            page.get_by_role('button', name='Prospective Clients', exact=True).click()
            open_selected_profile(page, inquiry_id)
            profile.locator('[data-onboarding-step="intake"]').get_by_text('Submitted', exact=True).wait_for()

            profile.get_by_label('Portal invitation status').select_option('Sent')
            profile.get_by_role('button', name='Save invitation tracking').click()
            page.get_by_text('Invitation tracking saved locally.', exact=False).wait_for()
            profile.get_by_role('button', name='Convert to Client', exact=True).click()
            profile.get_by_role('button', name='Cancel Conversion', exact=True).click()
            profile.get_by_text('Not converted to client.', exact=True).wait_for()
            profile.get_by_role('button', name='Convert to Client', exact=True).click()
            profile.get_by_role('button', name='Confirm Conversion', exact=True).click()
            page.get_by_text('Conversion saved.', exact=False).wait_for()
            assert page.evaluate('state.activeAdminPanel') == 'established'
            assert inquiry_id in profile.inner_text()
            assert profile.get_by_label('Portal invitation status').input_value() == 'Sent'
            assert profile.get_by_role('button', name='Convert to Client', exact=True).count() == 0
            assert 'Converted to client' in profile.inner_text()
            assert profile.locator('[data-onboarding-step="intake"]').get_by_text('Submitted', exact=True).count() == 1
            profile.get_by_label('Portal invitation status').select_option('Activated')
            profile.get_by_role('button', name='Save invitation tracking').click()
            page.get_by_text('Invitation tracking saved locally.', exact=False).wait_for()
            page.get_by_role('button', name='Prospective Clients', exact=True).click()
            assert page.locator('[data-managed-record="' + inquiry_id + '"]').count() == 0
            staff_login(page)
            page.reload()
            open_admin()
            page.get_by_role('button', name='Clients', exact=True).click()
            page.get_by_role('button', name='Established Clients', exact=True).click()
            page.get_by_text('1 established clients.', exact=True).wait_for()
            open_selected_profile(page, inquiry_id)
            profile.get_by_role('heading', name='Jordan Demo profile').wait_for()
            assert profile.get_by_label('Portal invitation status').input_value() == 'Activated'
            stop(backend)
            backend = start([BACKEND_PYTHON, '-m', 'uvicorn', 'app.main:app', '--host',
                             '127.0.0.1', '--port', '8000'], ROOT / 'backend', env,
                            'http://127.0.0.1:8000/health')
            staff_login(page)
            page.get_by_role('button', name='Refresh client lists').click()
            page.get_by_text('1 established clients.', exact=True).wait_for()
            assert inquiry_id in profile.inner_text()
            assert 'MYIO tracking updated' in profile.inner_text()
            for width in [320, 375, 1280]:
                page.set_viewport_size({'width': width, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), width
                assert page.locator('[data-managed-record] h3').first.bounding_box()['height'] < 80, 'Client name must remain readable'
            page.set_viewport_size({'width': 1280, 'height': 900})
            if os.environ.get('QA_SCREENSHOTS'):
                (ROOT / 'work').mkdir(exist_ok=True)
                page.screenshot(path=str(ROOT / 'work' / 'refined-established.png'), full_page=True)
                page.set_viewport_size({'width': 375, 'height': 900})
                page.screenshot(path=str(ROOT / 'work' / 'refined-established-mobile.png'), full_page=True)
                page.set_viewport_size({'width': 1280, 'height': 900})
            # Profile/list errors are shown without inventing records.
            page.route('**/api/clients?include_archived=true', lambda route: route.fulfill(status=503,
                       content_type='application/json', body='{"detail":"Database unavailable"}'))
            page.get_by_role('button', name='Refresh client lists').click()
            page.get_by_text('Could not load client lists.', exact=False).wait_for()
            page.unroute('**/api/clients?include_archived=true')
            open_admin()
            # Failed POST does not fabricate a saved record; the user can retry.
            page.route('**/api/inquiries', lambda route: route.fulfill(status=422,
                       content_type='application/json', body=json.dumps({'detail':'Fictional validation failure'}))
                       if route.request.method == 'POST' else route.continue_())
            open_form()
            page.get_by_label('I confirm this is a test record and contains no real patient information.').check()
            page.get_by_role('button', name='Submit Request', exact=True).click()
            page.get_by_text('Request was not confirmed saved.', exact=False).wait_for()
            assert page.evaluate('state.demoRequests.length') == 0
            page.unroute('**/api/inquiries')
            stop(backend)
            page.get_by_role('button', name='Submit Request', exact=True).click()
            page.get_by_text('Cannot reach the local backend.', exact=False).wait_for()
            assert page.evaluate('state.demoRequests.length') == 0
            open_admin()
            page.get_by_role('button', name='Refresh saved inquiries').click()
            panel.get_by_text('Could not refresh saved inquiries.', exact=False).wait_for()
            assert inquiry_id in panel.inner_text()
            # Any other frontend origin retains the static demo without backend calls.
            other = browser.new_page()
            requests = []
            other.on('request', lambda request: requests.append(request.url))
            other.goto('http://127.0.0.1:5501/?tools=1')
            other.evaluate("state.bookingCounselor=counselors[0];render()")
            other.get_by_role('button', name='Submit Request', exact=True).click()
            assert other.evaluate('state.demoRequests.length') == 1
            assert not any(':8000' in url for url in requests)
            assert not errors, errors
            browser.close()
        print('PASS: local CORS POST/GET, exact schema, persistent Admin list, refresh/restart, validation/network failures, no false saves, static-origin isolation, Phase 3 navigation, confirmation/cancellation, independent portal tracking, history, and conversion refresh/restart persistence.')
    finally:
        for process in reversed(processes):
            stop(process)
            if process.stderr:
                process.stderr.close()
