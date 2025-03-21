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
    #conn.close()

    #Making reviews database
    cursor.execute("DROP TABLE IF EXISTS userReviews")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS userReviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        review_text TEXT NOT NULL,
        rating INTEGER CHECK(rating BETWEEN 1 and 5),
        FOREIGN KEY (user_id) REFERENCES userLogins(id) ON DELETE CASCADE,
        FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE
        )
    ''')

    cursor.execute("DROP TABLE IF EXISTS Books")
    print("Books Database Cleared")
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            page_count INTEGER,
            cover_image TEXT            
            )
        ''')


    conn.close()


if __name__ == "__main__":
    initializeDb()