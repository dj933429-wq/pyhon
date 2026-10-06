"""
Automated Test Verification Script for CGI Application
Spawns the CGI HTTP server, submits valid and invalid test data, and verifies responses.
"""

import http.server
import threading
import urllib.request
import urllib.parse
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import init_db
from backend.service import get_all_registrations


class AppCGIHandler(http.server.CGIHTTPRequestHandler):
    cgi_directories = ["/cgi-bin"]


def run_tests():
    init_db()
    port = 8912
    server = http.server.HTTPServer(("127.0.0.1", port), AppCGIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)

    base = f"http://127.0.0.1:{port}"

    print("Running verification test suite...")

    # Test 1: Fetch static index.html
    req1 = urllib.request.urlopen(f"{base}/index.html")
    assert req1.status == 200, f"Expected 200, got {req1.status}"
    html1 = req1.read().decode("utf-8")
    assert 'id="registration-form"' in html1
    print("  [PASS] Test 1: index.html served successfully with HTTP 200")

    # Test 2: Fetch CSS & JS
    req_css = urllib.request.urlopen(f"{base}/css/style.css")
    assert req_css.status == 200
    print("  [PASS] Test 2a: CSS stylesheet loaded successfully")
    req_js = urllib.request.urlopen(f"{base}/js/app.js")
    assert req_js.status == 200
    print("  [PASS] Test 2b: JavaScript validation script loaded successfully")

    # Test 3: Submit valid registration via POST to CGI
    form_payload = urllib.parse.urlencode({
        "full_name": "Devon Vance",
        "email": "devon.vance@university.edu",
        "phone": "+1 555-987-6543",
        "age": "22",
        "department": "Artificial Intelligence & Machine Learning",
        "message": "Excited to study CGI and distributed systems architecture."
    }).encode("utf-8")

    req3 = urllib.request.Request(
        f"{base}/cgi-bin/submit.py",
        data=form_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    res3 = urllib.request.urlopen(req3)
    assert res3.status == 200
    html3 = res3.read().decode("utf-8")
    assert "Registration Successful!" in html3
    assert "Devon Vance" in html3
    assert "LIVE CGI ENV" in html3
    print("  [PASS] Test 3: POST /cgi-bin/submit.py executed, DB row inserted, and HTML confirmation rendered")

    # Test 4: Query records via GET to /cgi-bin/view_data.py
    req4 = urllib.request.urlopen(f"{base}/cgi-bin/view_data.py")
    assert req4.status == 200
    html4 = req4.read().decode("utf-8")
    assert "Devon Vance" in html4
    assert "Total Registrations" in html4
    assert "Registered Students Roster" in html4
    print("  [PASS] Test 4: GET /cgi-bin/view_data.py executed, SQLite queried, and HTML table rendered")

    # Test 5: Verify server-side validation error handling
    bad_payload = urllib.parse.urlencode({
        "full_name": "X",
        "email": "invalid-email-address",
        "phone": "123",
        "age": "10",
        "department": "Unknown Department",
        "message": ""
    }).encode("utf-8")

    req5 = urllib.request.Request(
        f"{base}/cgi-bin/submit.py",
        data=bad_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    res5 = urllib.request.urlopen(req5)
    assert res5.status == 200
    html5 = res5.read().decode("utf-8")
    assert "Validation Failed on Server" in html5
    assert "Full Name must be between 2 and 80 characters." in html5
    assert "Please provide a valid email address" in html5
    print("  [PASS] Test 5: Server-side validation cleanly rejected corrupt inputs and returned styled error page")

    server.shutdown()
    print("\n[ALL TESTS PASSED SUCCESSFULLY] The CGI architecture is fully verified.")


if __name__ == "__main__":
    run_tests()
