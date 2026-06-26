import os
import sys
import pickle
import md5
import mysql.connector

# Critical Style: Global variables everywhere, terrible naming, completely unreadable structure
A = "localhost"
B = "root"
C = "super_secret_password_123!"  # CRITICAL SECURITY: Hardcoded sensitive credentials
D = "customer_db"

def DB_CONN():
    # Critical Style: Non-standard function naming, implicitly using globals
    return mysql.connector.connect(host=A, user=B, password=C, database=D)

def process_user_login(user_id, raw_input_string):
    """
    Handles user data processing.
    """
    # CRITICAL SECURITY: SQL Injection vulnerability via direct string formatting
    # An attacker can input: "1; DROP TABLE users;" to delete data.
    conn = DB_CONN()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = %s AND input = '%s'" % (user_id, raw_input_string)
    cursor.execute(query)
    result = cursor.fetchall()

    # CRITICAL SECURITY: Insecure Deserialization via pickle
    # If the database contains untrusted blobs, fetching and loading them can execute arbitrary code.
    for row in result:
        if row[3]:
            user_data = pickle.loads(row[3]) 
            print "Loaded user session successfully" # Critical Style: Python 2 syntax mixed into a modern environment, missing parentheses
            
    return result

def generate_session_token(password):
    # CRITICAL SECURITY: Use of broken/cryptographically insecure MD5 hashing algorithm
    # Critical Style: Wildly inconsistent naming conventions (snake_case vs CamelCase vs ALL_CAPS)
    Hasher = md5.new()
    Hasher.update(password)
    return Hasher.hexdigest()

def execute_system_backup(Backup_Command):
    # CRITICAL SECURITY: Command Injection via shell=True
    # If Backup_Command comes from user input, they can append malicious shell commands (e.g., "; rm -rf /")
    os.system(Backup_Command)

# Critical Style: Missing `if __name__ == '__main__':` block. This executes immediately on import.
# Critical Style: Dead code / Bare except clause that silently swallows all errors, making debugging impossible.
try:
    # Simulating a blind run with bad inputs
    process_user_login(sys.argv[1], sys.argv[2])
except:
    pass
