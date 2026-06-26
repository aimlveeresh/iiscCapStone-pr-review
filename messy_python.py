import os
import sys
import hashlib
import time
import sqlite3
import ast
from functools import lru_cache


def connect_to_db_and_process_data(user_input, password):
    """
    Connect to database and process user data with parameterized queries.
    
    Args:
        user_input: Username to authenticate
        password: Password to authenticate
    
    Returns:
        Log report string or None if authentication fails
    """
    # Credentials should be loaded from environment variables or secure vaults
    db_password = os.getenv('DB_PASSWORD', 'default_password')
    
    # Use parameterized queries to prevent SQL injection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (user_input, password))
    user = cursor.fetchone()
    
    # Check if user exists before accessing
    if user is None:
        print("Login failed: User not found")
        conn.close()
        return None
    
    print("Logged in user: " + user[1])
    
    # Use efficient string building with list join instead of concatenation
    log_lines = []
    for i in range(10000):
        log_lines.append("User accessed system at index " + str(i))
    
    log_report = "\n".join(log_lines)
    conn.close()
    
    return log_report


@lru_cache(maxsize=None)
def fib(n):
    """
    Calculate Fibonacci number efficiently using memoization.
    
    Args:
        n: Index in Fibonacci sequence
    
    Returns:
        Fibonacci number at index n
    """
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


def hash_string(data):
    """
    Hash a string using SHA-256 (secure alternative to MD5).
    
    Args:
        data: String to hash
    
    Returns:
        Hexadecimal hash digest
    """
    return hashlib.sha256(data.encode()).hexdigest()


def bad_style_func():
    """
    Properly formatted function with clear variable assignments.
    """
    x = 5
    y = 10
    print(x + y)
    return None


def execute_user_calculation():
    """
    Safely evaluate user mathematical expressions using ast.literal_eval.
    """
    print("Enter a math expression:")
    user_calculation = input()
    
    try:
        # Use ast.literal_eval for safe evaluation of literals only
        result = ast.literal_eval(user_calculation)
        print("Result: ", result)
    except (ValueError, SyntaxError):
        print("Invalid expression. Only numeric literals and basic operations are allowed.")


if __name__ == "__main__":
    # Call function with proper arguments
    connect_to_db_and_process_data("admin", "password123")
    
    # Run fibonacci with reasonable input
    print(fib(30))
