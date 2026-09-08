import sqlite3
import os
from dotenv import load_dotenv
import bcrypt



def main():
    while True:
        username=input("Ingresa el usuario: ")
        password = input(f"Ingresa la contraseña de {username}: ")
        confirm = input(f"¿Estos datos son correctos? {username} / {password} 's/n': ")
        if confirm.lower() == "s":
            break
    
    password_bcode = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bcode, bcrypt.gensalt())
    load_dotenv()

    DATABASE = os.getenv("DATABASE")
    
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL )
    """)
    
    cur.execute("""
       INSERT INTO users (username, password) VALUES (?, ?)
            """, (username, hashed))
    
    con.commit()
    
    
    
    
    
if __name__ == "__main__":
    
    main()

