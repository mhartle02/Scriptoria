from flask import *
import sqlite3
from initializeDb import initializeDatabase

app = Flask(__name__)

@app.route('/')
def home():  # put application's code here
    #try:
        #test = cursor.execute("select USERNAME from users WHERE password = 'password'").fetchone()
        #print(test)
        #return test[0]
    #except:
        #return 'Database connection failed'
    return render_template('home.html')     #Honestly idk if 'home.html' here is correct, but this should be the landing page

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        #Get username and password from login.html
        username = request.form['username']
        password = request.form['password']

        #Validate user
        conn = sqlite3.connect('Scriptoria.db')
        cursor = conn.cursor()
        user = cursor.execute(
            "Select name from Users where username = ? and password = ?",
            (username, password)
        ).fetchall()

        if user:
            print("user found")
        else:
            print("user not found")

        conn.close()

    return render_template('login.html')



if __name__ == '__main__':
    initializeDatabase()
    app.run(debug=True)
