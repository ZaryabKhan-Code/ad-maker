from flask import *
from flask_login import *
home = Blueprint('home',__name__)

@home.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('main/home.html', current_view='home')

