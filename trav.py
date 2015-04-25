import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

DATABASE = 'blog.db'
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('Trav_Settings', silent=True)

@app.route('/')
def landing():
    if session.get('id'):
        return redirect(url_for('homepage'))
    return render_template('landing.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        user = g.db.execute('select * from users where p_num = ? and pass = ?',[request.form['pn'],request.form['pw']])
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
            g.db.execute('insert into users (p_num,pass) value (?,?)',[request.form['pn'],])



if __name__ == '__main__':
    app.run()
