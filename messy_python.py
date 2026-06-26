import os
import sys
import hashlib
import time
import sqlite3

# STYLING ISSUE: Bad spacing, no docstring, terrible variable names
def Connect_To_DB_And_processData(user_input,password):
    # SECURITY ISSUE: Hardcoded sensitive credentials
    DB_PASSWORD = "SuperSecretPassword123!" 
    
    # STYLING ISSUE: Inline comments should have a space after '#'
    #SECURITY ISSUE: SQL Injection vulnerability (string formatting instead of parameterized queries)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + user_input + "' AND password = '" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    # BUG: Trying to use a variable that might be None if no user is found, causing an AttributeError later
    print("Logged in user: " + user[1]) 
    
    # PERFORMANCE ISSUE: Highly inefficient string concatenation in a loop (creates new string objects every time)
    # PERFORMANCE ISSUE: Doing a database fetch inside a heavy loop
    log_report = ""
    for i in range(10000):
        log_report += "User accessed system at index " + str(i) + "\n"
        
    return log_report

# PERFORMANCE ISSUE: Inefficient Fibonacci implementation (O(2^n) exponential time complexity due to redundant recursion)
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# SECURITY ISSUE: Using an insecure/deprecated cryptographic hash algorithm (MD5)
def hash_string(data):
    return hashlib.md5(data.encode()).hexdigest()

# STYLING ISSUE: Multiple statements on one line, completely unreadable
def bad_style_func(): x = 5; y = 10; print(x+y); return None

# BUG & SECURITY ISSUE: Using `eval()` on raw user input (Remote Code Execution risk)
def execute_user_calculation():
    print("Enter a math expression:")
    user_calculation = input() # If user enters "__import__('os').system('rm -rf /')", it executes!
    result = eval(user_calculation)
    print("Result: ", result)

if __name__ == "__main__":
    # BUG: Passing a single string instead of a tuple/list to a function that might expect parsed args
    # BUG: Calling the function with missing arguments (password is missing)
    # This will crash immediately with a TypeError
    Connect_To_DB_And_processData("admin") 
    
    # PERFORMANCE ISSUE: Running the horribly slow fibonacci function with a relatively high number
    print(fib(40))
