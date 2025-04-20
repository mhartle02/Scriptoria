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
            google_book_id=item.get('id', 'Unknown ID'),
            title=volume_info.get('title', 'Unknown Title'),
            authors=volume_info.get('authors', ['Unknown Author']),
            #authors=', '.join(volume_info.get('authors', ['Unknown Author'])),   #Commented out bc doesn't work but might be needed later (with tweaking)
            description=volume_info.get('description', 'No Description'),
            page_count=volume_info.get('pageCount', 0),
            cover_image=volume_info.get('imageLinks', {}).get('thumbnail', ''),
            average_rating=0
        )
        books.append(book)
    #Inserting fetched books into book database
    insert_books_into_db(books)
    return books


def insert_books_into_db(books):
    #Insert books into db while screening for dupes
    conn = sqlite3.connect('Scriptoria.db')
    cursor = conn.cursor()

    for book in books:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO Books 
                (google_book_id, title, author, description, page_count, cover_image, average_rating)
                VALUES (?, ?, ?, ?, ?, ?, COALESCE(?,0))
            ''', (
                book.google_book_id,
                book.title,
                book.authors,
                book.description,
                book.page_count,
                book.cover_image,
                book.average_rating
            ))

            if cursor.rowcount>0:
                print(f"Added book to database: {book.title}")
            else:
                print(f"Skipped duplicate book: {book.title}")

        except sqlite3.Error as e:
            print(f"Skipping duplicate book: {book.title}")

    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        user_id = session['user_id']
        name = session['name']
        permission  = session['permission']
    except KeyError:
        name = ""
        user_id = ""
        permission = ""
    print(user_id)

    conn = sqlite3.connect('Scriptoria.db')
    cursor = conn.cursor()

    #Handling POST for Readers
    if request.method == 'POST' and permission == "Reader":
        try:
            title = request.form.get('title')
            author = request.form.get('author')
            description = request.form.get('description')
            page_count = request.form.get('page_count')
            cover_image = request.form.get('cover_image')
            average_rating = request.form.get('average_rating')
        except Exception as e:
            return redirect(url_for('login'))

        print(f"Adding book: {title} by {author}")

        cursor.execute("SELECT book_id FROM myBooks WHERE title = ? AND author = ?", (title, author))
        existing_book = cursor.fetchone()

        if existing_book is None:
            cursor.execute('''
                INSERT INTO myBooks (user_id, title, author, description, page_count, cover_image, average_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, title, author, description, page_count, cover_image, average_rating))
            conn.commit()
            flash("Book added to your reading list!", "success")
        else:
            flash("Book already in your list.", "warning")
        #conn.close()
        return redirect(url_for('home'))

    #Handling POST for Admins
    elif request.method == 'POST' and permission == "Admin":
        try:
            title = request.form.get('title')
            author = request.form.get('author')
            google_book_id = request.form.get('google_book_id')
        except Exception as e:
                return redirect(url_for('login'))

        '''
        print(f"Deleting book: {title} by {author}")
        cursor.execute('DELETE FROM Books WHERE google_book_id = ?', (google_book_id,))
        conn.commit()
        flash("Book successfully deleted!", "success")
        '''


    query = request.args.get("q", "")
    books = []
    if query:
        #Now searching local database before querying GoogleBooksAPI
        cursor.execute('''
            SELECT * FROM Books
            WHERE title LIKE ? OR author LIKE ?
        ''', (f"%{query}%", f"%{query}%"))
        book_rows = cursor.fetchall()

        if book_rows:
            for row in book_rows:
                books.append({
                    'book_id' : row[0],
                    'google_book_id' : row[1],
                    'title' : row[2],
                    'authors' : row[3],
                    'description' : row[4],
                    'page_count' : row[5],
                    'cover_image' : row[6],
                    'average_rating' : round(row[7], 2) if row[7] is not None else 0.0
                })
        else:
            #If not found in local DB, query GoogleBooksAPI
            books = fetch_books(query)

    conn.close()
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
                SELECT id, name, username, password, permission
                FROM userLogins
                WHERE username = ? AND password = ?
            """, (username,password,))
            user = cursor.fetchone()
            conn.close()

            #Debugging
            print(f"Query Result: {user}")

            if user:
                session["user_id"] = user[0]
                session['username'] = user[2]
                session['permission'] = user[4]
                session['name'] = user[1]

                print("Session Data: ", session)
                #If we redirect based on the permission level of the user, we can handle it here
                if session['permission'] == "Reader":
                    return redirect(url_for('home'))
                elif session['permission'] == "Author":
                    return redirect(url_for('author'))
                elif session['permission'] == "Admin":
                    return redirect(url_for('home'))
                return render_template('home')

            else:
                flash("Invalid username or password", 'danger')
                return render_template('login.html')
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
            cursor.execute('''SELECT id FROM userLogins WHERE username = ?''', (username,))
            new_user = cursor.fetchone()
            user_id = new_user[0]
            cursor.execute('''SELECT permission FROM userLogins WHERE username = ?''', (username,))
            newest_user = cursor.fetchone()
            permission = newest_user[0]
            cursor.execute('''SELECT username FROM userLogins WHERE username = ?''', (username,))
            newest_user2 = cursor.fetchone()
            username = newest_user2[0]

            conn.close()
            if permission == "Reader":
                flash("User created!", "success")
                return redirect(url_for('home'))
            elif permission == "Author":
                flash("User created!", "success")
                return redirect(url_for('home'))
            elif permission == "Admin":
                flash("User created!", "success")
                return redirect(url_for('home'))
            return redirect(url_for('home'))

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

@app.route('/my_books', methods=['GET','POST'])
def my_books():
    if "user_id" not in session:
        flash("You must be logged in to view your books.", "error")
        return redirect(url_for("login"))

    user_id = session['user_id']
    print(user_id)
    conn = sqlite3.connect('Scriptoria.db')
    cursor = conn.cursor()

    if request.method == "POST":
        book_id = request.form.get("book_id")
        if book_id:
            #Deleting this book from user's list
            cursor.execute(
                '''DELETE FROM myBooks WHERE book_id = ? AND user_id = ?''', (book_id, user_id)
            )
            conn.commit()
            flash("Book removed from your list!", "success")
        else:
            flash("Invalid book ID.", "error")

    cursor.execute(
        '''SELECT book_id, title, author, description, page_count, cover_image, average_rating FROM myBooks where user_id = ?''',(user_id,)
    )
    books = cursor.fetchall()
    conn.close()

    book_list = []
    for book in books:
        book_list.append({
            "book_id": book[0],
            "title": book[1],
            "author": book[2],
            "description": book[3],
            "page_count": book[4],
            "cover_image": book[5],
            "average_rating": book[6]
        })

        print(f"Book title: {book[1]}")
    return render_template('my_books.html', books = book_list)

@app.route('/my_reviews', methods=['GET', 'POST'])
def my_reviews():
    if "user_id" not in session:
        flash("You must be logged in to view your reviews.", "error")
        return redirect(url_for("login"))

    user_id = session['user_id']
    conn = sqlite3.connect('Scriptoria.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Reviews.review_text, Reviews.rating, Reviews.date_created,
               Books.title, Books.author, Books.cover_image
        FROM Reviews
        JOIN Books ON Reviews.book_id = Books.book_id
        WHERE Reviews.user_id = ?
        ORDER BY Reviews.date_created DESC
    ''', (user_id,))

    reviews = cursor.fetchall()
    conn.close()
    return render_template('my_reviews.html', reviews=reviews)





"""@app.route('/delete_books', methods=['GET','POST'])
 def delete_books():
         user_id = session['user_id']
         conn = sqlite3.connect('Scriptoria.db')
         cursor = conn.cursor()
         cursor.execute(
             '''SELECT book_id, title, author, description, page_count, cover_image, average_rating FROM myBooks where user_id = ?''',
             (user_id,))
         books = cursor.fetchall()
         for i in range(len(books)):
             book_id = books[i][0]
         cursor.execute('''DELETE FROM myBooks where user_id = ? AND book_id = ?''', (user_id, book_id,))
         conn.commit()
         cursor.execute('''SELECT book_id, title, author, description, page_count, cover_image, average_rating
                           FROM myBooks WHERE user_id = ?''', (user_id,))
         books = cursor.fetchall()
         conn.close()

         book_list = []
         for book in books:
             book_list.append({
                 "book_id": book[0],
                 "title": book[1],
                 "author": book[2],
                 "description": book[3],
                 "page_count": book[4],
                 "cover_image": book[5],
                 "average_rating": book[6]
             })
         return render_template('my_books.html', books = book_list)"""

@app.route('/profile', methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in to view your profile.", "error")
        print("User must log in <--- Debugging")
        return redirect(url_for("login"))

    #This is different from all other session variable instances, I'm unsure if this will cause issues
    user_id = int(session["user_id"])
    #Debugging Print(s)
    print(f"Current session user ID: {session['user_id']}")
    conn = sqlite3.connect("Scriptoria.db")
    cursor = conn.cursor()

    if request.method == "POST":
        pronouns = request.form.get("pronouns")
        bio = request.form.get("bio")

        cursor.execute('''
            UPDATE userLogins
            SET pronouns = ?, bio = ?
            WHERE id = ?
        ''', (pronouns, bio, user_id))
        conn.commit()
        flash("Profile updated successfully!", "success")

    cursor.execute("SELECT username, name, pronouns, bio FROM userLogins where id = ?", (user_id,))
    user = cursor.fetchone()

    #Fetching friends for display on profile page
    cursor.execute('''
        SELECT u.name, u.username
        FROM userFriends f
        JOIN userLogins u ON f.friend_id = u.id
        WHERE f.user_id = ?
    ''', (user_id,))
    friends = cursor.fetchall()

    #Debugging print(s) again
    print(f"Fetched friends: {friends}")
    print("Current session user ID:", user_id)
    cursor.execute("SELECT * FROM userFriends")
    print("All userFriends rows:", cursor.fetchall())

    conn.close()

    return render_template("profile.html", user=user, friends=friends)


@app.route("/review", methods=["GET", "POST"])
def review():
    if "user_id" not in session:
        flash("You must be logged in to submit a review.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        user_id = session['user_id']
        google_book_id = request.form.get("book_id")  #Changed to google_book_id
        review_text = request.form.get("review")
        rating = request.form.get("rating")

        if not google_book_id or not review_text or not rating:
            print("Error: Missing form data!")
            flash("Error: Missing required fields.", "error")
            return redirect(url_for("review"))

        try:
            rating = int(rating)  #Ensure rating is a valid integer
        except ValueError:
            print("Error: Invalid rating input!")
            flash("Error: Invalid rating value.", "error")
            return redirect(url_for("review"))

        conn = sqlite3.connect("Scriptoria.db")
        cursor = conn.cursor()

        #Find book_id from google_book_id
        cursor.execute("SELECT book_id FROM Books WHERE google_book_id = ?", (google_book_id,))
        book_entry = cursor.fetchone()

        if book_entry:
            book_id = book_entry[0]
            print(f"Book found in database: book_id={book_id}")
        else:
            print(f"Error: Book not found in database for google_book_id={google_book_id}")
            flash("Error: Book not found in database.", "error")
            conn.close()
            return redirect(url_for("review"))

        #Insert review
        try:
            cursor.execute('''
                INSERT INTO Reviews (user_id, book_id, review_text, rating)
                VALUES (?, ?, ?, ?)
            ''', (user_id, book_id, review_text, rating))
            print(f"Review successfully inserted: user_id={user_id}, book_id={book_id}, rating={rating}")

        except sqlite3.IntegrityError as e:
            print(f"SQLite Integrity Error: {e}")
            flash("Error submitting review. Please try again.", "error")
            conn.close()
            return redirect(url_for("review"))

        print(f"Average rating updated for book_id={book_id}")

        conn.commit()
        conn.close()

        flash("Review submitted successfully!", "success")
        return redirect(url_for("review"))

    query = request.args.get("q", "")
    books = fetch_books(query)  #Fetching books from database
    return render_template("review.html", books=books, query=query)




if __name__ == '__main__':
    app.run(debug = True)