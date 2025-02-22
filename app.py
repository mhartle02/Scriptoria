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

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', msg=None, errors=[], show_form=True)
    #If adding fields to the database and the signup then add them below
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

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

    #add_to_db() or other such function here to insert new user into database
    return render_template('signup.html', msg="User successfully created!", errors=[], show_form=False)

@app.route('/reset', methods = ['GET', 'POST'])
def reset():
    if request.method == 'GET':
        return render_template('reset.html')
    if request.method == 'POST':
        new_password = request.form.get('password1')
        password_confirm = request.form.get('password2')
        if new_password != password_confirm:
            flash("You enter the wrong password. Try again")
    return render_template('reset.html', msg="Password successfully changed", errors=[], show_form=False)


if __name__ == '__main__':
    app.run()
