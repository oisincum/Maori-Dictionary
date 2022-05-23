from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from datetime import datetime

app = Flask(__name__)

DATABASE = "dictionary.db"

app.secret_key = "secret+key"


def create_connection(db_file):
    """
    create a connection with the database
    parameter: name of database file
    returns: a connection to the file
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


def get_categories():
    con = create_connection(DATABASE)

    query = "SELECT id, name FROM category"

    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    return category_list


def get_user_data(user_id):

    con = create_connection(DATABASE)

    query = "SELECT * FROM user WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (user_id, ))
    fetched_data = cur.fetchall()

    con.close()

    return fetched_data


def yes_logged_in():
    if session.get('email'):
        print("Logged in")
        return True
    else:
        print("Not logged in")
        return False


@app.route('/')
def render_homepage():
    return render_template('home.html', categories=get_categories(), user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in())


@app.route('/category/<cat_id>')
def render_category_page(cat_id):
    con = create_connection(DATABASE)

    query = "SELECT * FROM category WHERE id=?"

    cur = con.cursor()
    cur.execute(query, (cat_id,))
    cur_category = cur.fetchall()

    query = "SELECT * FROM word_list WHERE categoryID=?"

    cur = con.cursor()
    cur.execute(query, (cat_id,))
    words_list = cur.fetchall()
    con.close()

    return render_template('category.html', categories=get_categories(), words_found=words_list,
                           user_data=get_user_data(session.get('user_id')), logged_in=yes_logged_in(),
                            cat_data=cur_category)


@app.route('/word/<word_id>')
def render_word_page(word_id):
    con = create_connection(DATABASE)

    query = "SELECT * FROM word_list WHERE id=?"

    cur = con.cursor()
    cur.execute(query, (word_id,))
    words_list = cur.fetchall()
    con.close()

    return render_template('word.html', categories=get_categories(), words_found=words_list,
                           user_data=get_user_data(session.get('user_id')), logged_in=yes_logged_in())


@app.route('/login', methods=['GET', 'POST'])
def render_login_page():
    if yes_logged_in():
        return redirect('/?error=Already+logged+in')

    if request.method == "POST":
        print(request.form)
        email = request.form.get('email').strip()
        password = str(request.form.get('password')).strip()

        con = create_connection(DATABASE)

        query = "SELECT * FROM user WHERE email=?"
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()

        con.close()

        if user_data is None:
            return redirect('/login?error=Email+or+password+is+incorrect')
        else:
            user_id = user_data[0][0]
            fname = user_data[0][1]
            lname = user_data[0][2]
            email = user_data[0][3]
            db_password = user_data[0][4]
            teacher = user_data[0][5]

        if db_password != password:
            return redirect('/login?error=Email+or+password+is+incorrect')

        session['user_id'] = user_id
        session['fname'] = fname
        session['lname'] = lname
        session['email'] = email
        session['teacher'] = teacher
        return redirect('/')

    return render_template('login.html', categories=get_categories(), user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in())


@app.route('/logout')
def render_logout_page():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))

    return redirect('/?message=Goodbye')


@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if yes_logged_in():
        return redirect('/?error=Already+logged+in')

    if request.method == "POST":
        print(request.form)
        fname = request.form.get('fname').strip()
        lname = request.form.get('lname').strip()
        email = request.form.get('email').strip()
        password = str(request.form.get('password')).strip()
        password2 = str(request.form.get('password2')).strip()
        yes_teacher = request.form.get('teacher')

        teacher = False
        if yes_teacher:
            teacher = True

        if password != password2:
            print("something went wrong")
            return redirect('/signup?error=Passwords+do+not+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+length+is+below+8+characters')

        con = create_connection(DATABASE)

        query = "SELECT id FROM user WHERE email=?"
        cur = con.cursor()
        cur.execute(query, (email,))
        email_list = cur.fetchall()

        if len(email_list) > 0:
            return redirect('/signup?error=Email+is+already+in+use')

        final_password = password

        query = "INSERT INTO user(id, fname, lname, email, password, teacher) VALUES(NULL,?,?,?,?,?)"

        cur = con.cursor()
        cur.execute(query, (fname, lname, email, final_password, teacher))
        con.commit()

        con.close()

        return redirect('/login')

    return render_template('signup.html', categories=get_categories(), user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in())

@app.route('/add_word', methods=['GET', 'POST'])
def render_add_word_page():
    return render_template('add_word.html', categories=get_categories(), user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in())

app.run(host='0.0.0.0', debug=True)
