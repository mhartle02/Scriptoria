from flask import *
import sqlite3, requests
from werkzeug.security import generate_password_hash, check_password_hash
from classes.book import *

app = Flask(__name__)
app.secret_key = 'Secret Key'
#We should open a connection right before we use it and close right after
#I feel like if we do it enclosing like this then we'll close the db, and it won't get reopened for a new page
#conn = sqlite3.connect('Scriptoria.db')
#cursor = conn.cursor()

app.secret_key = "keys" #needed to change the password

def fetch_books(query, max_results=5):
    #Arbitrary max_results number, for testing
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    response = requests.get(url)
    data = response.json()

    books = []
    for item in data.get('items', []):
        volume_info = item.get('volumeInfo', {})

        book = Book(
        #The fields commented out below can be deleted, but could also be used as additional info for books
            #book_id=volume_info.get('id', 'Unknown ID'),
            title=volume_info.get('title', 'Unknown Title'),
            authors=volume_info.get('authors', ['Unknown Author']),
            description=volume_info.get('description', 'No Description'),
            page_count=volume_info.get('pageCount', 0),
            cover_image=volume_info.get('imageLinks', {}).get('thumbnail', ''),
            average_rating=volume_info.get('averageRating', 0.0)  #Default 'extracted' rating to 0.0

        )
        books.append(book)
    #Inserting fetched books into book database
    insert_books_into_db(books)
    return books

def insert_books_into_db(books):
    #Insert books into db while screening for dupes
    conn = sqlite3.connect('Scriptoria.db')
    cursor = conn.cursor()

    #testing if following code is necessary
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS booksTable (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            page_count INTEGER,
            cover_image TEXT            
        )
    ''')
    """

    for book in books:
        #CHeck that book isn't already in database
        cursor.execute("SELECT book_id FROM Books WHERE title = ? AND author = ?", (book.title, book.authors))
        existing_book = cursor.fetchone()

        if existing_book is None:
            cursor.execute('''
                INSERT INTO Books (title, author, description, page_count, cover_image, average_rating)
                VALUES (?, ?, ?, ?, ?, ?)    
            ''', (book.title, book.authors, book.description, book.page_count, book.cover_image, book.average_rating))

            #Debugging
            print(f"Added book to database: {book.title}")
            #Debugging pt2
            print(f"Rating: {book.average_rating}")

    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def home():
    query = request.args.get("q","")    #Get search query from search-bar form
    books = fetch_books(query) if query else []     #Only search for books if a query does exist
    return render_template('home.html', books=books, query=query)

@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            conn = sqlite3.connect('Scriptoria.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, username, password, permission
                FROM userLogins
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            conn.close()

            #Debugging
            print(f"Query Result: {user}")

            if user:
                session['username'] = user[1]
                session['permission'] = user[3]
                session['name'] = user[0]
                """
                #If we redirect based on the permission level of the user, we can handle it here
                if session['permission'] == "reader":
                    return redirect(...)
                if session['permission'] == "admin":
                    return redirect(...)
                if session['permission'] == "author":
                    return redirect(...)
                """

                #This is temporary until we decide how to utilize user permissions
                return render_template('home.html')

            else:
                flash("Invalid username or password", 'danger')
        except Exception as e:
            #Logging Error for debugging
            print(f"Error During login: {e}")
            flash("An Error Occurred. Please Try Again.", 'danger')
            return render_template('login.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', msg=None, errors=[], show_form=True)
    #If adding fields to the database and the signup then add them below
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        permission = request.form.get('permission')

    #Add error checking to be flashed on website if new fields are needed
        errors=[]
        if not name:
            errors.append("You must input a name")
        if not username:
            errors.append("You must input a username")
        if not password:
            errors.append("You must input a password")

        if errors:
            return render_template('signup.html', msg="Errors:", errors=errors, show_form=False)

        else:
            hashed_password = generate_password_hash(password)
            conn = sqlite3.connect('Scriptoria.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO userLogins (name, username, password, permission)
                VALUES (?, ?, ?, ?)
            ''', (name, username, hashed_password, permission))
            conn.commit()
            conn.close()
            flash("User created!", "success")
            return redirect(url_for('home'))
            # temporary, will change depending on the role/permission one have

    return render_template('signup.html', msg="User successfully created!", errors=[], show_form=False)

@app.route('/reset', methods = ['GET', 'POST'])
def reset():
    if request.method == 'GET':
        return render_template('reset.html')
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('password1')
        password_confirm = request.form.get('password2')
        try:
            conn = sqlite3.connect('Scriptoria.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username
                FROM userLogins
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            if user:
                 if new_password != password_confirm:
                    flash("You enter the wrong password. Try again", "error")
                    return redirect(url_for('reset'))
                 else:
                    hashed_password = generate_password_hash(new_password)
                    cursor.execute("UPDATE userLogins SET password = ? WHERE username = ?",
                                   (hashed_password, username))
                    conn.commit()
                    conn.close()
                    flash("Password changed!", "success")
                    return redirect(url_for('login')) #if succeeded, this should redirect us to login page (or some other page)
            if not user:
                flash("User not found. Try again", "danger")
                return redirect(url_for('reset'))
        except Exception as e:
            print(f"Error: {e}")
            flash("An Error Occurred. Please Try Again.", 'danger')
            return render_template('reset.html', show_form=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
