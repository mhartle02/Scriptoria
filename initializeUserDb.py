import sqlite3

def initializeUserDatabase():
    conn = sqlite3.connect('userLoginDatabase.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS userLogins")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS userLogins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        permission TEXT NOT NULL
        )
    ''')

    #Temporary, for debugging
    exampleUsers = [
        {"name": "John", "username": "Reader", "password": "Password", "permission": "reader"},
        {"name": "John", "username": "Admin", "password": "Password", "permission": "admin"},
        {"name": "John", "username": "Author", "password": "Password", "permission": "author"}
    ]

    for user in exampleUsers:
        cursor.execute('''
                INSERT INTO userLogins (name, username, password, permission)
                VALUES (?, ?, ?, ?)
            ''', (user["name"], user["username"], user["password"], user["permission"]))
    conn.commit()

    cursor.execute("SELECT name, username, password, permission FROM userLogins")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Name: {row[0]}, Username: {row[1]}, Password: {row[2]}, Permission: {row[3]}")
    conn.close()


if __name__ == "__main__":
    initializeUserDatabase()