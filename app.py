from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ✅ Flask-MySQLdb Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Latpot@12'  # Replace with your actual password
app.config['MYSQL_DB'] = 'feedback_db'

# ✅ Initialize MySQL
mysql = MySQL(app)

# -------------------------------------
# Routes
# -------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        mysql.connection.commit()
        cursor.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/feedback')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO feedbacks (user_id, subject, message) VALUES (%s, %s, %s)",
                       (session['user_id'], subject, message))
        mysql.connection.commit()
        cursor.close()

        return "Thank you for your feedback!"
    return render_template('feedback.html')

@app.route('/admin')
def admin():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT f.id, u.username, f.subject, f.message
        FROM feedbacks f
        JOIN users u ON f.user_id = u.id
    """)
    feedbacks = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', feedbacks=feedbacks)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------------------------------------
# Run the App
# -------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
