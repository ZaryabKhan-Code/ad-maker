from flask import *
auth = Blueprint('auth',__name__)
from flask_dance.contrib.google import google
from flask_login import logout_user, login_required,current_user
from util.viewoauth import google_blueprint,login_user_with_credentials,register_user
auth.register_blueprint(google_blueprint, url_prefix="/google_login")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            if login_user_with_credentials(username, password):
                return redirect(url_for("home.index"))
            else:
                return render_template("auth/login.html")
        except Exception as e:
            flash("Invalid email or password", "danger")
            return render_template("auth/login.html")
    return render_template("auth/login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if request.method == "POST":
        username = request.form.get("email")
        name = request.form.get("username")
        password = request.form.get("password")

        try:
            success, message = register_user(username, password, name=name)

            if success:
                flash(message, "success")
                return redirect(url_for("auth.login"))
            else:
                flash(message, "danger")
                return redirect(url_for("auth.register"))
        except Exception as e:
            flash("An error occurred during registration. Please try again later.", "danger")
            return redirect(url_for("auth.register"))
    return render_template('auth/register.html')

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.index"))

@auth.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("auth.google.login"))
    return redirect(url_for("home.index"))


