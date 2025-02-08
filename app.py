from flask import Flask
import pypyodbc as db

DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'MasonsLaptop'
DATABASE_NAME = 'Scriptoria'


connection = (f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
    uid=mgh21l
    pwd=password
""")


app = Flask(__name__)
conn = db.connect(connection)
#conn = db.connect('exampleDatabaseFile.db')
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




if __name__ == '__main__':
    app.run()
