from app import app
from flask import request, render_template, redirect, url_for
from modules.database.db_main import db
from modules.database.db_models import User
import bcrypt

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