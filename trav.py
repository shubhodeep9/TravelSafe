import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

DATABASE = 'trav.db'
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('TRAVELSAFE_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('blog.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def landing():
    if session.get('id'):
        return redirect(url_for('homepage'))
    return render_template('landing.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        user = g.db.execute('select * from users where p_num = ? and password = ?',[request.form['pn'],request.form['pw']])
        if len(user.fetchall())==0:
            error = 'Invalid Phone Number OR Password, Try Again'
        else:
            session['id'] = request.form['pn']
            return redirect(url_for('homepage'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        user = g.db.execute('select * from users where p_num = ?',[request.form['pn']])
        if len(user.fetchall())>0:
            error = 'Phone Number already use'
        else:
            g.db.execute('insert into users (p_num,password) values (?,?)',[request.form['pn'],request.form['pw']])
            g.db.execute('insert into friends (p_num,f_num) values (?,?)',[request.form['pn'],request.form['fn']])
            g.db.commit()
            return redirect(url_for('landing'))
    return error



if __name__ == '__main__':
    app.run()
