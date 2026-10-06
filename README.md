# Python CGI Web Application

A complete, runnable **Python Common Gateway Interface (CGI)** web application demonstrating how an HTML frontend communicates with a Python backend and persistent SQLite database through standard CGI and HTTP.

---

## 📌 Project Architecture & Data Flow

This application is built to demonstrate the foundational end-to-end request/response cycle of the Web:

```text
┌─────────────────┐       HTTP POST        ┌─────────────────────┐
│   HTML5 / CSS3  │ ─────────────────────> │   HTTP Web Server   │
│   JavaScript    │                        │  (server.py :8000)  │
└─────────────────┘                        └──────────┬──────────┘
  (Browser Client)                                    │ Spawns Subprocess
                                                      │ Sets ENV vars (REQUEST_METHOD, etc.)
                                                      │ Pipes Body to STDIN
                                                      ▼
┌─────────────────┐                        ┌─────────────────────┐
│   Browser View  │ <───────────────────── │  Python CGI Script  │
│ (Rendered HTML) │     STDOUT / Stream    │ (cgi-bin/submit.py) │
└─────────────────┘   Content-Type: text/html└──────────┬──────────┘
                                                      │ Calls backend
                                                      ▼
                                           ┌─────────────────────┐
                                           │   Backend Service   │
                                           │ (backend/service.py)│
                                           └──────────┬──────────┘
                                                      │ Parameterized SQL
                                                      ▼
                                           ┌─────────────────────┐
                                           │   SQLite Database   │
                                           │  (database/app.db)  │
                                           └─────────────────────┘
```

### Step-by-Step Data Flow:
1. **Frontend Input & Client Validation**:
   - The user fills out the registration form in `index.html`.
   - `js/app.js` runs client-side validation (checks required fields, email format, phone format, age range, department selection).
   - If invalid, submission is intercepted and clear error feedback is shown.
2. **HTTP Request**:
   - The browser sends an `HTTP POST` request to `/cgi-bin/submit.py` with payload encoded as `application/x-www-form-urlencoded`.
3. **CGI Gateway Invocation**:
   - The server sets CGI environment variables (`REQUEST_METHOD="POST"`, `CONTENT_LENGTH`, `REMOTE_ADDR`, etc.) and invokes Python `cgi-bin/submit.py`.
   - The request payload is streamed to the script via standard input (`sys.stdin`).
4. **Backend Processing & Database Persistence**:
   - `cgi-bin/submit.py` parses the form data and forwards it to `backend/service.py`.
   - `backend/service.py` sanitizes inputs (HTML escaping to prevent XSS) and executes strict server-side validation.
   - `backend/database.py` executes a parameterized `INSERT` query into SQLite (`database/app.db`), preventing SQL injection.
5. **CGI Response Generation**:
   - `cgi-bin/submit.py` writes the HTTP response header (`Content-Type: text/html; charset=utf-8\r\n\r\n`) to standard output (`sys.stdout`).
   - It follows the header with a formatted HTML document containing confirmation details, assigned database ID, and a live CGI diagnostic inspector.
6. **Browser Rendering**:
   - The browser receives and renders the HTML response directly without needing JSON or client-side single-page framework routing.

---

## 📂 Project Directory Structure

```text
PYTHON/
├── index.html                   # Modern, accessible HTML5 registration portal
├── css/
│   └── style.css                # Polished design system (CSS custom properties, glassmorphism, responsive)
├── js/
│   └── app.js                   # Client-side validation engine & interactive feedback
├── cgi-bin/
│   ├── submit.py                # CGI POST script: parses STDIN, saves to DB, outputs HTML response
│   └── view_data.py             # CGI GET script: queries SQLite, outputs searchable HTML data table
├── backend/
│   ├── __init__.py              # Python package marker
│   ├── database.py              # SQLite connection factory, schema creation, context manager
│   └── service.py               # Validation, sanitization, CRUD operations, query helpers
├── database/
│   └── app.db                   # Persistent SQLite database (auto-created on startup)
├── server.py                    # Standalone HTTP CGI server launcher
├── test_app.py                  # Automated test verification suite
└── README.md                    # Project documentation & CGI study guide
```

---

## 🚀 How to Run the Application

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Any modern web browser (Edge, Chrome, Firefox, Safari)
- No external libraries (`pip install`) required — utilizes Python standard libraries!

### 1. Start the CGI Server
Open your terminal or PowerShell in this project directory:

```bash
python server.py
```

The server will automatically:
- Create the SQLite database directory (`database/app.db`) if not already present.
- Create the `student_registrations` table schema with appropriate indexes.
- Bind to port `8000` (or the next available port).
- Display an informative ASCII banner with direct links.

### 2. Access the Application in Your Browser
- **Student Registration Portal**: [http://localhost:8000/index.html](http://localhost:8000/index.html)
- **Database Records Viewer**: [http://localhost:8000/cgi-bin/view_data.py](http://localhost:8000/cgi-bin/view_data.py)

### 3. Run Automated Tests
To run automated verification covering static serving, CGI POST submission, SQLite persistence, CGI GET data viewing, and server-side validation error handling:

```bash
python test_app.py
```

---

## 🛠️ Key Features

### 1. Robust Client-Side Validation (`js/app.js`)
- **Real-Time Feedback**: Validates fields on `blur` and `input` events.
- **Pattern Matching**:
  - Full Name: 2–80 characters, alphabetical only.
  - Email: RFC-compliant email pattern.
  - Phone: 10–15 digits with international prefix formatting support.
  - Age: Whole number between 16 and 99.
  - Department: Mandatory selection from verified academic list.
  - Message: Character counter with 1000-character ceiling.
- **Submission Guard**: Blocks invalid submissions (`event.preventDefault()`), focuses first error, and renders a floating error banner.
- **Loading State**: Displays an animated spinner on the submit button when valid.

### 2. Defense-in-Depth Server Validation (`backend/service.py`)
- Client-side validation can be bypassed (e.g., via `curl` or disabled JavaScript).
- The Python backend repeats every validation rule on the server side.
- If invalid data reaches the server, `submit.py` generates a structured HTML error page listing all rejection reasons.
- All input strings are sanitized with `html.escape()` to mitigate Cross-Site Scripting (XSS).

### 3. Database Persistence (`backend/database.py`)
- SQLite database stored at `database/app.db`.
- Parameterized SQL queries (`?` placeholders) prevent SQL Injection attacks.
- Indexed timestamp column (`submitted_at DESC`) ensures optimal retrieval order.
- Context managers ensure database connections are closed and rollbacks occur on errors.

### 4. Interactive CGI Data Viewer (`cgi-bin/view_data.py`)
- Renders an HTML page of all database records.
- Includes dynamic metrics:
  - Total registered students.
  - Number of distinct academic departments.
  - Timestamp of latest submission.
- Supports keyword search across name, email, and phone.
- Supports department filtering.
- Supports record deletion with confirmation alert.

---

## 🎓 College Viva / Oral Examination Q&A

### Q1: What is CGI (Common Gateway Interface)?
> **Answer**: CGI is a standard protocol that defines how a web server communicates with external console programs (like Python scripts) to generate dynamic web pages. The web server forwards client request parameters to the script using environment variables and standard input (STDIN), and the script returns the HTTP headers and HTML payload via standard output (STDOUT).

### Q2: How does a CGI script receive data in GET vs. POST requests?
> **Answer**:
> - **GET**: Parameters are encoded in the URL query string and passed to the CGI script via the `QUERY_STRING` environment variable (e.g., `os.environ.get("QUERY_STRING")`).
> - **POST**: Parameters are passed in the HTTP request body. The web server sets `CONTENT_LENGTH` in the environment, and the script reads the data from standard input (`sys.stdin.read(int(os.environ['CONTENT_LENGTH']))`).

### Q3: Why must a CGI script print `Content-Type: text/html\r\n\r\n` before the HTML?
> **Answer**: In HTTP protocol, headers communicate metadata (such as MIME type, encoding, and status) to the browser. The HTTP specification mandates that headers must be separated from the message body by a blank line (CRLF CRLF, or `\r\n\r\n`). If omitted, the browser would misinterpret HTML tags as invalid HTTP headers, causing an HTTP 500 Internal Server Error.

### Q4: Why do we have both client-side (JavaScript) and server-side (Python) validation?
> **Answer**:
> - **Client-side validation** improves user experience by providing immediate feedback without requiring a network round-trip.
> - **Server-side validation** is essential for security ("defense in depth") because client-side checks can be bypassed by modifying JavaScript or crafting raw HTTP requests.

### Q5: How does this project prevent SQL Injection?
> **Answer**: By using parameterized queries (`cursor.execute("INSERT ... VALUES (?, ?, ...)", (val1, val2, ...))`). SQLite treats parameters as literal values rather than executable SQL code, preventing attackers from injecting arbitrary SQL commands.
