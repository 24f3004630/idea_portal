from flask import Blueprint, render_template, request, redirect, session
from database.db import db
from database.models import Person

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ---------------- REGISTER STUDENT ----------------
@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists
        existing_user = Person.query.filter_by(email=email).first()
        if existing_user:
            return render_template('auth/register_student.html', 
                                 error="This email is already registered. Please use a different email or login.")

        user = Person(name=name, email=email, type='Student')
        user.set_password(password)
        user.is_approved = True

        db.session.add(user)
        db.session.commit()

        return redirect('/auth/login')

    return render_template('auth/register_student.html')


# ---------------- REGISTER FACULTY ----------------
@auth_bp.route('/register/faculty', methods=['GET', 'POST'])
def register_faculty():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists
        existing_user = Person.query.filter_by(email=email).first()
        if existing_user:
            return render_template('auth/register_faculty.html', 
                                 error="This email is already registered. Please use a different email or login.")

        user = Person(name=name, email=email, type='Faculty')
        user.set_password(password)
        user.is_approved = False  # needs admin approval

        db.session.add(user)
        db.session.commit()

        return render_template('auth/register_faculty.html', 
                             success="Registration submitted! Please wait for admin approval.")

    return render_template('auth/register_faculty.html')


# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Person.query.filter_by(email=email).first()

        if user and user.check_password(password):

            if user.type == "Faculty" and not user.is_approved:
                return "Not approved by admin"

            session['user_id'] = user.person_id
            session['role'] = user.type

            if user.type == "Admin":
                return redirect('/admin/dashboard')
            elif user.type == "Faculty":
                return redirect('/faculty/dashboard')
            else:
                return redirect('/student/dashboard')

        return "Invalid credentials"

    return render_template('auth/login.html')


# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/auth/login')