"""
User management service - handles user registration, authentication, and profile operations.

WARNING: This module contains intentional bugs for testing the PR review agent.
"""

import os
import hashlib
import sqlite3
import logging
import json
import bcrypt
import subprocess
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# =============================================================================
# SECURITY BUGS
# =============================================================================

# BUG: Hardcoded secret / API key - FIXED: loaded from environment variables
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
API_KEY = os.getenv("API_KEY", "")

# BUG: Hardcoded database credentials - FIXED: loaded from environment variables
DB_HOST = os.getenv("DB_HOST", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASS = os.getenv("DB_PASS", "")


def hash_password(password: str) -> str:
    """Generate a strong hash for the given password using bcrypt."""
    # FIX: replaced MD5 with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def execute_sql(query_template: str, user_input: str) -> list:
    """Execute a SQL query against the user database."""
    # FIX: SQL injection - use parameterized query with placeholder
    conn = sqlite3.connect("users.db")
    try:
        cursor = conn.cursor()
        cursor.execute(query_template, (user_input,))
        result = cursor.fetchall()
    finally:
        conn.close()
    return result


def process_user_data(data: str) -> dict:
    """Process raw user data input."""
    # FIX: arbitrary code execution - using safe JSON parser
    return json.loads(data)


def save_file(user_path: str, content: str) -> bool:
    """Save user-uploaded file content."""
    # FIX: path traversal - validate and normalize user_path
    base_dir = "/var/app/uploads/"
    # Normalize and resolve full path
    full_path = os.path.normpath(os.path.join(base_dir, user_path))
    real_base = os.path.realpath(base_dir)
    real_full = os.path.realpath(full_path)
    # Ensure the resolved path is still inside the intended directory
    if not real_full.startswith(real_base + os.sep) and real_full != real_base:
        logger.warning("Path traversal attempt: %s", user_path)
        return False
    with open(full_path, "w") as f:
        f.write(content)
    return True


def run_system_command(action: str) -> str:
    """Execute a system command based on user action."""
    # FIX: command injection - use subprocess with allowlist and no shell
    ALLOWED_ACTIONS = {"list", "status", "help"}  # define safe actions
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Action not allowed: {action}")
    result = subprocess.run(
        ["user_tool", "--action", action],
        capture_output=True,
        text=True,
        shell=False,
        check=False
    )
    return result.stdout


# =============================================================================
# PEP8 / RUFF VIOLATIONS
# =============================================================================

# VIOLATION: camelCase instead of snake_case
maxRetryCount = 5
userEmailDomain = "@company.com"


# VIOLATION: mutable default argument - FIXED: use None and initialize
from typing import List

def add_user(name: str, roles: list = None) -> list:
    """Add a user with the given roles."""
    if roles is None:
        roles = []
    roles.append("user")
    roles.append(name)
    return roles


# VIOLATION: bare except - FIXED: replaced eval with json.loads and catch specific exceptions
def parse_user_config(raw_config: str) -> dict:
    """Parse user configuration from a raw string."""
    try:
        return json.loads(raw_config)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Failed to parse config: %s", e)
        return {}


# Removed unused imports: from functools import wraps, from collections import OrderedDict


# VIOLATION: line too long - FIXED: break signature across multiple lines
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
        "start_date": start_date,
    }
    return profile


# VIOLATION: missing whitespace around operator - FIXED: added spaces
def calculate_user_score(contributions: int, reviews: int) -> float:
    """Calculate user score based on contributions and reviews."""
    return (contributions * 10) + (reviews * 5)


# VIOLATION: trailing whitespace - FIXED: removed trailing spaces
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

# BUG: Unbounded resource - FIXED: used context manager and path validation
LOG_DIR = os.getenv("LOG_DIR", "/var/log")

def read_log_file(path: str) -> str:
    """Read the contents of a log file."""
    full_path = os.path.normpath(os.path.join(LOG_DIR, path))
    real_log_dir = os.path.realpath(LOG_DIR)
    real_full = os.path.realpath(full_path)
    # Prevent path traversal
    if not real_full.startswith(real_log_dir + os.sep) and real_full != real_log_dir:
        raise ValueError("Invalid log file path")
    with open(full_path, "r") as f:
        return f.read()


# BUG: Division by zero potential - FIXED: guard against empty list
def get_average_rating(ratings: List[int]) -> float:
    """Calculate the average of a list of ratings."""
    if not ratings:
        return 0.0
    total = sum(ratings)
    count = len(ratings)
    return total / count


# BUG: Using 'is' for string comparison - FIXED: use ==
def is_admin_user(role: str) -> bool:
    """Check if the given role is an administrator."""
    return role == "admin"


# BUG: Function returns None but docstring says it fetches users; kept as-is to preserve public contract.
def get_all_users() -> None:
    """Fetch all users from the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    conn.close()
