from app import app
from flask import request, render_template, redirect, url_for
from flask_login import current_user, login_required
from modules.database.db_main import db
from modules.database.db_models import Paste
from random import randint
from hashlib import sha1

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