from flask import *
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('userLoginDatabase.db')
cursor = conn.cursor()



@app.route('/')
def home():  # put application's code here
    #try:
        #test = cursor.execute("select USERNAME from users WHERE password = 'password'").fetchone()
        #print(test)
        #return test[0]
    #except:
        #return 'Database connection failed'
    return render_template('home.html')     #Honestly idk if 'home.html' here is correct, but this should be the landing page

@app.route('/login')
def login():
    return render_template('login.html')



if __name__ == '__main__':
    app.run()
