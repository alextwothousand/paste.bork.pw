from app import app
from flask import render_template

@app.route("/about")
def about():
    # add user authentification check, otherwise redirect home
    return render_template(
        'main/about.html',
    )