from app import app
from flask import render_template
from flask_login import current_user, login_required
from modules.database.db_models import Paste

@app.route("/<name>")
@login_required
def user(name, paste_name = ''):
    if current_user.username == name:
        return render_template(
            'home.html',
            snippets=Paste.query.filter_by(author=current_user.id).all(),
            pastename=paste_name
        )