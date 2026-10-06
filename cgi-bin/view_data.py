#!/usr/bin/env python3
"""
CGI Script: Data Viewer (cgi-bin/view_data.py)
Retrieves and displays all submitted student records from SQLite.
Supports searching by keyword, filtering by department, and record deletion.
Outputs standard HTML via CGI STDOUT.
"""

import os
import sys
import html
import urllib.parse

# Reconfigure stdout to UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.service import (
    get_all_registrations, 
    get_registration_stats, 
    delete_registration, 
    VALID_DEPARTMENTS
)


def parse_query_params():
    """Parses GET query string parameters from os.environ['QUERY_STRING']."""
    query_string = os.environ.get("QUERY_STRING", "")
    parsed = urllib.parse.parse_qs(query_string, keep_blank_values=True)
    params = {}
    for k, v in parsed.items():
        params[k] = v[0] if v else ""
    return params


def handle_request():
    params = parse_query_params()
    action = params.get("action", "")
    delete_msg = None

    # Handle record deletion if requested
    if action == "delete" and "id" in params:
        try:
            record_id = int(params["id"])
            if delete_registration(record_id):
                delete_msg = f"Record #{record_id} was successfully removed from SQLite database."
            else:
                delete_msg = f"Record #{record_id} could not be found."
        except ValueError:
            delete_msg = "Invalid record ID for deletion."

    # Extract filter parameters
    search_q = params.get("search", "").strip()
    dept_filter = params.get("department", "").strip()

    # Query records and summary metrics
    records = get_all_registrations(
        search_query=search_q if search_q else None,
        department_filter=dept_filter if dept_filter else None
    )
    stats = get_registration_stats()

    # CGI Headers
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")

    # Build Department Options for Dropdown
    dept_options_html = '<option value="">All Departments</option>'
    for d in VALID_DEPARTMENTS:
        selected = 'selected="selected"' if d == dept_filter else ''
        dept_options_html += f'<option value="{html.escape(d)}" {selected}>{html.escape(d)}</option>'

    # Build Table Rows
    if records:
        table_rows = ""
        for rec in records:
            r_id = rec["id"]
            name = html.escape(rec["full_name"])
            email = html.escape(rec["email"])
            phone = html.escape(rec["phone"])
            age = html.escape(str(rec["age"]))
            dept = html.escape(rec["department"])
            msg = html.escape(rec["message"] or "")
            msg_snippet = msg if msg else "<span class='text-muted'>-</span>"
            submitted = html.escape(str(rec["submitted_at"]))

            table_rows += f"""
            <tr>
                <td class="col-id"><span class="badge badge-id">#{r_id}</span></td>
                <td class="col-name">
                    <strong>{name}</strong>
                    <div class="table-subtext">{email}</div>
                </td>
                <td class="col-contact">
                    <div>{phone}</div>
                    <div class="table-subtext">{age} yrs old</div>
                </td>
                <td class="col-dept">
                    <span class="badge badge-dept">{dept}</span>
                </td>
                <td class="col-msg">
                    <div class="message-cell" title="{msg}">{msg_snippet}</div>
                </td>
                <td class="col-date">
                    <span class="date-badge">{submitted}</span>
                </td>
                <td class="col-actions">
                    <a href="/cgi-bin/view_data.py?action=delete&id={r_id}" 
                       class="btn-delete" 
                       onclick="return confirm('Are you sure you want to delete record #{r_id} for {name}?');"
                       title="Delete record">
                        🗑️ Delete
                    </a>
                </td>
            </tr>
            """
    else:
        table_rows = """
        <tr>
            <td colspan="7" class="empty-state">
                <div class="empty-illustration">📭</div>
                <h3>No Student Records Found</h3>
                <p>No matching submissions found in the database. Use the button below to register a student.</p>
                <a href="/index.html" class="btn btn-primary" style="margin-top: 1rem;">Go to Registration Form</a>
            </td>
        </tr>
        """

    # Alert notification if deletion took place
    delete_banner_html = ""
    if delete_msg:
        delete_banner_html = f"""
        <div class="alert alert-info animate-fade-in" style="margin-bottom: 1.5rem;">
            <span>ℹ️ {html.escape(delete_msg)}</span>
            <a href="/cgi-bin/view_data.py" class="alert-close">✕</a>
        </div>
        """

    # Print Full HTML Document
    html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Records - Python CGI</title>
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
                    <span class="badge badge-tech">Database Viewer (SQLite ⇄ CGI)</span>
                </div>
            </div>
            <nav class="nav-links">
                <a href="/index.html" class="nav-btn nav-btn-primary">+ New Registration</a>
                <a href="/cgi-bin/view_data.py" class="nav-btn">Refresh Data 🔄</a>
            </nav>
        </div>
    </header>

    <main class="main-container wide">
        {delete_banner_html}

        <!-- Top Metrics Cards -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-content">
                    <span class="metric-label">Total Registrations</span>
                    <span class="metric-value">{stats['total_registrations']}</span>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🏛️</div>
                <div class="metric-content">
                    <span class="metric-label">Departments Active</span>
                    <span class="metric-value">{len(stats['department_counts'])}</span>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🕒</div>
                <div class="metric-content">
                    <span class="metric-label">Latest Submission</span>
                    <span class="metric-value text-small">{html.escape(str(stats['latest_submission']))}</span>
                </div>
            </div>
        </div>

        <!-- Filter & Search Section -->
        <div class="card card-filters">
            <form method="GET" action="/cgi-bin/view_data.py" class="filter-form">
                <div class="filter-group">
                    <label for="search">Search Name, Email, or Phone:</label>
                    <input type="text" id="search" name="search" placeholder="Type keyword to search..." value="{html.escape(search_q)}" class="form-input">
                </div>
                <div class="filter-group">
                    <label for="department">Filter by Department:</label>
                    <select id="department" name="department" class="form-select">
                        {dept_options_html}
                    </select>
                </div>
                <div class="filter-actions">
                    <button type="submit" class="btn btn-primary">Filter Records 🔍</button>
                    <a href="/cgi-bin/view_data.py" class="btn btn-secondary">Clear Filters</a>
                </div>
            </form>
        </div>

        <!-- Data Table Card -->
        <div class="card card-table">
            <div class="table-header">
                <div>
                    <h2>Registered Students Roster</h2>
                    <p class="text-muted">Directly queried from SQLite (<code>database/app.db</code>) via Python CGI</p>
                </div>
                <span class="badge badge-count">{len(records)} record(s) shown</span>
            </div>

            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student</th>
                            <th>Contact &amp; Age</th>
                            <th>Department</th>
                            <th>Notes</th>
                            <th>Timestamp</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Educational CGI Architecture Walkthrough -->
        <div class="cgi-inspector-box">
            <div class="inspector-header">
                <span class="inspector-title">💡 How this page was rendered via CGI</span>
                <span class="pill pill-live">CGI GET REQUEST</span>
            </div>
            <p style="margin-bottom: 0.75rem; color: var(--text-secondary); font-size: 0.9rem;">
                When you loaded this page, the browser made an <strong>HTTP GET</strong> request to <code>/cgi-bin/view_data.py</code>.
                The CGI web server invoked this Python script as a standalone process, passing query parameters via <code>QUERY_STRING</code>.
                The script connected to the SQLite database via <code>backend/service.py</code>, retrieved the rows, generated this complete HTML page,
                printed the <code>Content-Type: text/html</code> HTTP header, and streamed the HTML output to <code>stdout</code>.
            </p>
        </div>
    </main>

    <footer class="app-footer">
        <div class="footer-container">
            <p>Python CGI Web Application Architecture Project</p>
            <div class="cgi-badge-group">
                <span class="pill">SQLite 3</span>
                <span class="pill">CGI 1.1</span>
                <span class="pill">Vanilla CSS</span>
            </div>
        </div>
    </footer>
</body>
</html>"""
    print(html_output)


if __name__ == "__main__":
    handle_request()
