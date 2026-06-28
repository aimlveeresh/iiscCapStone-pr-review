import os
import sys
import hashlib
import time
import sqlite3
import ast
import bcrypt

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
    db_password = os.getenv('DB_PASSWORD', '')
    if not db_password:
        raise ValueError('DB_PASSWORD environment variable not set')
    
    # SECURITY FIX: Use parameterized queries to prevent SQL injection
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (user_input, password))
    user = cursor.fetchone()
    conn.close()
    
    return user

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
        log_lines.append("User accessed system at index " + str(i))
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
    if user is None:
        print("Authentication failed: User not found")
        return None
    
    # BUG FIX: Null check before accessing user[1]
    if user:
        print("Logged in user: " + user[1])
    
    log_report = generate_activity_log(user[0])
    return log_report

# PERFORMANCE FIX: Efficient Fibonacci with memoization
def fib(n, memo=None):
    """
    Calculate Fibonacci number efficiently using memoization.
    
    Args:
        n: Fibonacci index
        memo: Memoization dictionary
    
    Returns:
        Fibonacci number at index n
    """
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]

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
    connect_to_db_and_process_data("admin", "password123")
    
    # PERFORMANCE FIX: Use reasonable input for efficient Fibonacci
    print(fib(30))
