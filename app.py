from flask import *
import sqlite3, requests
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'Secret Key'
#We should open a connection right before we use it and close right after
#I feel like if we do it enclosing like this then we'll close the db, and it won't get reopened for a new page
#conn = sqlite3.connect('Scriptoria.db')
#cursor = conn.cursor()

app.secret_key = "keys" #needed to change the password

class Book:
    def __init__(self, book_id, title, authors, description, page_count, cover_image, published_date, reviews, buy_link):
        self.book_id = book_id
        self.title = title
        self.authors = authors
        self.description = description
        self.page_count = page_count
        self.cover_image = cover_image
        self.published_date = published_date
        #self.reviews = reviews     #Need to return to
        self.buy_link = buy_link
    def __str__(self):
        return f"Title: {self.title}\nAuthors: {', '.join(self.authors)}\nPublished: {self.published_date}\nMore Info: {self.buy_link}\n"

def fetch_books(query, max_results=5):
    #Arbitrary max_results number, for testing
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    response = requests.get(url)
    data = response.json()

    books = []
    for item in data.get('items', []):
        volume_info = item.get('volumeInfo', {})
        book = Book(
            book_id=volume_info.get('id', 'Unknown ID'),
            title=volume_info.get('title', 'Unknown Title'),
            authors=volume_info.get('authors', ['Unknown Author']),
            description=volume_info.get('description', 'No Description'),
            page_count=volume_info.get('pageCount', 0),
            published_date=volume_info.get('publishedDate', 'Unknown Date'),
            cover_image=volume_info.get('imageLinks', {}).get('thumbnail', ''),
            buy_link=item.get('saleInfo', {}).get('buyLink', '')
        )
        books.append(book)
    return books

@app.route('/')
def home():  # put application's code here
    #try:
        #test = cursor.execute("select USERNAME from users WHERE password = 'password'").fetchone()
        #print(test)
        #return test[0]
    #except:
        #return 'Database connection failed'
    return render_template('home.html')     #Honestly idk if 'home.html' here is correct, but this should be the landing page

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
