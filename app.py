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

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    message_evaluation = db.Column(db.String(500), nullable=False)
    message_improvement = db.Column(db.String(500), nullable=False)
    lab_advice = db.Column(db.String(500), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Feedback(id={self.id}, evaluation={self.message_evaluation}, improvement={self.message_improvement}, lab_advice={self.lab_advice})"


class grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_type = db.Column(db.String(100), nullable=False)  # Type of assignment (e.g., assignment, lab, midterm, final)
    grade = db.Column(db.String(100), nullable=False)
    remark_request = db.Column(db.Boolean, default=False)  # True if remark request has been submitted
    remark_request_reason = db.Column(db.Text)  # Explanation for the remark request

class user(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    grade = db.relationship('grade', backref='user', lazy=True)

class regrade_request_model(db.Model):
    __tablename__ = 'regrade_request_model'
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
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form['username']
        thispassword = request.form['password']
        class_name = request.form['class_name']
        hashed_password = bcrypt.generate_password_hash(thispassword).decode('utf-8')
        new_user = user(username=username, password=hashed_password, class_name=class_name)
        if user.query.filter_by(username=username).count() > 0:
            flash("Username already exists")
        else:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful. Please log in.")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logged_user = user.query.filter_by(username=username).first()
        print(logged_user.id)
        if logged_user:
            if bcrypt.check_password_hash(logged_user.password, password):
                if logged_user.class_name == 'student':
                    session['student_id'] = logged_user.id
                else :
                    session['teacher_id'] = logged_user.id
            return redirect(url_for('home'))
        flash("Invalid username or password")
    if request.method == 'GET':
        if session.get('student_id') is not None or session.get('teacher_id') is not None:
            return redirect(url_for('home'))
        else:
            return render_template('login.html')

@app.route('/add_feedback', methods=['GET', 'POST'])
def add_feedback():
    if request.method == 'POST':
        message_evaluation = request.form['message_evaluation']
        message_improvement = request.form['message_improvement']
        lab_advice = request.form['lab_advice']
        teacher=request.form['teacher']
        teacher_id = user.query.filter_by(username=teacher).first().id
        new_feedback = Feedback(message_evaluation=message_evaluation, message_improvement=message_improvement, lab_advice=lab_advice, teacher_id=teacher_id)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('add_feedback'))
    return render_template('feedback.html')

@app.route('/feedback_view', methods=['GET'])
def feedback_view():
    if session.get('teacher_id') is None:
        return redirect(url_for('home'))
    feedback_entries = Feedback.query.filter_by(teacher_id=session.get('teacher_id')).all()
    print(feedback_entries)
    return render_template('feedback_view.html', feedback_entries=feedback_entries)
@app.route('/mainpage')
def mainpage():
    # Define your main page functionality here
    return render_template('mainpage.html')

@app.route('/grade_view', methods=['GET', 'POST'])
def view_grade():
    if request.method=='GET':
        if session.get('student_id') is None:
            return redirect(url_for('home'))
        student_grade=grade.query.filter_by(user_id=session.get('student_id')).all()
        return render_template('grade_view.html', student_grade=student_grade)
# this page is designed for teacher to post students' grades for the first time
@app.route('/grade', methods=['GET', 'POST'])
def add_grade():
    if request.method == 'POST':
        if session.get('teacher_id') is None:
            return redirect(url_for('home'))
        student=request.form['student']
        student_id = user.query.filter_by(username=student).first().id
        thisgrade = request.form['grade']
        assignment_type = request.form['assignment_type']
        new_grade = grade(grade=thisgrade, user_id=student_id , assignment_type=assignment_type)
        db.session.add(new_grade)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('grade.html')

@app.route('/regrade_request/<grade_id>', methods=['GET', 'POST'])
def regrade_request(grade_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        new_regrade_request = regrade_request_model(name=name, email=email, message=message, grade_id=grade_id)
        db.session.add(new_regrade_request)
        db.session.commit()
        return redirect(url_for('view_grade'))
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


@app.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('teacher_id', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
