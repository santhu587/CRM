import os
import re
import sys
from typing import Tuple

import mysql.connector
from dotenv import load_dotenv


def load_env() -> None:
    base_dir = os.path.dirname(__file__)
    env_path = os.path.join(base_dir, '.env')
    load_dotenv(env_path)


def is_password_strong(password: str) -> Tuple[bool, str]:
    if len(password) < 12:
        return False, 'Password must be at least 12 characters long.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit.'
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, 'Password must contain at least one special character.'
    return True, 'Strong password.'


def connect_mysql():
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')

    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connection_timeout=5,
        )
        return conn
    except mysql.connector.Error as e:
        raise SystemExit(f"MySQL connection failed: {e}")


def print_validate_password_settings(cursor) -> None:
    cursor.execute("SHOW VARIABLES LIKE 'validate_password%';")
    rows = cursor.fetchall()
    if not rows:
        print('validate_password plugin not enabled (no variables found).')
        return
    print('MySQL validate_password settings:')
    for name, value in rows:
        print(f"  {name} = {value}")


def main():
    load_env()

    # Validate the current DB password from env
    db_password = os.getenv('DB_PASSWORD', '')
    ok, msg = is_password_strong(db_password)
    print(f"Env DB_PASSWORD strength: {'OK' if ok else 'FAIL'} - {msg}")

    # Try connecting to MySQL with env credentials
    conn = connect_mysql()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
            print('MySQL connectivity: OK')
            print_validate_password_settings(cur)
    finally:
        conn.close()

    # Optional: validate a password passed as an argument
    if len(sys.argv) > 1:
        test_pw = sys.argv[1]
        ok2, msg2 = is_password_strong(test_pw)
        print(f"Input password strength: {'OK' if ok2 else 'FAIL'} - {msg2}")


if __name__ == '__main__':
    main()



