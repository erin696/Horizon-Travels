from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt 
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Secret key for session management
app.secret_key = 'your_secret_key'

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '#aStrid922pizza'
app.config['MYSQL_DB'] = 'horizon_travels'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book')
def book():
    return render_template('book.html')
@app.route('/acct', methods=["GET", "POST"])
def account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user_id WHERE user_id = %s", (session["user_id"],))
    user = cursor.fetchone()  # ✅ Fetch user from the database

    if user is None:
        flash("User not found!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        first_name = request.form["firstName"]
        last_name = request.form["lastName"]

        cursor.execute("UPDATE user_id SET f_name = %s, l_name = %s WHERE user_id = %s",
                       (first_name, last_name, session["user_id"]))
        mysql.connection.commit()  # ✅ Save changes to the database

        flash("Profile updated successfully!", "success")

    cursor.close()  # ✅ Close the cursor after use
    return render_template("account.html", user=user)  # ✅ Pass the user object



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_id WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            flash('Login successful!', 'success')
            return redirect(url_for('account'))  # ✅ Redirect to account instead!
        else:
            flash('Incorrect email or password', 'danger')
    
    return render_template('my_account.html', user=None)  # ✅ Pass user as None to avoid errors


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO user_id (f_name, l_name, email, password) VALUES (%s, %s, %s, %s)', 
                       (f_name, l_name, email, hashed_password))
        mysql.connection.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
