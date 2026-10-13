"""Integration check. Needs backend dev dependencies and Playwright/Chromium.
Run from repository root: python scripts/check-backend-integration.py
Ports 5500, 5501, and 8000 must be free. Uses a temporary database only.
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
    try:
        backend = start([BACKEND_PYTHON, '-m', 'uvicorn', 'app.main:app', '--host',
                         '127.0.0.1', '--port', '8000'], ROOT / 'backend', env,
                        'http://127.0.0.1:8000/health')
        for port in [5500, 5501]:
            start([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1'],
                  ROOT, env, 'http://127.0.0.1:' + str(port))
        with sync_playwright() as p:
            executable = os.environ.get('CHROMIUM_PATH')
            if not executable and Path('/usr/bin/chromium').exists():
                executable = '/usr/bin/chromium'
            browser = p.chromium.launch(executable_path=executable, args=['--no-sandbox'])
            page = browser.new_page()
            errors, posts = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: posts.append(json.loads(request.post_data))
                    if request.method == 'POST' and '/api/inquiries' in request.url else None)

            def open_form():
                page.evaluate("state.bookingCounselor=counselors.find(c=>c.id==='rachel-kim');state.bookingSubmitted=false;state.inquirySaveError='';render()")

            def open_admin():
                page.evaluate("state.bookingCounselor=null;selectDemoRole('Admin');state.activeAdminPanel='appointments';render()")

            page.goto('http://127.0.0.1:5500')
            for pathway, category in [('Anxiety', 'individual'), ('Grief', 'individual'),
                                      ('Marriage', 'couples'), ('Children', 'family')]:
                mapped = page.evaluate("pathway => inquiryPayload({get:key => ({name:'Jordan Demo', concern:pathway, preferred_contact_method:'email', fictional_data_only:'on'})[key]})", pathway)
                assert mapped['category'] == category
            open_form()
            page.get_by_label('Support pathway').select_option('Marriage')
            page.get_by_label('Preferred contact method (preference only)').select_option('phone')
            page.get_by_label('I confirm this is fictional demonstration data only.').check()
            page.get_by_role('button', name='Submit Fictional Request', exact=True).click()
            page.locator('.confirmation').get_by_text('Saved to the local development database.', exact=False).wait_for()
            assert posts == [dict(fictional_client_name='Jordan Demo', category='couples',
                                  preferred_contact_method='phone', fictional_data_only=True)], posts
            assert page.evaluate('state.demoRequests.length') == 1
            page.get_by_role('button', name='Switch to Administrator Demo', exact=True).click()
            panel = page.locator('[data-saved-inquiries]')
            panel.get_by_text('4 saved fictional inquiries.', exact=True).wait_for()
            assert 'Jordan Demo' in panel.inner_text()
            inquiry_id = page.evaluate('state.lastSavedInquiryId')
            page.reload()
            open_admin()
            panel.get_by_text('4 saved fictional inquiries.', exact=True).wait_for()
            assert inquiry_id in panel.inner_text()
            stop(backend)
            backend = start([BACKEND_PYTHON, '-m', 'uvicorn', 'app.main:app', '--host',
                             '127.0.0.1', '--port', '8000'], ROOT / 'backend', env,
                            'http://127.0.0.1:8000/health')
            page.get_by_role('button', name='Refresh saved inquiries').click()
            panel.get_by_text('4 saved fictional inquiries.', exact=True).wait_for()
            assert inquiry_id in panel.inner_text()
            # Failed POST does not fabricate a saved record; the user can retry.
            page.route('**/api/inquiries', lambda route: route.fulfill(status=422,
                       content_type='application/json', body=json.dumps({'detail':'Fictional validation failure'}))
                       if route.request.method == 'POST' else route.continue_())
            open_form()
            page.get_by_label('I confirm this is fictional demonstration data only.').check()
            page.get_by_role('button', name='Submit Fictional Request', exact=True).click()
            page.get_by_text('Request was not confirmed saved.', exact=False).wait_for()
            assert page.evaluate('state.demoRequests.length') == 0
            page.unroute('**/api/inquiries')
            stop(backend)
            page.get_by_role('button', name='Submit Fictional Request', exact=True).click()
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
            other.goto('http://127.0.0.1:5501')
            other.evaluate("state.bookingCounselor=counselors[0];render()")
            other.get_by_role('button', name='Submit Fictional Request', exact=True).click()
            assert other.evaluate('state.demoRequests.length') == 1
            assert not any(':8000' in url for url in requests)
            assert not errors, errors
            browser.close()
        print('PASS: local CORS POST/GET, exact schema, persistent Admin list, refresh/restart, validation/network failures, no false saves, and static-origin isolation.')
    finally:
        for process in reversed(processes):
            stop(process)
            if process.stderr:
                process.stderr.close()
