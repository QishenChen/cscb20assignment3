from flask import Flask, request, flash, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
app = Flask(__name__)
Bcrypt = Bcrypt(app)
app.config['sqlalchemY_DATABASE_URI']='sqlite:///notes.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 10)
db = SQLAlchemy(app)
class feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    message_evaluation = db.Column(db.String(500), nullable=False)
    message_improvement = db.Column(db.String(500), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), nullable=False)
    def __repr__(self):
        return f"elavaluation: {self.message_evaluation}", "improvement: {self.message_improvement}",\
                "improvement aspects: {self.message_improvement}"
class grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
class user(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    grade = db.relationship('grade', backref='user', lazy=True)
    feedback = db.relationship('feedback', backref='user', lazy=True)
class regrade_request(db.Model):
    __tablename__ = 'regrade_request'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
class student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
class teacher(db.Model):
    __tablename__ = 'teacher'
    teacher_id = db.Column(db.Integer, primary_key=True)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        class_name = request.form['class_name']
        hashed_password = Bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = user(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        if class_name == 'student':
            new_student = student(student_id=new_user.id)
            db.session.add(new_student)
            db.session.commit()
        if class_name == 'teacher':
            new_teacher = teacher(teacher_id=new_user.id)
            db.session.add(new_teacher)
            db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user.query.filter_by(username=username).first()
        if user:
            if Bcrypt.check_password_hash(user.password, password):
                if db.session.query(student).filter_by(student_id=user.id).scalar() is not None:
                    session['student_id'] = user.id
                else :
                    session['teacher_id'] = user.id
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/feedback', methods=['GET', 'POST'])
def add_feedback():
    if request.method == 'POST':
        message_evaluation = request.form['message_evaluation']
        message_improvement = request.form['message_improvement']
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
@app.route('feeedback_view', methods=['GET'])
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
