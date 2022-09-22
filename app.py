# All Imports
from flask import Flask, render_template, request
from flask import session, redirect, url_for, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import requests
from jsonpath_ng import jsonpath, parse
import urllib.request
import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import telegram_send
from admin import adminpn
from user import userpn
UPLOAD_FOLDER = 'static/Photo/'
# Flask APP start
app = Flask(__name__)
app.secret_key = "cairocoders-ednalan"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.register_blueprint(userpn)
app.register_blueprint(adminpn)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# DB Configuration
HOST = "localhost"
NAME = "lib_last"
USER = "superadmin"
PASS = "JeffLiloza"

# DB Connection
conn = psycopg2.connect(dbname=NAME, user=USER, password=PASS, host=HOST)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    

@app.route('/', methods=['POST', 'GET'])
def main():
    if 'loggedin' in session: 
       if session['role'] == 'Admin':
           return redirect(url_for('adminpn.admin_panel'))
       elif session['role'] == 'Librarian':
           return redirect(url_for('librarian'))    
       else:
           return redirect(url_for('userpn.dashboard'))
    return redirect(url_for('login'))

 


@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                session['role']=account['role']
                session['card_id']=account['card_id']
                # Redirect to home page
                return redirect(url_for('main'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
 
    return render_template('accounting/login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session: 
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # Create variables for easy access
            fullname = request.form['fullname']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            _hashed_password = generate_password_hash(password)
    
            #Check if account exists using MySQL
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()
            print(account)
            # If account exists show error and validation checks
            if account:
                flash('Account already exists!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash('Username must contain only characters and numbers!')
            elif not username or not password or not email:
                flash('Please fill out the form!')
            else:
                # Account doesnt exists and the form data is valid, now insert new account into users table
                cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
                conn.commit()
                flash('You have successfully registered!')
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            flash('Please fill out the form!')
        # Show registration form with message (if any)
        return render_template('accounting/register.html')
    else:
        return redirect(url_for('login'))    
   
   
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
            
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('/accounting/profile.html', account=account)
    # User is not loggedin redirect to login page
    else:
        return redirect(url_for('login'))


@app.route('/add_teachers', methods=['POST' , 'GET'])
def add_teachers():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'file' not in request.files:
                flash('No file part')
                return redirect(url_for('adminpn.teachers'))
    else:
                file = request.files['file']
    if file.filename == '':
                flash('No image selected for uploading')
                return redirect(url_for('adminpn.teachers'))
    if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photost= f'Photo/{filename}'
                name = request.form['name']
                position = request.form['position']
                card_id = request.form['card_id']
                cur.execute(f"INSERT INTO teachers(name, position, card_id, photo) VALUES ('{name}','{position}','{card_id}','{photost}'  )");
                conn.commit()
                flash('Student Added successfully')
                return redirect(url_for('adminpn.teachers'))
    else:
                flash('Allowed image types are - png, jpg, jpeg, gif')
                return redirect(url_for('adminpn.teachers'))

#Start all      
if __name__ == "__main__":

    app.run(debug=True,host="0.0.0.0",port=50)
