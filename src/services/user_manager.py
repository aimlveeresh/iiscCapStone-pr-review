"""
User management service - handles user registration, authentication, and profile operations.

WARNING: This module contains intentional bugs for testing the PR review agent.
"""

import os
import hashlib
import sqlite3
import logging
import ast
import subprocess
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# =============================================================================
# SECURITY BUGS - FIXED
# =============================================================================

# Load sensitive credentials from environment variables instead of hardcoding.
DEFAULT_ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
API_KEY = os.environ["API_KEY"]

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]


def hash_password(password: str) -> str:
    """Generate a strong, salted hash for the given password using scrypt."""
    salt = os.urandom(16)
    key = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=64)
    return salt.hex() + ":" + key.hex()


def execute_sql(query_template: str, user_input: str) -> list:
    """Execute a parameterized SQL query against the user database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Parameterized query prevents SQL injection.
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))
    result = cursor.fetchall()
    conn.close()
    return result


def process_user_data(data: str) -> dict:
    """Process raw user data input safely using ast.literal_eval."""
    return ast.literal_eval(data)


def save_file(user_path: str, content: str) -> bool:
    """Save user-uploaded file content, preventing path traversal."""
    base_dir = os.path.abspath("/var/app/uploads/")
    # Normalize and resolve the full path, then ensure it stays inside base_dir.
    full_path = os.path.abspath(os.path.join(base_dir, user_path))
    if not full_path.startswith(base_dir + os.sep):
        raise ValueError("Path traversal detected")
    with open(full_path, "w") as f:
        f.write(content)
    return True


def run_system_command(action: str) -> str:
    """Execute a system command safely using subprocess."""
    # subprocess.run with a list avoids shell injection.
    result = subprocess.run(
        ["user_tool", "--action", action],
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout


# =============================================================================
# PEP8 / RUFF VIOLATIONS - FIXED
# =============================================================================

max_retry_count = 5
user_email_domain = "@company.com"


def add_user(name: str, roles: list = None) -> list:
    """Add a user with the given roles. Avoids mutable default argument."""
    if roles is None:
        roles = []
    roles.append("user")
    roles.append(name)
    return roles


def parse_user_config(raw_config: str) -> dict:
    """Parse user configuration from a raw string safely."""
    try:
        return ast.literal_eval(raw_config)
    except (ValueError, SyntaxError):
        logger.error("Failed to parse config")
        return {}


# Removed unused imports (functools.wraps, collections.OrderedDict)


def create_user_profile(
    username: str,
    email: str,
    full_name: str,
    role: str,
    department: str,
    manager: str,
    start_date: str
) -> Dict[str, str]:
    """Create a comprehensive user profile dictionary."""
    profile = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "role": role,
        "department": department,
        "manager": manager,
        "start_date": start_date
    }
    return profile


def calculate_user_score(contributions: int, reviews: int) -> float:
    """Calculate user score based on contributions and reviews."""
    return (contributions * 10) + (reviews * 5)


def get_user_status(user_id: int) -> str:
    """Return the status of a user."""
    status_map = {
        1: "active",
        2: "inactive",
        3: "suspended",
    }
    return status_map.get(user_id, "unknown")


# =============================================================================
# CODE SMELLS / OTHER BUGS - FIXED
# =============================================================================


def read_log_file(path: str) -> str:
    """Read the contents of a log file using a context manager."""
    with open(path, "r") as f:
        return f.read()


def get_average_rating(ratings: List[int]) -> float:
    """Calculate the average of a list of ratings, avoiding division by zero."""
    if not ratings:
        return 0.0
    total = sum(ratings)
    count = len(ratings)
    return total / count


def is_admin_user(role: str) -> bool:
    """Check if the given role is an administrator (using ==, not is)."""
    return role == "admin"


def get_all_users() -> list:
    """Fetch all users from the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
