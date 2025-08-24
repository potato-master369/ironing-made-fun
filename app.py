#IMF 2.0 FLASK client
#======================================================================================================#
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify                   #
from flask_sqlalchemy import SQLAlchemy                                                                #
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user #
from werkzeug.security import generate_password_hash, check_password_hash                              #
from datetime import datetime                                                                          #
import logging                                                                                         #
import os                                                                                              #
#======================================================================================================#
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hya3paupcj3nwb73vqbort7taa3ede6e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
UPLOAD_FOLDER = '/home/debian/ironing/uploads'
print(UPLOAD_FOLDER)
os.makedirs('pictures', exist_ok=True)

app.config['UPLOAD_FOLDER'] = 'pictures'
logging.basicConfig(
    filename='app.log',             # Log file name
    level=logging.INFO,             # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

db = SQLAlchemy(app)

#class defns
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    points = db.Column(db.Integer, default=0)
    role = db.Column(db.String(20), default="user")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/rewards")
def poc_v1():
    return render_template("rewards.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(username=request.form['username'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route("/forum", methods=["GET", "POST"])
@login_required
def forum():
    if request.method == "POST":
        new_msg = Message(author=current_user.username, content=request.form["content"])
        db.session.add(new_msg)
        db.session.commit()
        return redirect("/forum")

    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return render_template("forum.html", messages=messages)

@app.route("/submit")
@login_required
def submit():
    return render_template("submit.html")

@app.route("/badges")
@login_required
def badges():
    users = User.query.order_by(User.points.desc()).all()
    return render_template("badges.html", users=users)
    
@app.route('/capture', methods=['GET'])
@login_required
def capture():
        # You can decode and save the image if needed
        current_user.points += 5
        db.session.commit()
        flash("Image captured and point awarded!", "success")
        return redirect(url_for('camera'))

@app.route('/rewards')
@login_required
def rewards():
    return render_template("rewards.html")

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        abort(403)

    try:
        with open("/home/debian/ironing/app.log", "r") as f:
            log1 = f.readlines()
    except FileNotFoundError:
        log1 = "FileNotFoundError reported at app.py."
    print(log1)
    uploads = []
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    if os.path.exists(upload_dir):
        uploads = os.listdir(upload_dir)
    log = log1[:-100]
    users = User.query.order_by(User.id).all()
    stats = {
        "total_users": User.query.count(),
        "admin_count": User.query.filter_by(role="admin").count(),
        "moderator_count": User.query.filter_by(role="moderator").count(),
    }
    return render_template("admin.html", users=users, stats=stats)

@app.route("/promote", methods=["POST"])
@login_required
def promote():
    # Only allow actual admins to perform promotions
    if current_user.role != "admin":
        abort(403)

    user_id = request.form.get("user_id")
    user = User.query.get(int(user_id))
    if user and user.role != "admin":
        user.role = "admin"
        db.session.commit()
    
    return redirect(url_for("admin_dashboard"))

@app.route("/delete", methods=["POST"])
@login_required
def delete_user():
    if current_user.role != "admin":
        abort(403)

    user_id = request.form.get("user_id")
    user = User.query.get(int(user_id))
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("admin_dashboard"))
    with open("app.log") as f:
        log = f.read()




# --- Change Password ---
@app.route("/change-password", methods=["POST"])
@login_required
def change_password():
    if current_user.role != "admin":
        abort(403)

    user_id = request.form.get("user_id")
    new_password = request.form.get("new_password")
    user = User.query.get(int(user_id))
    if user and new_password:
        user.password = generate_password_hash(new_password)
        db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file submitted!"

    file = request.files['file']  # <--- assign file here!

    if file.filename == '':
       return "No file submitted!"
    if os.path.isfile(os.path.join("/home/debian/ironing/uploads", file.filename)):
       return "This is a repeated file."
    else:
       filename, file_extension = os.path.splitext('/home/debian/ironing/' + file.filename)
       if file_extension == ".png" or file_extension == ".jpg" or file_extension == ".pdf" or file_extension == ".jpeg":
           current_user.points += 5
           db.session.commit()

           print(current_user.username, "submitted photo", file.filename)
           file_path = os.path.join(UPLOAD_FOLDER, file.filename)
           file.save(file_path)
           return "Upload successful: +5 points!"
       else:
           return "Wrong format submitted!"

#Fancy errors!
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def no_access(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.route('/trigger-error/<int:error_code>')
def trigger_error(error_code):
    if error_code == 404:
        # Triggers a "Not Found" error
        abort(404)
    elif error_code == 500:
        # Triggers an "Internal Server Error"
        raise RuntimeError("This is a simulated 500 error.")
    elif error_code == 403:
        # Triggers a "Forbidden" error
        abort(403)
    else:
        # Aborts with the specified error code
        abort(error_code)

# You can add more routes as needed
if __name__ == "__main__":
    app.run(port = 5000, debug=False, host = '0.0.0.0')

