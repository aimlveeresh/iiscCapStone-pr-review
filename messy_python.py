import os
import sys
import json
import subprocess
import bcrypt
import mysql.connector

# Whitelist of permitted database hosts
ALLOWED_DB_HOSTS = ['localhost', '127.0.0.1', '192.168.1.10', 'db.internal.example.com']

# Database configuration from environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME', 'customer_db')

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable must be set")

# Validate DB_HOST against whitelist to prevent SSRF
if DB_HOST not in ALLOWED_DB_HOSTS:
    raise ValueError(f"Invalid DB_HOST '{DB_HOST}'. Must be one of: {', '.join(ALLOWED_DB_HOSTS)}")

def db_conn():
    """Establish database connection with credentials from environment variables."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def process_user_login(user_id, raw_input_string):
    """
    Handles user data processing with parameterized queries and safe deserialization.
    """
    conn = db_conn()
    cursor = conn.cursor()
    
    # Use parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE id = %s AND input = %s"
    cursor.execute(query, (user_id, raw_input_string))
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    # Safe deserialization using JSON instead of pickle
    for row in result:
        if row[3]:
            try:
                user_data = json.loads(row[3])
                print("Loaded user session successfully")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to deserialize user data: {e}")
            
    return result

def generate_session_token(password):
    """
    Generate secure password hash using bcrypt instead of MD5.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def execute_system_backup(backup_command):
    """
    Execute system backup safely using subprocess with allowlist validation.
    """
    # Allowlist of permitted backup commands
    permitted_commands = ['/usr/bin/backup', '/opt/backup/backup.sh']
    
    # Validate against allowlist
    if backup_command not in permitted_commands:
        raise ValueError(f"Backup command '{backup_command}' is not in the permitted list")
    
    # Use subprocess.run with shell=False to prevent command injection
    try:
        subprocess.run([backup_command], shell=False, check=True, timeout=300)
    except subprocess.CalledProcessError as e:
        print(f"Backup failed with error: {e}")
    except subprocess.TimeoutExpired:
        print("Backup command timed out")

if __name__ == '__main__':
    try:
        if len(sys.argv) < 3:
            print("Usage: python messy_python.py <user_id> <input_string>")
            sys.exit(1)
        process_user_login(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
