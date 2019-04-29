from modules.loginmanager.lm_main import login_manager
from modules.database.db_models import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))