from flask import *
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('userLoginDatabase.db')
cursor = conn.cursor()



@app.route('/')
def hello_world():  # put application's code here
    #try:
        #test = cursor.execute("select USERNAME from users WHERE password = 'password'").fetchone()
        #print(test)
        #return test[0]
    #except:
        #return 'Database connection failed'
    return 'Hello World!'

@app.route('/login')
def login():
    return render_template('login.html')



if __name__ == '__main__':
    app.run()
