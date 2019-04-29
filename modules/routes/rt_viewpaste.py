from app import app
from flask import redirect, url_for, render_template
from flask_login import current_user, login_required
from modules.database.db_main import db
from modules.database.db_models import Paste

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