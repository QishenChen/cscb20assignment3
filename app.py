from flask import Flask, request, flash, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt=Bcrypt(app)
app.template_folder = 'templates'
app.config['SECRET_KEY']='8a0f946f1471e113e528d927220ad977ed8b2cce63303beff10c8cb4a15e1a99'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///assignment3.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 10)
db = SQLAlchemy(app)
class feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    message_evaluation = db.Column(db.String(500), nullable=False)
    message_improvement = db.Column(db.String(500), nullable=False)
    lab_advice = db.Column(db.String(500), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"evaluation: {self.message_evaluation}", "improvement: {self.message_improvement}",\
                "improvement aspects: {self.message_improvement}"
class grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
class user(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    grade = db.relationship('grade', backref='user', lazy=True)
class regrade_request(db.Model):
    __tablename__ = 'regrade_request'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        thispassword = request.form['password']
        class_name = request.form['class_name']
        hashed_password = bcrypt.generate_password_hash(thispassword).decode('utf-8')
        new_user = user(username=username, password=hashed_password, class_name=class_name)
        if user.query.filter_by(username=username).scalar() is not None:
            flash("Username already exists")
            return redirect(url_for('register'))
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logged_user = user.query.filter_by(username=username).first()
        if logged_user:
            if bcrypt.check_password_hash(logged_user.password, password):
                if logged_user.class_name == 'student':
                    session['student_id'] = logged_user.id
                else :
                    session['teacher_id'] = logged_user.id
                return redirect(url_for('feedback'))
        flash("Invalid username or password")
    return render_template('login.html')

@app.route('/mainpage')
def mainpage():
    # Define your main page functionality here
    return render_template('mainpage.html')

@app.route('/feedback', methods=['GET', 'POST'])
def add_feedback():
    if request.method == 'POST':
        message_evaluation = request.form['message_evaluation']
        message_improvement = request.form['message_improvement']
        lab_advice = request.form['lab_advice']
        new_feedback = feedback(message_evaluation=message_evaluation, message_improvement=message_improvement)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('add_feedback'))
    return render_template('feedback.html')
@app.route('/grade_view', methods=['GET', 'POST'])
def view_grade():
    if request.method=='GET':
        if session.get('teacher_id') is None:
            return redirect(url_for('home'))
        student_grade=grade.query.filter_by(id=session.get('student_id')).first()
        return render_template('grade_view.html', student_grade=student_grade)
@app.route('/grade', methods=['GET', 'POST'])
def add_grade():
    if request.method == 'POST':
        if session.get('teacher_id') is None:
            return redirect(url_for('home'))
        student=request.form['student']
        student_id = user.query.filter_by(username=student).first().id
        grade = request.form['grade']
        new_grade = grade(grade=grade, user_id=student_id)
        db.session.add(new_grade)
        db.session.commit()
        return redirect(url_for('add_grade'))
    return render_template('grade.html')

@app.route('/regrade_request/<grade_id>/', methods=['GET', 'POST'])
def regrade_request(grade_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        new_regrade_request = regrade_request(name=name, email=email, message=message, grade_id=grade_id)
        db.session.add(new_regrade_request)
        db.session.commit()
        return redirect(url_for('regrade_request'))
    return render_template('regrade_request.html',grade_id=grade_id)
@app.route('/change_grade/<grade_id>', methods=['GET', 'POST'])
def change_grade():
    if request.method == 'POST':
        if session.get('teacher_id') is None:
            return redirect(url_for('home'))
        grade_id = request.form['grade_id']
        new_grade = request.form['new_grade']
        grade.query.filter_by(id=grade_id).update(dict(grade=new_grade))
        db.session.commit()
        return redirect(url_for('change_grade'))
    return render_template('change_grade.html')
@app.route('/regrade_request_view', methods=['GET'])
def regrade_request_view():
    if session.get('teacher_id') is None:
        return redirect(url_for('home'))
    regrade_request=regrade_request.query.all()
    return render_template('regrade_request_view.html', regrade_request=regrade_request)
@app.route('/regrade_request_delete/<regrade_request_id>', methods=['GET'])
def regrade_request_delete(regrade_request_id):
    if session.get('teacher_id') is None:
        return redirect(url_for('home'))
    regrade_request.query.filter_by(id=regrade_request_id).delete()
    db.session.commit()
    return redirect(url_for('regrade_request_view'))
@app.route('/feeedback_view', methods=['GET'])
def feedback_view():
    if session.get('teacher_id') is None:
        return redirect(url_for('home'))
    feedback=feedback.query.filter_by(teacher_id=session.get('teacher_id')).all()
    return render_template('feedback_view.html', feedback=feedback)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
