from crypt import methods
from datetime import datetime
from flask import Blueprint, render_template, session,abort, request, redirect, url_for, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import datetime

userpn = Blueprint('userpn',__name__)

HOST = "localhost"
NAME = "lib_last"
USER = "superadmin"
PASS = "JeffLiloza"

conn = psycopg2.connect(dbname=NAME, user=USER, password=PASS, host=HOST)


@userpn.route("/", methods=['POST', 'GET'])
def dashboard():
    if 'loggedin' in session:
        return render_template('user/dashboard.html')
    return redirect(url_for('login'))


@userpn.route("/books", methods=['POST','GET'])
def books():
    if 'loggedin' in session:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM lib"
        cur.execute(s) # Execute the SQL
        list_users = cur.fetchall()
        
        return render_template('user/books.html', list_users=list_users )
    return redirect(url_for('login'))


@userpn.route('/book/<string:id>', methods = ['POST', 'GET'])
def book(id):
    isbn = id[:-1]
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM lib WHERE isbn = '{isbn}'")
    data = cur.fetchall()
    return render_template('user/book.html', data = data )


@userpn.route('/book/add_order/<string:id>', methods= ['POST', 'GET'])
def add_order(id):
    if session['role'] == 'student':
      isbn = id
      cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  
      cur.execute(f"SELECT * FROM lib WHERE isbn = '{isbn}'")
      rows = cur.fetchall()
      for row in rows:
         isbn = str(row[7])
         bookPhoto = str(row[11])
         bookName = str(row[2])
         bookTitle = str(row[1])
      card_id=session['card_id']
      cur.execute(f"SELECT * FROM students WHERE card_id='{card_id}' ")
      
      studInfo = cur.fetchall()
      for row in studInfo:
          name = str(row[1])
          grade = str(row[2])
          photost = str(row[4])
      borrowed = datetime.datetime.now()
      card_id=session['card_id']

      cur.execute(f"INSERT INTO orders (isbn, quantity, borrowed, card_id , name ,grade , photost, bookPhoto, bookName,bookTitle) SELECT '{isbn}','1','{borrowed}', '{card_id}', '{name}' , '{grade}', '{photost}','{bookPhoto}', '{bookName}','{bookTitle}'");
      conn.commit()
      cur.execute(f"SELECT * FROM students WHERE card_id='{card_id}' ")
      return redirect(url_for('userpn.orders'))      
    elif session['role']== 'staff':
      isbn = id
      cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  
      cur.execute(f"SELECT * FROM lib WHERE isbn = '{isbn}'")
      rows = cur.fetchall()
      for row in rows:
         isbn = str(row[7])
         bookPhoto = str(row[11])
         bookName = str(row[2])
         bookTitle = str(row[1])
      card_id=session['card_id']
      cur.execute(f"SELECT * FROM teachers WHERE card_id='{card_id}' ")
      
      new = cur.fetchall()
      for row in new:
          name = str(row[1])
          grade = str(row[2])
          photost = str(row[4])
      borrowed = datetime.datetime.now()
      card_id=session['card_id']
      cur.execute(f"INSERT INTO orders_staff (isbn, quantity, borrowed, card_id , name ,position , photost,bookPhoto, bookName,bookTitle) SELECT '{isbn}','1','{borrowed}', '{card_id}', '{name}' , '{grade}', '{photost}','{bookPhoto}', '{bookName}','{bookTitle}'");
      conn.commit()
      return redirect(url_for('userpn.orders'))  
    
    return redirect(url_for('login'))   
        



@userpn.route("/orders", methods=['POST','GET'])
def orders():
    if 'loggedin' in session:
        if session['role']== 'student':
            card_id = session['card_id']
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
            cur.execute(f"SELECT * FROM orders WHERE card_id ='{card_id}'") # Execute the SQL
            list_users = cur.fetchall()
            return render_template('user/orders.html', list_users=list_users)
        elif session['role'] == 'staff':
            card_id = session['card_id']
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
            cur.execute(f"SELECT * FROM orders_staff WHERE card_id ='{card_id}'") # Execute the SQL
            list_users = cur.fetchall()
            return render_template('user/orders.html', list_users=list_users)
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))

@userpn.route('/order/<string:id>', methods = ['POST', 'GET'])
def order(id):
    if 'loggedin' in session:
        if session['role']== 'student':
            isbn = id[:-1]
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f"SELECT * FROM orders WHERE isbn = '{isbn}'")
            data = cur.fetchall()
            return render_template('user/order.html', data = data )
        elif session['role']== 'staff':
            isbn = id[:-1]
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f"SELECT * FROM orders_staff WHERE isbn = '{isbn}'")
            data = cur.fetchall()
            return render_template('user/order.html', data = data )
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))

@userpn.route("/help", methods=['POST','GET'])
def help():
    if 'loggedin' in session:
        return render_template('user/help.html')
    return redirect(url_for('login'))


@userpn.route("/rules", methods=['POST','GET'])
def rules():
    if 'loggedin' in session:
        return render_template('user/rules.html')
    return redirect(url_for('login'))