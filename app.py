from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from datetime import datetime

# imports everything extra needed

app = Flask(__name__)
DATABASE = "dictionary.db"
app.secret_key = "secret+key"


# all of the functions

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


# function that creates an connection to the database


def get_categories():
    con = create_connection(DATABASE)

    query = "SELECT id, name FROM category"

    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    return category_list


# function that will get the the id and name from the category database

def get_user_data(user_id):
    con = create_connection(DATABASE)

    query = "SELECT * FROM user WHERE id=?"

    cur = con.cursor()
    cur.execute(query, (user_id,))
    fetched_data = cur.fetchall()
    con.close()
    return fetched_data


# function that will get everything in the user database

def yes_logged_in():
    if session.get('email'):
        print("Logged in")
        return True
    else:
        print("Not logged in")
        return False


# function that will check if the person using the website is logged in or not

def is_teacher():
    if session.get('teacher') == 1:
        print("Is a teacher")
        return True
    else:
        print("is not a teacher")
        return False


# function that will check if the current person using the website is logged in on a teacher account or not

@app.route('/')
def render_homepage():
    return render_template('home.html', categories=get_categories(), user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in(), teacher=is_teacher())


# this takes a few of the functions above and checks if they are true
# it also uses the functions above to get the categories data and the user data
# e.g if they are logged in or not

@app.route('/category/<cat_id>')
def render_category_page(cat_id):
    con = create_connection(DATABASE)

    query = "SELECT * FROM category WHERE id=?"
    # selects all data from category database
    cur = con.cursor()
    cur.execute(query, (cat_id,))
    cur_category = cur.fetchall()

    query = "SELECT * FROM word_list WHERE categoryID=?"
    # selects all data from the word_list database
    cur = con.cursor()
    cur.execute(query, (cat_id,))
    words_list = cur.fetchall()
    con.close()

    return render_template('category.html', categories=get_categories(), words_found=words_list,
                           user_data=get_user_data(session.get('user_id')), logged_in=yes_logged_in(),
                           cat_data=cur_category, teacher=is_teacher())


@app.route('/word/<word_id>')
def render_word_page(word_id):
    con = create_connection(DATABASE)

    query = "SELECT * FROM word_list WHERE id=?"
    # selects all data from the word_list database
    cur = con.cursor()
    cur.execute(query, (word_id,))
    words_list = cur.fetchall()

    query = "SELECT * FROM user WHERE id=?"
    # selects all data from user database
    cur = con.cursor()
    cur.execute(query, (words_list[0][7],))
    # takes the editor_id from word_list as well as all user info
    found_user = cur.fetchall()

    con.close()

    return render_template('word.html', categories=get_categories(), words_found=words_list,
                           user_data=get_user_data(session.get('user_id')), word_user_data=found_user,
                           logged_in=yes_logged_in(), teacher=is_teacher())


@app.route('/login', methods=['GET', 'POST'])
def render_login_page():
    if yes_logged_in():
        return redirect('/?error=Already+logged+in')
    # checks to see if the user is already logged in before being able to access the login page

    if request.method == "POST":
        email = request.form.get('email').strip()
        password = str(request.form.get('password')).strip()
        # gets email and password that are entered in login
        con = create_connection(DATABASE)

        query = "SELECT * FROM user WHERE email=?"
        # gets all data from the line of the database which the email is the same as
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()

        con.close()

        if user_data is None:
            return redirect('/login?error=Email+or+password+is+incorrect')
        # checks if the email and password are entered
        else:
            user_id = user_data[0][0]
            fname = user_data[0][1]
            lname = user_data[0][2]
            email = user_data[0][3]
            db_password = user_data[0][4]
            teacher = user_data[0][5]

        if db_password != password:
            return redirect('/login?error=Email+or+password+is+incorrect')
        # checks if the password is correct if not gives you message above

        session['user_id'] = user_id
        session['fname'] = fname
        session['lname'] = lname
        session['email'] = email
        session['teacher'] = teacher
        return redirect('/')

    return render_template('login.html', categories=get_categories(), user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in(), teacher=is_teacher())


@app.route('/logout')
def render_logout_page():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))

    return redirect('/?message=Goodbye')
    # logout code that will stop session and redirect them to home page

@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if yes_logged_in():
        return redirect('/?error=Already+logged+in')
    # checks to see if the user is already logged in before being able to access the signup page

    if request.method == "POST":
        fname = request.form.get('fname').strip()
        lname = request.form.get('lname').strip()
        email = request.form.get('email').strip()
        password = str(request.form.get('password')).strip()
        password2 = str(request.form.get('password2')).strip()
        yes_teacher = request.form.get('teacher')

        teacher = False
        if yes_teacher:
            teacher = True
        # code for teacher value being true or false

        if password != password2:
            print("something went wrong")
            return redirect('/signup?error=Passwords+do+not+match')
        # code that checks if the password entered is equal to the password on the database

        if len(password) < 8:
            return redirect('/signup?error=Password+length+is+below+8+characters')
        # code that makes sure the password is more than 8 letters long

        con = create_connection(DATABASE)

        query = "SELECT id FROM user WHERE email=?"
        cur = con.cursor()
        cur.execute(query, (email,))
        email_list = cur.fetchall()

        if len(email_list) > 0:
            return redirect('/signup?error=Email+is+already+in+use')
        # checks if the email is in use or not

        final_password = password
        # makes the password that will be used for login equal to the first password entered on signup

        query = "INSERT INTO user(id, fname, lname, email, password, teacher) VALUES(NULL,?,?,?,?,?)"
        # inserts the data entered for an account into the user database
        cur = con.cursor()
        cur.execute(query, (fname, lname, email, final_password, teacher))
        con.commit()

        con.close()

        return redirect('/login')
        # after signing up the user will be brought to the login page

    return render_template('signup.html', categories=get_categories(), user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in(), teacher=is_teacher())


@app.route('/add_word', methods=['GET', 'POST'])
def render_add_word_page():
    if not yes_logged_in():
        return redirect('/?error=Not+logged+in')
    # checks to see if the user is already logged in before being able to access the add word page

    if not is_teacher():
        return redirect('/?error=Not+a+teacher')
    # checks to see if the user is a teacher before being able to access the add word page

    if request.method == "POST":
        print(request.form)
        maori = request.form.get('maori').strip()
        english = request.form.get('english').strip()
        definition = request.form.get('definition').strip()
        level = request.form.get('level')
        categoryID = request.form.get('categories')
        user_id = session.get('user_id')
        # code that gets the data that was entered into the add word page

        con = create_connection(DATABASE)

        query = "INSERT INTO word_list(id, maori, english, categoryID, definition, " \
                "level, image, editor_id, date_edited) " "VALUES(NULL,?,?,?,?,?,?,?,?)"
        # inserts the data from the user as well as the image, username and when it was submitted into the word list database

        cur = con.cursor()
        cur.execute(query, (maori, english, categoryID, definition, level, "noimage.png", user_id, datetime.now()))
        con.commit()

        con.close()

        return redirect('/')

    return render_template('add_word.html', categories=get_categories(),
                           user_data=get_user_data(session.get('user_id')),
                           logged_in=yes_logged_in(), teacher=is_teacher())

@app.route('/delete_word/<word_id>')
def render_delete_word_page(word_id):
    if not yes_logged_in():
        return redirect('/?error=Not+logged+in')
    # check for if logged in
    if not is_teacher():
        return redirect('/?error=Not+a+teacher')
    # check for if a teacher

    con = create_connection(DATABASE)

    query = "DELETE FROM word_list WHERE id=?"
    # removes data for selected word from the database
    cur = con.cursor()
    cur.execute(query, (word_id,))

    con.commit()
    con.close()


    return redirect('/?message=Word_deleted')

app.run(host='0.0.0.0', debug=True)
