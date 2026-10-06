"""
Backend Service Layer
Contains business logic, data validation, sanitization, and CRUD operations.
"""

import re
import html
from typing import Dict, List, Tuple, Optional, Any
from backend.database import get_db_connection, init_db

VALID_DEPARTMENTS = [
    "Computer Science & Engineering",
    "Data Science & Analytics",
    "Artificial Intelligence & Machine Learning",
    "Information Technology",
    "Electronics & Communication Engineering",
    "Mechanical Engineering"
]

def sanitize_input(value: Optional[str]) -> str:
    """Strip whitespace and escape HTML special characters to prevent XSS."""
    if value is None:
        return ""
    # Strip whitespace
    stripped = value.strip()
    # Normalize excessive internal spaces
    return html.escape(stripped)

def validate_registration_data(data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Validates submitted form fields according to business rules.
    Returns: (is_valid: bool, errors: List[str], cleaned_data: Dict[str, Any])
    """
    errors: List[str] = []
    cleaned: Dict[str, Any] = {}

    # 1. Full Name
    raw_name = data.get("full_name", "")
    name = str(raw_name).strip()
    if not name:
        errors.append("Full Name is required.")
    elif len(name) < 2 or len(name) > 80:
        errors.append("Full Name must be between 2 and 80 characters.")
    elif not re.match(r"^[A-Za-z\s.'-]+$", name):
        errors.append("Full Name should only contain letters, spaces, dots, hyphens, and apostrophes.")
    cleaned["full_name"] = name

    # 2. Email Address
    raw_email = data.get("email", "")
    email = str(raw_email).strip().lower()
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email:
        errors.append("Email address is required.")
    elif not re.match(email_pattern, email):
        errors.append("Please provide a valid email address (e.g., student@university.edu).")
    cleaned["email"] = email

    # 3. Phone Number
    raw_phone = data.get("phone", "")
    phone = str(raw_phone).strip()
    digits_only = re.sub(r"[^\d]", "", phone)
    if not phone:
        errors.append("Phone number is required.")
    elif len(digits_only) < 10 or len(digits_only) > 15:
        errors.append("Phone number must contain between 10 and 15 digits.")
    cleaned["phone"] = phone

    # 4. Age
    raw_age = data.get("age", "")
    try:
        age = int(str(raw_age).strip())
        if age < 16 or age > 99:
            errors.append("Age must be a valid number between 16 and 99.")
        cleaned["age"] = age
    except (ValueError, TypeError):
        errors.append("Age must be a valid whole number (between 16 and 99).")
        cleaned["age"] = 0

    # 5. Course / Department
    raw_dept = data.get("department", "")
    dept = str(raw_dept).strip()
    if not dept:
        errors.append("Course / Department selection is required.")
    elif dept not in VALID_DEPARTMENTS:
        errors.append(f"Invalid department selected. Must be one of the recognized departments.")
    cleaned["department"] = dept

    # 6. Message / Purpose (optional)
    raw_message = data.get("message", "")
    message = str(raw_message).strip()
    if len(message) > 1000:
        errors.append("Message cannot exceed 1000 characters.")
    cleaned["message"] = message

    # Metadata fields (passed from CGI environment)
    cleaned["ip_address"] = str(data.get("ip_address", "127.0.0.1")).strip()
    cleaned["user_agent"] = str(data.get("user_agent", "Unknown"))[:250].strip()

    is_valid = len(errors) == 0
    return is_valid, errors, cleaned

def create_registration(data: Dict[str, Any]) -> Tuple[bool, Optional[int], List[str]]:
    """
    Validates and stores a new student registration record in SQLite.
    Returns: (success: bool, record_id: Optional[int], errors: List[str])
    """
    # Ensure database table exists
    init_db()

    is_valid, errors, cleaned = validate_registration_data(data)
    if not is_valid:
        return False, None, errors

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO student_registrations (
                    full_name, email, phone, age, department, message, ip_address, user_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleaned["full_name"],
                cleaned["email"],
                cleaned["phone"],
                cleaned["age"],
                cleaned["department"],
                cleaned["message"],
                cleaned["ip_address"],
                cleaned["user_agent"]
            ))
            conn.commit()
            record_id = cursor.lastrowid
            return True, record_id, []
    except Exception as exc:
        return False, None, [f"Database error while saving registration: {str(exc)}"]

def get_all_registrations(search_query: Optional[str] = None, department_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves student registrations with optional filtering.
    Returns list of dictionary records.
    """
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        sql = "SELECT * FROM student_registrations"
        params: List[Any] = []
        conditions: List[str] = []

        if search_query:
            conditions.append("(full_name LIKE ? OR email LIKE ? OR phone LIKE ?)")
            pattern = f"%{search_query.strip()}%"
            params.extend([pattern, pattern, pattern])

        if department_filter and department_filter in VALID_DEPARTMENTS:
            conditions.append("department = ?")
            params.append(department_filter)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY submitted_at DESC, id DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

def get_registration_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single registration by its primary key ID."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_registrations WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_registration_stats() -> Dict[str, Any]:
    """Computes summary statistics for dashboard viewing."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM student_registrations")
        total = cursor.fetchone()["total"]
        
        cursor.execute("""
            SELECT department, COUNT(*) as count 
            FROM student_registrations 
            GROUP BY department 
            ORDER BY count DESC
        """)
        dept_counts = {row["department"]: row["count"] for row in cursor.fetchall()}
        
        cursor.execute("SELECT MAX(submitted_at) as latest FROM student_registrations")
        latest = cursor.fetchone()["latest"]
        
        return {
            "total_registrations": total,
            "department_counts": dept_counts,
            "latest_submission": latest or "None"
        }

def delete_registration(record_id: int) -> bool:
    """Deletes a registration record by ID."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_registrations WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount > 0
