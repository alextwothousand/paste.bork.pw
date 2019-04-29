from app import app
from flask import redirect, url_for, render_template
from flask_login import current_user, login_required
from modules.database.db_main import db
from modules.database.db_models import Paste

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