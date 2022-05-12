from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from datetime import datetime
app = Flask(__name__)

#DATABASE ="C:/Users/18130/OneDrive - Wellington College"
DATABASE = "dictionary.db"

def create_connection(db_file):
    """
    create a connection with the database
    parameter: name of database file
    returns: a connection to the file
    """
    try:
        connection =sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


def get_categories():
    con = create_connection(DATABASE)

    query ="SELECT id, name FROM category"

    cur =con.cursor()
    cur.execute(query)
    category_list =cur.fetchall()
    con.close()
    return category_list



@app.route('/')
def render_homepage():
    return render_template('home.html', categories=get_categories())


@app.route('/category/<cat_id>')
def render_category_page(cat_id):
    con = create_connection(DATABASE)

    query = "SELECT * FROM word_list WHERE categoryID=?"

    cur = con.cursor()
    cur.execute(query, (cat_id, ))
    words_list = cur.fetchall()
    con.close()

    return render_template('category.html', categories=get_categories(), words_found=words_list)

@app.route('/login')
def render_login_page():
    return render_template('login.html', categories=get_categories())

@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    print(request.form)
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')



    return render_template('signup.html', categories=get_categories())

app.run(host='0.0.0.0', debug=True)