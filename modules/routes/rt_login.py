from app import app
from flask import request, render_template, redirect, url_for
from flask_login import login_user
from modules.database.db_main import db
from modules.database.db_models import User
import bcrypt

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