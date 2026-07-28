"""
User management service - handles user registration, authentication, and profile operations.

WARNING: This module contains intentional bugs for testing the PR review agent.
"""

import os
import hashlib
import sqlite3
import logging
import json
import subprocess
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# =============================================================================
# SECURITY BUGS
# =============================================================================

# Removed hardcoded secrets - load from environment variables
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
API_KEY = os.environ.get('API_KEY')

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')


def hash_password(password: str) -> str:
    """Generate a secure hash for the given password using PBKDF2."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ':' + dk.hex()


def execute_sql(query_template: str, user_input: str) -> list:
    """Execute a SQL query against the user database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Use parameterized query to prevent SQL injection
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))
    result = cursor.fetchall()
    conn.close()
    return result


def process_user_data(data: str) -> dict:
    """Process raw user data input (JSON format)."""
    return json.loads(data)


def save_file(user_path: str, content: str) -> bool:
    """Save user-uploaded file content safely."""
    base_dir = os.path.realpath("/var/app/uploads/")
    full_path = os.path.realpath(os.path.join(base_dir, user_path))
    if not full_path.startswith(base_dir + os.sep):
        raise ValueError("Invalid path: path traversal detected")
    with open(full_path, "w") as f:
        f.write(content)
    return True


def run_system_command(action: str) -> str:
    """Execute a system command safely using subprocess."""
    result = subprocess.run(
        ["user_tool", "--action", action],
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout


# =============================================================================
# PEP8 / RUFF VIOLATIONS
# =============================================================================

# VIOLATION: camelCase instead of snake_case
maxRetryCount = 5
userEmailDomain = "@company.com"


# VIOLATION: mutable default argument
def add_user(name: str, roles: list = []) -> list:
    """Add a user with the given roles."""
    roles.append("user")
    roles.append(name)
    return roles


# VIOLATION: bare except
def parse_user_config(raw_config: str) -> dict:
    """Parse user configuration from a raw JSON string."""
    try:
        return json.loads(raw_config)
    except json.JSONDecodeError:
        logger.error("Failed to parse config")
        return {}


# VIOLATION: unused imports (if we import at top) + star import pattern
from functools import wraps
from collections import OrderedDict  # noqa: F811 — unused import


# VIOLATION: line too long (ruff is set to 100 chars)
def create_user_profile(username: str, email: str, full_name: str, role: str, department: str, manager: str, start_date: str) -> Dict[str, str]:
    """Create a comprehensive user profile dictionary. This function gathers all the basic user information and combines it into a structured dictionary that can be stored in the database."""
    profile = {"username": username, "email": email, "full_name": full_name, "role": role, "department": department, "manager": manager, "start_date": start_date}
    return profile


# VIOLATION: missing whitespace around operator
def calculate_user_score(contributions:int, reviews:int)->float:
    """Calculate user score based on contributions and reviews."""
    return (contributions*10)+(reviews*5)


# VIOLATION: trailing whitespace followed by bad indentation
def get_user_status(user_id: int) -> str:
    """Return the status of a user."""
    status_map = {
        1: "active",
        2: "inactive",
        3: "suspended",
    }

    return status_map.get(user_id, "unknown")


# =============================================================================
# CODE SMELLS / OTHER BUGS
# =============================================================================

# BUG: Unbounded resource — function opens a file and never closes it
def read_log_file(path: str) -> str:
    """Read the contents of a log file."""
    f = open(path, "r")
    data = f.read()
    return data


# BUG: Division by zero potential
def get_average_rating(ratings: List[int]) -> float:
    """Calculate the average of a list of ratings."""
    if not ratings:
        return 0.0
    total = sum(ratings)
    count = len(ratings)
    return total / count


# BUG: Using 'is' for string comparison
def is_admin_user(role: str) -> bool:
    """Check if the given role is an administrator."""
    return role == "admin"


# VIOLATION: function name doesn't match its behavior (returns a bool, named like a question — but that's actually fine)
# Actually this one is just redundant code with a bug
def get_all_users() -> list:
    """Fetch all users from the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
