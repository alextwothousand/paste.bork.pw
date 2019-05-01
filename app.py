from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from hashlib import sha1
from os import urandom
from datetime import datetime
from random import randint
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/paste'
app.secret_key = urandom(30)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import *

# Notes:
# > now.strftime("%Y-%m-%d %H:%M")
# > to load in spaces from db: > style="white-space: pre-line" <

# To-Do:
# > Implement error handling (http://flask.pocoo.org/docs/1.0/patterns/errorpages/)
# > Modulate code
# > Finish up any places that lack 100% completion (delete, view, user)
# > Rename the functions to things that are relatively better
# > Make it so that anyone can view public pastes
# > Make the script a bit uniform, everything is in a mess (snippets, gists, pastes), needs to be one word


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user', name=current_user.username))
    else:
        return render_template(
            'main/index.html',
            snippets=Paste.query.filter_by(type=0).limit(10).all()
        )

@app.route("/about")
def about():
    # add user authentification check, otherwise redirect home
    return render_template(
        'main/about.html',
    )

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template(
            'accounts/login.html',
            error=''
        )

    identifier = request.form['username']
    password = request.form['password']
    username = None

    if '@' in identifier:
        if db.session.query(db.exists().where(User.email == identifier)).scalar() is False:
            return render_template(
                'accounts/login.html',
                error='No account with that email could been found.'
            )
        else:
            user = User.query.filter_by(email=identifier).first()
            username = user.username

    else:
        if db.session.query(db.exists().where(User.username == identifier)).scalar() is False:
            return render_template(
                'accounts/login.html',
                error='No account with that username could be found.'
            )
        else:
            user = User.query.filter_by(username=identifier).first()
            username = user.username

    user = User.query.filter_by(username=username).first()

    if bcrypt.checkpw(password.encode(), user.password.encode()):
        login_user(user)
        return redirect(request.args.get('next') or url_for('user', name=user.username))
    else:
        return render_template(
            'accounts/login.html',
            error='Password incorrect!',
        )

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template(
            'accounts/register.html',
            error=''
        )

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    if len(username) < 3:
        return render_template(
            'accounts/register.html',
            error='Your username must be longer than three characters.'
        )

    if len(email) < 1:
        return render_template(
            'accounts/register.html',
            error='You must enter a email.'
        )

    for i in ['@', '.']:
        if i not in email:
            return render_template(
                'accounts/register.html',
                error="That doesn't look like a email to me. Try again!"
            )

    if len(password) < 1:
        return render_template(
            'accounts/register.html',
            error='You must enter a password.'
        )

    if db.session.query(db.exists().where(User.username == username)).scalar() is True:
        return render_template(
            'accounts/register.html',
            error='Username is already in use.'
        )

    if db.session.query(db.exists().where(User.email == email)).scalar() is True:
        return render_template(
            'accounts/register.html',
            error='Email is already in use.'
        )

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    member = User(username=username, password=hashed, email=email)

    db.session.add(member)
    db.session.commit()

    return redirect(url_for('login'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/<name>")
@login_required
def user(name, paste_name = ''):
    if current_user.username == name:
        return render_template(
            'home.html',
            snippets=Paste.query.filter_by(author=current_user.id).all(),
            pastename=paste_name
        )

@app.route("/<name>/create", methods=['GET', 'POST'])
@login_required
def create(name):
    if request.method == 'GET':
        if current_user.username == name:
            return render_template(
                'create.html',
                error=''
            )
        
        return redirect(url_for('create', name=current_user.username))

    title = request.form['title']
    description = request.form['description']
    code = request.form['code']
    paste_type_string = request.form['type']
    paste_type = 0

    if len(title) < 3:
        return render_template(
            'create.html',
            error='Title must be three or more characters.'
        )

    if ' ' in title:
        return render_template(
            'create.html',
            error='Title cannot contain spaces.'
            )

    if len(code) < 1:
        return render_template(
            'create.html',
            error='You must include some form of code.'
        )

    if len(code) > 5000:
        return render_template(
            'create.html',
            error='Your code has exceeded 5000 characters. If this is too low of a limitation, feel free to contact me!'
        )

    if paste_type_string == 'public':
        paste_type = 0
    elif paste_type_string == 'private':
        paste_type = 1

    # sha hash: authorid, authorname, title, moreinfo, randomint
    hash = sha1(f"{current_user.id}{current_user.username}{title}{description}{randint(0, 100)}".encode()).hexdigest()
    paste = Paste(author = current_user.id, sha = hash, type = paste_type, info = title, moreinfo = description, code = code)

    db.session.add(paste)
    db.session.commit()

    return redirect(url_for('user', name=current_user.username))

@app.route("/<name>/<scriptname>")
@login_required
def view(name, scriptname):
    if current_user.username == name:
        if db.session.query(db.exists().where(Paste.sha == scriptname)).scalar() is True:
            return redirect(
                url_for(
                    'view', 
                    name=name, 
                    scriptname=Paste.query.filter_by(sha=scriptname).first().info
                )
            )

        elif db.session.query(db.exists().where(Paste.info == scriptname)).scalar() is True:
            return render_template(
                'view.html',
                script=Paste.query.filter_by(info=scriptname).first(),
                author=name
            )

        else:
            return render_template(
                '404.html'
            )

@app.route("/<name>/<scriptname>/delete")
@login_required
def delete(name, scriptname):
    if current_user.username == name:
        if db.session.query(db.exists().where(Paste.sha == scriptname)).scalar() is True:
            return redirect(
                url_for(
                    'view', 
                    name=name, 
                    scriptname=Paste.query.filter_by(sha=scriptname).first().info
                )
            )

        elif db.session.query(db.exists().where(Paste.info == scriptname)).scalar() is True:
            paste_name = Paste.query.filter_by(info=scriptname).first().info
            Paste.query.filter_by(info=scriptname).delete()
            db.session.commit()

            return redirect(url_for('user', name=name, pastename=f"Your paste, {paste_name}, has successfully been deleted!"))

        else:
            return render_template(
                '404.html'
            )

    else:
        return render_template(
            '404.html'
        )

@app.route("/<name>/<scriptname>/raw")
def raw(name, scriptname):
    if current_user.username == name:
        if db.session.query(db.exists().where(Paste.sha == scriptname)).scalar() is True:
            return redirect(
                url_for(
                    'raw', 
                    name=name, 
                    scriptname=Paste.query.filter_by(sha=scriptname).first().info
                )
            )

        elif db.session.query(db.exists().where(Paste.info == scriptname)).scalar() is True:
            return render_template(
                'raw.html',
                code=Paste.query.filter_by(info=scriptname).first().code
            )

        else:
            return render_template(
                '404.html'
            )

    else:
        return render_template(
            '404.html'
        )


if __name__ == '__main__':
    db.create_all()
    app.run()