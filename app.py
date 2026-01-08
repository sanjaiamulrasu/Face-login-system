from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from database import db, User
from face_utils import capture_face, recognize_face

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template("dashboard.html", user=user)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        # Check if username already exists
        existing_user = User.query.filter_by(username=request.form["username"]).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))
        
        user = User(
            name=request.form["name"],
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            roll_no=request.form["roll"],
            department=request.form["department"],
            dob=request.form["dob"],
            phone=request.form["phone"],
            email=request.form["email"]
        )
        db.session.add(user)
        db.session.commit()

        try:
            capture_face(user.id)
            flash('Registration successful! Please login.', 'success')
        except Exception as e:
            flash(f'Registration successful but face capture failed: {str(e)}', 'warning')
        
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/face-login", methods=["GET","POST"])
def face_login():
    if request.method == "POST":
        try:
            user_id, confidence = recognize_face()

            if user_id is None:
                flash("No trained face data found. Please register first.", 'error')
                return redirect(url_for('face_login'))

            if confidence < 80:  # Lower confidence means better match in LBPH
                user = User.query.get(user_id)
                if user:
                    session['user_id'] = user.id
                    session['username'] = user.username
                    flash(f'Face Login Successful! Welcome {user.name}', 'success')
                    return redirect(url_for('dashboard'))

            flash("Face Not Recognized. Please try again.", 'error')
        except Exception as e:
            flash(f'Face recognition error: {str(e)}', 'error')
        
        return redirect(url_for('face_login'))

    return render_template("face_login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    username = session.get('username')
    session.clear()
    flash(f'You have been logged out successfully.', 'success')
    return redirect(url_for('main'))

if __name__ == "__main__":
    app.run(debug=True)