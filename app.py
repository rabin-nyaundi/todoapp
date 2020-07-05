import requests, datetime, requests
from models import *

from sqlalchemy import and_

from flask import Flask, flash, render_template, url_for, request, flash, session, redirect

from werkzeug.security import generate_password_hash, check_password_hash

from flask_session import Session

app = Flask(__name__)

app.config["SECRET_KEY"] = 'DNkWChBzTyb81CTXS2MU0A'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Check for environment variable
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


@app.route('/', methods=['POST','GET'])
def index():
    date = datetime.date.today()
    if 'user' in session:
        email = session['user']

        user = Users.query.filter_by(email = session['user']).first()

        # tasks = Tasks.query.filter_by(task_user = user.id).all()
        tasks = Tasks.query.filter(and_(Tasks.task_user == user.id,Tasks.created_at == date)).all()

        return render_template('index.html',user = email, tasks = tasks)



    return redirect(url_for('login'))


@app.route('/login', methods=['POST','GET'])
def login():
    session.pop('user', None)
    if request.method == 'POST':

        user_email = request.form.get('email')
        passwd = request.form.get('password')

        user = Users.query.filter_by(email = user_email).first()
        
        if not user:
            flash('User does not exists or wrong email address', 'danger')
            return redirect(url_for('login'))

        if not check_password_hash(user.password, passwd):
            flash("Wrong password","danger")
            return redirect(url_for('login'))

        session['user'] = user.email
        return redirect(url_for('index'))

    
    if 'user' in session:
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/signup', methods=['POST','GET'])
def signup():

    if request.method == 'POST':

        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')

        if(len(password) < 6):
            flash('Password should be at least 6 characters', 'danger')
            return redirect(url_for('signup'))

        if Users.query.filter_by(email=email).first():
            flash('User already exists! Login', 'danger')
            return redirect(url_for('login'))

        Users.add_user(id,firstname,lastname,email,generate_password_hash(password, method='sha256'))

        flash('Account create success', 'success')
        return redirect(url_for('login'))


    return render_template('signup.html')


@app.route('/task', methods=['POST','GET'])
def task():
    date= datetime.datetime.today()
    if request.method == 'POST':
        task = request.form.get('task')
        status = 'Not complete'

        user = Users.query.filter_by(email = session['user']).first()
        if task is None:
            flash('Please fill all the fields and try again','danger')
        
        Tasks.add_task(id,task,user.id,date,status)
        flash('Todo task added successfully', 'success')

        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user', None) 
    
    return redirect(url_for('index'))


@app.route('/all', methods=['POST','GET'])
def all_tasks():
    user = Users.query.filter_by(email = session['user']).first()

    tasks = Tasks.query.filter_by(task_user = user.id).all()

    count  = Tasks.query.filter_by(task_user = user.id).count()

    return render_template('index.html',tasks = tasks, count=count)


@app.route('/complete', methods = ['POST','GET'])
def complete_tasks():
    user = Users.query.filter_by(email = session['user']).first()

    tasks = Tasks.query.filter(and_(Tasks.task_user == user.id, Tasks.status == 'Complete')).all()

    count_complete = Tasks.query.filter(and_(Tasks.task_user == user.id, Tasks.status == 'Complete')).count()
    
    return render_template('index.html', tasks = tasks, count_complete = count_complete)

@app.route('/not_complete')
def not_complete():
    user = Users.query.filter_by(email = session['user']).first()

    tasks = Tasks.query.filter(and_(Tasks.task_user == user.id, Tasks.status == 'Not complete')).all()

    count_incomplete = Tasks.query.filter(and_(Tasks.task_user == user.id, Tasks.status == 'Not complete')).count()
    
    return render_template('index.html', tasks = tasks, count_incomplete = count_incomplete)





@app.route('/delete/<int:id>')
def delete(id):

    try:

        tasks = Tasks.query.get_or_404(id)
        db.session.delete(tasks)
        db.session.commit()

        flash('Todo task deleted', 'danger')
        return redirect(url_for('index'))

    except:
        return 'Failed'

@app.route('/edit/<int:id>')
def edit(id):

    try:
        task = Tasks.query.get_or_404(id)
        task.status = 'Complete'
        db.session.commit()

        flash('Todo task completed', 'success')
        return redirect(url_for('index'))

    except:
        return 'Failed'
