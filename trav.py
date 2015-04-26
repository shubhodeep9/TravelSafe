import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from werkzeug import secure_filename
import qrtools
from datetime import datetime

DATABASE = 'trav.db'
DEBUG = True
SECRET_KEY = 'development key'
UPLOAD_FOLDER = '/home/shubhodeep/TravelSafe/static/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'svg'])


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

@app.route('/home')
def homepage():
    if not session.get('id'):
        return redirect(url_for('landing'))
    return render_template('home.html')

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
    return error

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    error = None
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded', filename = filename))
        else:
            error = "Sorry something wrong happened"
    return error


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

@app.route('/add_friend', methods = ['GET', 'POST'])
def add_friend():
    error = None
    if request.method == 'POST':
        friend = g.db.execute('select * from friends where p_num = ? and f_num = ?',[session.get('id'),request.form['fn']])
        if len(friend.fetchall())>0:
            error = 'Friend already added'
        else:
            g.db.execute('insert into friends (p_num,f_num) values (?,?)',[session.get('id'),request.form['fn']])
            g.db.commit()
            return redirect(url_for('homepage'))
    return error

@app.route('/uploaded')
def uploaded():
    error = None
    if not session.get('id'):
        return redirect(url_for('landing'))
    qr = qrtools.QR()

    if qr.decode(os.path.join(app.config['UPLOAD_FOLDER'], request.args['filename'])):
        data = qr.data
        f = data.split(':')
        f[1] = int(f[1])
        time = datetime.now()
        g.db.execute('insert into vehicle (p_num,num_plate,d_id,stamp) values (?,?,?,?)',[session.get('id'),f[0],f[1],time])
        g.db.commit()
        return redirect(url_for('homepage'))
    else:
        error = 'Error'
    return error




@app.route('/pass', methods = ['GET', 'POST'])
def password():
    error = None
    if request.method == 'POST':
        if request.form['pw'] == request.form['cpw']:
            g.db.execute('update users set password = ? where p_num = ?',[request.form['pw'],session.get('id')])
            g.db.commit()
            return redirect(url_for('homepage'))
        else:
            error = 'Passwords do not match'
    return error

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run()
