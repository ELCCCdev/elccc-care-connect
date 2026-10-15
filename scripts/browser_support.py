"""Synthetic local staff fixtures; never use these keys outside disposable tests."""
import json
from pathlib import Path

ADMIN_KEY = 'synthetic-browser-admin-test-key-only'
RACHEL_KEY = 'synthetic-browser-rachel-test-key-only'
MELISSA_KEY = 'synthetic-browser-melissa-test-key-only'


def configure_staff(env, temp):
    path = Path(temp) / 'staff-access.json'
    path.write_text(json.dumps([
        dict(role='administrator', counselor_id=None, key=ADMIN_KEY),
        dict(role='counselor', counselor_id='rachel-kim', key=RACHEL_KEY),
        dict(role='counselor', counselor_id='melissa-smith', key=MELISSA_KEY)]))
    env['ELCCC_ACCESS_PATH'] = str(path)


def staff_login(page, key=ADMIN_KEY):
    response = page.request.post('http://127.0.0.1:8000/api/staff/login', data={'key': key})
    assert response.status == 200, response.text()


def legacy_profile_components(page):
    # Keep earlier component regressions; new-tab routing is tested without overrides
    # in check-counselor-profiles.py. No application test flag or access bypass exists.
    page.add_init_script("window.addEventListener('DOMContentLoaded',()=>{openManagedProfile=loadManagedProfile;});")
