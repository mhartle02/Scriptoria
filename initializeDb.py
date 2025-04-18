
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
            permission TEXT NOT NULL,
            pronouns TEXT,
            bio TEXT,
            profile_picture TEXT DEFAULT 'default.jpg'
        )
    ''')

    #Temporary, for debugging
    exampleUsers = [
        {"name": "John", "username": "reader", "password": "1000", "permission": "Reader", "pronouns": "he/him", "bio": "Example Bio", "profile_picture" : "example_profile_picture_link"},
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
    cursor.execute("DROP TABLE IF EXISTS Reviews")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            review_text TEXT NOT NULL,
            rating INTEGER CHECK(rating BETWEEN 1 and 5),
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES userLogins(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE
        )
    ''')
            #UNIQUE(user_id, book_id),
    #Add above line ^ to the table if we want to eventually prevent dupe reviews
    #Right now, for testing, I'm leaving this out -Bryce

    cursor.execute("DROP TABLE IF EXISTS Books")
    print("Books Database Cleared")
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_book_id TEXT UNIQUE,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            page_count INTEGER,
            cover_image TEXT,
            average_rating REAL DEFAULT 0            
            )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_book_rating
        AFTER INSERT ON Reviews
        FOR EACH ROW
        BEGIN
            UPDATE Books
            SET average_rating = (
                SELECT ROUND(AVG(rating), 2)
                FROM Reviews
                WHERE book_id = NEW.book_id
            )
            WHERE book_id = NEW.book_id;
        END;
    ''')

    #Making user's private list in MyBooks
    cursor.execute("DROP TABLE IF EXISTS myBooks")
    print("MyBooks Database Cleared")
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS myBooks (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            page_count INTEGER,
            cover_image TEXT,
            average_rating REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES userLogins(id) ON DELETE CASCADE      
            )
    ''')

    #Later: Allow users to update reviews and delete reviews and create triggers to table like above ^



    conn.close()


if __name__ == "__main__":
    initializeDb()
