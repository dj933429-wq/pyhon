#!/usr/bin/env python3
"""
CGI Script: Submit Handler (cgi-bin/submit.py)
Acts as the CGI bridge between the HTTP client and the Python backend/database.
Reads HTTP POST data from STDIN, executes backend validation, saves to SQLite,
and writes an HTML response back to STDOUT with HTTP headers.
"""

import os
import sys
import html
import urllib.parse

# Reconfigure stdout to UTF-8 for reliable multi-platform output
sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path so backend package is importable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.service import create_registration, VALID_DEPARTMENTS


def parse_cgi_form_data():
    """
    Parses form data from the standard CGI environment.
    Uses sys.stdin.read(CONTENT_LENGTH) for POST requests or QUERY_STRING for GET requests.
    """
    method = os.environ.get("REQUEST_METHOD", "GET").upper()
    data = {}

    if method == "POST":
        try:
            content_length = int(os.environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        raw_body = sys.stdin.read(content_length) if content_length > 0 else ""
        parsed = urllib.parse.parse_qs(raw_body, keep_blank_values=True)
        # Flatten lists into single values
        for key, vals in parsed.items():
            data[key] = vals[0] if vals else ""
    else:
        # Fallback for GET queries
        query_string = os.environ.get("QUERY_STRING", "")
        parsed = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        for key, vals in parsed.items():
            data[key] = vals[0] if vals else ""

    return method, data


def render_html_page(title: str, body_content: str):
    """Generates the full HTML response document wrapped in our modern aesthetic styling."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - Student Portal CGI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/style.css">
</head>
<body class="cgi-page">
    <header class="app-header">
        <div class="header-container">
            <div class="brand">
                <div class="brand-icon">⚡</div>
                <div class="brand-text">
                    <h1>Python CGI Web Application</h1>
                    <span class="badge badge-tech">HTTP ⇄ Python CGI ⇄ SQLite Pipeline</span>
                </div>
            </div>
            <nav class="nav-links">
                <a href="/index.html" class="nav-btn">← Back to Form</a>
                <a href="/cgi-bin/view_data.py" class="nav-btn nav-btn-primary">View All Records 🗄️</a>
            </nav>
        </div>
    </header>

    <main class="main-container">
        {body_content}
    </main>

    <footer class="app-footer">
        <div class="footer-container">
            <p>Demonstrating Common Gateway Interface (CGI) architecture with Python 3 and SQLite.</p>
            <div class="cgi-badge-group">
                <span class="pill">CGI 1.1 Specification</span>
                <span class="pill">Server-Side Python</span>
                <span class="pill">Direct HTML Output</span>
            </div>
        </div>
    </footer>
</body>
</html>"""


def handle_request():
    # 1. Parse CGI Environment and Input
    method, form_data = parse_cgi_form_data()
    client_ip = os.environ.get("REMOTE_ADDR", "127.0.0.1")
    user_agent = os.environ.get("HTTP_USER_AGENT", "Unknown")
    content_len = os.environ.get("CONTENT_LENGTH", "0")
    server_software = os.environ.get("SERVER_SOFTWARE", "Python CGI Server")
    gateway_interface = os.environ.get("GATEWAY_INTERFACE", "CGI/1.1")

    # 2. Output HTTP Headers
    # Every CGI script must emit valid HTTP headers separated by a blank line (\r\n\r\n)
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")

    if method != "POST":
        # Handle inadvertent GET request to submit endpoint
        body = f"""
        <div class="card card-warning animate-fade-in">
            <div class="result-header">
                <span class="result-icon icon-warning">⚠️</span>
                <h2>Direct GET Access Detected</h2>
            </div>
            <p class="result-desc">
                The <code>/cgi-bin/submit.py</code> endpoint is designed to accept <strong>HTTP POST</strong> 
                requests submitted from the registration form.
            </p>
            <div class="action-row">
                <a href="/index.html" class="btn btn-primary">Go to Registration Form</a>
                <a href="/cgi-bin/view_data.py" class="btn btn-secondary">View Existing Records</a>
            </div>
        </div>
        """
        print(render_html_page("Invalid Request Method", body))
        return

    # 3. Add client metadata to submission payload
    form_data["ip_address"] = client_ip
    form_data["user_agent"] = user_agent

    # 4. Invoke backend service for validation and SQLite persistence
    success, record_id, errors = create_registration(form_data)

    if success:
        # Build success content
        name_safe = html.escape(form_data.get("full_name", ""))
        email_safe = html.escape(form_data.get("email", ""))
        phone_safe = html.escape(form_data.get("phone", ""))
        age_safe = html.escape(str(form_data.get("age", "")))
        dept_safe = html.escape(form_data.get("department", ""))
        msg_safe = html.escape(form_data.get("message", ""))
        msg_display = msg_safe if msg_safe else "<em class='text-muted'>No message provided</em>"

        body = f"""
        <div class="card card-success animate-fade-in">
            <div class="result-header">
                <div class="result-icon icon-success">✓</div>
                <div>
                    <h2>Registration Successful!</h2>
                    <p class="result-subtitle">Data received via HTTP POST, processed by Python CGI, and committed to SQLite.</p>
                </div>
            </div>

            <div class="record-summary-card">
                <div class="record-id-banner">
                    <span class="record-label">Assigned Database Record ID:</span>
                    <span class="badge badge-id">#{record_id}</span>
                </div>

                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-key">Full Name</span>
                        <span class="summary-val">{name_safe}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-key">Email Address</span>
                        <span class="summary-val">{email_safe}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-key">Phone Number</span>
                        <span class="summary-val">{phone_safe}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-key">Age</span>
                        <span class="summary-val">{age_safe} years</span>
                    </div>
                    <div class="summary-item summary-full">
                        <span class="summary-key">Department / Course</span>
                        <span class="summary-val"><span class="badge badge-dept">{dept_safe}</span></span>
                    </div>
                    <div class="summary-item summary-full">
                        <span class="summary-key">Message / Notes</span>
                        <span class="summary-val summary-msg">{msg_display}</span>
                    </div>
                </div>
            </div>

            <!-- CGI Diagnostic Inspector (Educational/Viva proof) -->
            <div class="cgi-inspector-box">
                <div class="inspector-header">
                    <span class="inspector-title">🔍 CGI Protocol &amp; HTTP Transaction Details</span>
                    <span class="pill pill-live">LIVE CGI ENV</span>
                </div>
                <div class="inspector-grid">
                    <div class="inspector-row">
                        <code>REQUEST_METHOD</code>
                        <span>{html.escape(method)}</span>
                    </div>
                    <div class="inspector-row">
                        <code>CONTENT_LENGTH</code>
                        <span>{html.escape(str(content_len))} bytes</span>
                    </div>
                    <div class="inspector-row">
                        <code>CONTENT_TYPE</code>
                        <span>{html.escape(os.environ.get("CONTENT_TYPE", "application/x-www-form-urlencoded"))}</span>
                    </div>
                    <div class="inspector-row">
                        <code>GATEWAY_INTERFACE</code>
                        <span>{html.escape(gateway_interface)}</span>
                    </div>
                    <div class="inspector-row">
                        <code>SERVER_SOFTWARE</code>
                        <span>{html.escape(server_software)}</span>
                    </div>
                    <div class="inspector-row">
                        <code>REMOTE_ADDR</code>
                        <span>{html.escape(client_ip)}</span>
                    </div>
                </div>
            </div>

            <div class="action-buttons-group">
                <a href="/cgi-bin/view_data.py" class="btn btn-primary btn-lg">
                    <span>View All Database Records</span> ➔
                </a>
                <a href="/index.html" class="btn btn-secondary btn-lg">
                    <span>Submit Another Application</span> ↺
                </a>
            </div>
        </div>
        """
        print(render_html_page("Registration Successful", body))
    else:
        # Build server-side validation error response
        error_items = "".join(f"<li>{html.escape(err)}</li>" for err in errors)
        body = f"""
        <div class="card card-danger animate-fade-in">
            <div class="result-header">
                <div class="result-icon icon-error">✕</div>
                <div>
                    <h2>Validation Failed on Server</h2>
                    <p class="result-subtitle">Python CGI backend rejected the submitted data due to validation constraints.</p>
                </div>
            </div>

            <div class="error-box">
                <h4>Issues Identified by Server-Side Validation:</h4>
                <ul class="error-list">
                    {error_items}
                </ul>
            </div>

            <div class="action-buttons-group">
                <a href="javascript:history.back()" class="btn btn-primary">
                    ← Back to Correct Form
                </a>
                <a href="/index.html" class="btn btn-secondary">
                    Reset Form
                </a>
            </div>
        </div>
        """
        print(render_html_page("Registration Failed", body))


if __name__ == "__main__":
    handle_request()
