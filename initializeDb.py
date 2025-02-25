import sqlite3

def initializeDb():
    conn = sqlite3.connect('Scriptoria.db')
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
        {"name": "John", "username": "reader", "password": "1000", "permission": "Reader"},
        {"name": "John", "username": "admin", "password": "1234", "permission": "Admin"},
        {"name": "John", "username": "author", "password": "2345", "permission": "Author"}
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
    initializeDb()