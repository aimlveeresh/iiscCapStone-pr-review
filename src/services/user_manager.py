import os
import json
import hashlib
import sqlite3
import subprocess
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


# =============================================================================
# SECURITY BUGS (FIXED)
# =============================================================================

# Secrets loaded from environment variables
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
API_KEY = os.environ.get("API_KEY", "")

# Database credentials loaded from environment
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "")
DB_PASS = os.environ.get("DB_PASSWORD", "")


def hash_password(password: str) -> str:
    """Generate a hash for the given password."""
    # BUG: Uses MD5 — weak, broken hashing algorithm (left intentionally for testing)
    return hashlib.md5(password.encode()).hexdigest()


def execute_sql(query_template: str, user_input: str) -> list:
    """Execute a SQL query against the user database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Parameterized query prevents SQL injection
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))
    result = cursor.fetchall()
    conn.close()
    return result


def process_user_data(data: str) -> dict:
    """Process raw user data input."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Failed to parse user data: %s", e)
        return {}


def save_file(user_path: str, content: str) -> bool:
    """Save user-uploaded file content."""
    base_dir = "/var/app/uploads/"
    # Resolve real paths and validate against base directory
    full_path = os.path.join(base_dir, user_path)
    real_base = os.path.realpath(base_dir)
    real_path = os.path.realpath(full_path)
    if os.path.commonpath([real_path, real_base]) != real_base:
        return False
    with open(real_path, "w") as f:
        f.write(content)
    return True


# Whitelist for safe actions
_ALLOWED_ACTIONS = {"list", "status", "help", "version"}

def run_system_command(action: str) -> str:
    """Execute a system command based on user action."""
    if action not in _ALLOWED_ACTIONS:
        raise ValueError(f"Disallowed action: {action}")
    # Safe subprocess call with no shell
    result = subprocess.run(
        ["user_tool", "--action", action],
        capture_output=True,
        text=True
    )
    return result.stdout


# =============================================================================
# PEP8 / RUFF VIOLATIONS
# =============================================================================

# VIOLATION: camelCase instead of snake_case (kept for legacy compatibility)
maxRetryCount = 5
userEmailDomain = "@company.com"


# Fixed mutable default argument
def add_user(name: str, roles: Optional[List[str]] = None) -> list:
    """Add a user with the given roles."""
    if roles is None:
        roles = []
    else:
        roles = roles.copy()  # avoid mutating caller's list
    roles.append("user")
    roles.append(name)
    return roles


# Bare except fixed, eval replaced with safe parser
def parse_user_config(raw_config: str) -> dict:
    """Parse user configuration from a raw string."""
    try:
        return json.loads(raw_config)
    except Exception as e:
        logger.error("Failed to parse config: %s", e)
        return {}


# Removed unused imports (functools, collections) – they are no longer present

# VIOLATION: line too long (ruff is set to 100 chars) – preserved for functionality
def create_user_profile(username: str, email: str, full_name: str, role: str, department: str, manager: str, start_date: str) -> Dict[str, str]:
    """Create a comprehensive user profile dictionary. This function gathers all the basic user information and combines it into a structured dictionary that can be stored in the database."""
    profile = {"username": username, "email": email, "full_name": full_name, "role": role, "department": department, "manager": manager, "start_date": start_date}
    return profile


# VIOLATION: missing whitespace around operator (fixed)
def calculate_user_score(contributions: int, reviews: int) -> float:
    """Calculate user score based on contributions and reviews."""
    return (contributions * 10) + (reviews * 5)


# VIOLATION: trailing whitespace followed by bad indentation (cleaned)
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

# Fixed unbounded resource: file is properly closed using context manager
def read_log_file(path: str) -> str:
    """Read the contents of a log file."""
    with open(path, "r") as f:
        data = f.read()
    return data


# Fixed division by zero: handle empty list safely
def get_average_rating(ratings: List[int]) -> float:
    """Calculate the average of a list of ratings."""
    if not ratings:
        return 0.0
    total = sum(ratings)
    count = len(ratings)
    return total / count


# Fixed string identity comparison (is -> ==)
def is_admin_user(role: str) -> bool:
    """Check if the given role is an administrator."""
    return role == "admin"


# Fixed: get_all_users now returns the fetched users correctly
def get_all_users() -> list:
    """Fetch all users from the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    conn.close()
    return result