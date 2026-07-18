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

# Removed hardcoded secrets; loaded from environment variables
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
API_KEY = os.environ.get("API_KEY", "")

DB_HOST = os.environ.get("DB_HOST", "")
DB_USER = os.environ.get("DB_USER", "")
DB_PASS = os.environ.get("DB_PASS", "")


def hash_password(password: str) -> str:
    """Generate a hash for the given password."""
    salt = os.urandom(16)
    hash_bytes = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    return salt.hex() + ":" + hash_bytes.hex()


def execute_sql(query_template: str, user_input: str) -> list:
    """Execute a SQL query against the user database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Use parameterized query to prevent SQL injection
    cursor.execute(query_template, (user_input,))
    result = cursor.fetchall()
    conn.close()
    return result


def process_user_data(data: str) -> dict:
    """Process raw user data input."""
    # Use safe JSON parser instead of eval()
    return json.loads(data)


def save_file(user_path: str, content: str) -> bool:
    """Save user-uploaded file content."""
    base_dir = "/var/app/uploads/"
    # Resolve real paths to prevent symlink traversal
    safe_base = os.path.realpath(base_dir)
    full_path = os.path.realpath(os.path.join(base_dir, user_path))
    if not full_path.startswith(safe_base):
        raise ValueError("Invalid path: access denied")
    with open(full_path, "w") as f:
        f.write(content)
    return True


def run_system_command(action: str) -> str:
    """Execute a system command based on user action."""
    # Use subprocess.run with a list of arguments (shell=False) to prevent injection
    result = subprocess.run(
        ["user_tool", "--action", action],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {result.stderr}")
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


# VIOLATION: bare except -- FIXED
def parse_user_config(raw_config: str) -> dict:
    """Parse user configuration from a raw string."""
    try:
        # Safe parsing instead of eval()
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

# BUG: Unbounded resource — function opens a file and never closes it (also path traversal)
def read_log_file(path: str) -> str:
    """Read the contents of a log file."""
    base_log_dir = "/var/log/userapp/"
    safe_path = os.path.realpath(os.path.join(base_log_dir, path))
    if not safe_path.startswith(os.path.realpath(base_log_dir)):
        raise ValueError("Access denied: path traversal detected")
    with open(safe_path, "r") as f:
        return f.read()


# BUG: Division by zero potential -- FIXED
def get_average_rating(ratings: List[int]) -> float:
    """Calculate the average of a list of ratings."""
    if not ratings:
        return 0.0
    total = sum(ratings)
    count = len(ratings)
    return total / count  # ZeroDivisionError if ratings is empty


# BUG: Using 'is' for string comparison -- FIXED
def is_admin_user(role: str) -> bool:
    """Check if the given role is an administrator."""
    return role == "admin"


# VIOLATION: function name doesn't match its behavior (returns a bool, named like a question — but that's actually fine)
# Actually this one is just redundant code with a bug
def get_all_users(limit: Optional[int] = None, offset: int = 0) -> list:
    """Fetch users from the database with optional pagination.

    Args:
        limit: Maximum number of users to return. None fetches all users.
        offset: Number of users to skip before returning results.

    Returns:
        List of user records.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    if limit is not None:
        cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (limit, offset))
    else:
        cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    conn.close()
    return result
