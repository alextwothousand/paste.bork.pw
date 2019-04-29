from flask import Flask
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(30)

from modules.loginmanager import *
from modules.database import *
from modules.routes import *

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

if __name__ == '__main__':
    db.create_all()
    app.run()