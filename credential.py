import sqlite3
import os
import bcrypt

def test_credential(username, password):
    password_bcode = password.encode("utf-8")
    with sqlite3.connect(os.getenv("DATABASE")) as con:
        cur = con.cursor()
        cur.execute("SELECT username, password FROM users WHERE username = ?;", (username,))
        username_password = cur.fetchone()
    
    if username_password and bcrypt.checkpw(password_bcode, username_password[1]):
        print("login ok")
        return True
    else:
        return False
        
    
    