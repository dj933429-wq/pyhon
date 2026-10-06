#!/usr/bin/env python3
"""
Python CGI Web Application Server
Starts an HTTP CGI server capable of serving static assets (HTML/CSS/JS)
and executing Python CGI scripts located in /cgi-bin/.
"""

import os
import sys
import socket
from http.server import HTTPServer, CGIHTTPRequestHandler

# Set working directory to project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

# Ensure UTF-8 output encoding across all operating systems
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Add project root to sys.path so modules in backend/ are importable
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import init_db

DEFAULT_PORT = 8000


class AppCGIHandler(CGIHTTPRequestHandler):
    """Custom CGI request handler configured for the application."""
    
    # Restrict CGI execution strictly to the /cgi-bin directory
    cgi_directories = ["/cgi-bin"]

    def log_message(self, format, *args):
        """Custom formatted log output for educational clarity."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def is_port_in_use(port: int) -> bool:
    """Checks if a given TCP port is currently open/bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_available_port(start_port: int = DEFAULT_PORT) -> int:
    """Finds the first available port starting from start_port."""
    port = start_port
    while port < start_port + 50:
        if not is_port_in_use(port):
            return port
        port += 1
    return start_port


def run_server():
    # 1. Initialize SQLite Database Schema
    db_path = init_db()
    
    # 2. Determine Port
    port = find_available_port(DEFAULT_PORT)
    server_address = ("", port)
    
    try:
        httpd = HTTPServer(server_address, AppCGIHandler)
    except OSError as e:
        print(f"[ERROR] Could not start server on port {port}: {e}")
        sys.exit(1)

    url = f"http://localhost:{port}"

    banner = f"""
================================================================================
          PYTHON CGI WEB APPLICATION (CGI 1.1 + SQLite)
================================================================================
  Server URL        : {url}
  Form (Frontend)   : {url}/index.html
  Database Viewer   : {url}/cgi-bin/view_data.py
  Database File     : {db_path}
  CGI Directory     : {os.path.join(PROJECT_ROOT, 'cgi-bin')}

  ARCHITECTURAL DATA FLOW:
  1. Frontend (HTML5/CSS3/JS)
     --> User fills form and JS validates inputs
  2. HTTP Request (POST /cgi-bin/submit.py)
     --> Browser sends application/x-www-form-urlencoded
  3. Python CGI Gateway
     --> HTTP server sets ENV vars & pipes payload to STDIN of submit.py
  4. Backend / Database (backend/service.py & database/app.db)
     --> Validates data & executes SQL INSERT in SQLite
  5. CGI Response
     --> submit.py prints 'Content-Type: text/html' header + HTML body to STDOUT
  6. Browser Display
     --> User views styled HTML confirmation or error page directly!

  [Press Ctrl+C to stop the server]
================================================================================
"""
    print(banner)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received. Shutting down server gracefully...")
    finally:
        httpd.server_close()
        print("[INFO] Server stopped.")


if __name__ == "__main__":
    run_server()
