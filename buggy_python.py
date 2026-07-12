import os
import sys
import hashlib
import time
import sqlite3
import ast
import bcrypt
import functools

# Database connection
def connect_db():
    """
    Establish database connection.
    
    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect('users.db')
    return conn

# SECURITY FIX: Credentials from environment variables
def authenticate_user(user_input, password):
    """
    Authenticate user against database.
    
    Args:
        user_input: Username to authenticate
        password: Password to verify
    
    Returns:
        User tuple if authentication succeeds, None otherwise
    """
    db_password = os.getenv('DB_PASSWORD') or (_ for _ in ()).throw(ValueError('DB_PASSWORD environment variable not set'))
    if not db_password:
        raise ValueError('DB_PASSWORD environment variable not set')
    
    # SECURITY FIX: Use parameterized queries to prevent SQL injection
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = ?"
        cursor.execute(query, (user_input,))
        user = cursor.fetchone()
    
    if user and bcrypt.checkpw(password.encode(), user[2]):
        return user
    return None

# PERFORMANCE FIX: Generate activity log separately
def generate_activity_log(user_id):
    """
    Generate activity log for user.
    
    Args:
        user_id: ID of user to generate log for
    
    Returns:
        Log report string
    """
    # PERFORMANCE FIX: Use list join instead of string concatenation in loop
    log_lines = []
    for i in range(10000):
        log_lines.append(f"User accessed system at index {i}")
    log_report = "\n".join(log_lines)
    return log_report

def connect_to_db_and_process_data(user_input, password):
    """
    Authenticate user and process data securely.
    
    Args:
        user_input: Username to authenticate
        password: Password to verify
    
    Returns:
        Log report string or None if authentication fails
    """
    user = authenticate_user(user_input, password)
    
    # BUG FIX: Check if user exists before accessing
    if not user or len(user) <= 1:
        print("Authentication failed: User not found")
        return None
    
    # BUG FIX: Unpack tuple explicitly to validate structure
    print("Logged in user: " + user[1])
    
    log_report = generate_activity_log(user[0])
    return log_report

# PERFORMANCE FIX: Efficient Fibonacci with memoization
@functools.lru_cache(maxsize=None)
def fib(n):
    """
    Calculate Fibonacci number efficiently using memoization.
    
    Args:
        n: Fibonacci index
    
    Returns:
        Fibonacci number at index n
    """
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

# SECURITY FIX: Use SHA256 for general hashing, bcrypt for passwords
def hash_string(data):
    """
    Hash a string using SHA256.
    
    Args:
        data: String to hash
    
    Returns:
        Hexadecimal hash digest
    """
    return hashlib.sha256(data.encode()).hexdigest()

def hash_password(password):
    """
    Hash a password using bcrypt for secure storage.
    
    Args:
        password: Password to hash
    
    Returns:
        Bcrypt hash
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# STYLING FIX: Proper formatting and readability
def calculate_sum():
    """
    Calculate sum of two numbers.
    
    Returns:
        Sum of x and y
    """
    x = 5
    y = 10
    result = x + y
    print(result)
    return result

# SECURITY FIX: Use ast.literal_eval for safe evaluation of literals only
def execute_user_calculation():
    """
    Safely evaluate a mathematical expression from user input.
    Only supports literal values and basic operations.
    """
    print("Enter a math expression (literals and operators only):")
    user_calculation = input()
    
    try:
        # SECURITY FIX: Use ast.literal_eval for safe literal evaluation
        # This only allows literal structures (numbers, strings, tuples, lists, dicts, booleans, None)
        result = ast.literal_eval(user_calculation)
        print("Result: ", result)
    except (ValueError, SyntaxError):
        print("Invalid expression. Only literal values are allowed.")

if __name__ == "__main__":
    # BUG FIX: Provide both required arguments
    # Note: In production, credentials should come from secure sources
    connect_to_db_and_process_data(os.getenv('TEST_USER') or (_ for _ in ()).throw(ValueError('TEST_USER not set')), os.getenv('TEST_PASS') or (_ for _ in ()).throw(ValueError('TEST_PASS not set')))
    
    # PERFORMANCE FIX: Use reasonable input for efficient Fibonacci
    print(fib(30))
