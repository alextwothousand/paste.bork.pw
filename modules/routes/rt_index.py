from app import app
from flask import redirect, url_for, render_template
from flask_login import current_user
from modules.database.db_models import Paste

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user', name=current_user.username))
    else:
        return render_template(
            'main/index.html',
            snippets=Paste.query.filter_by(type=0).limit(10).all()
        )