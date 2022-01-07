import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from application import application as app, db, bcrypt, mail
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from application.models import User, TodoList, Courses, Calendar
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
import re


def find_course_code(course):
    words = course.split()
    for i in words:
        pattern = re.compile("^(?=.*[a-zA-Z])(?=.*[0-9])")
        if pattern.match(i):
            return i
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    courses = Courses.query.filter_by(user_id=current_user.id)
    if request.method == "POST":
        addedCourse = request.form.get("addCourse")
        if addedCourse:
            course_code = find_course_code(addedCourse)
            if course_code is None:
                flash(
                    "For the best user experience, include your course code!", "danger")
            course = Courses(course=addedCourse,
                             course_code=course_code, user_id=current_user.id)
            db.session.add(course)
            db.session.commit()
            flash('Your have added a new course!', 'success')
        return redirect("/")
    return render_template("index.html", courses=courses)


@app.route("/course/<int:course_id>", methods=["GET", "POST"])
@login_required
def course(course_id):
    course = Courses.query.get_or_404(course_id)
    todoList = TodoList.query.filter_by(
        user_id=current_user.id, course=course.course_code).order_by(TodoList.due_date)
    if current_user.id != course.user_id:
        return redirect(url_for("index"))
    if request.method == "POST":
        course.syllabus = request.form.get("addSyllabus")
        db.session.commit()
        return redirect(url_for('course', course_id=course.id))
    return render_template('course.html', course=course, todoList=todoList)


@app.route("/<int:course_id>/delete", methods=["POST"])
@login_required
def delete_course(course_id):
    course = Courses.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        abort(403)
    db.session.delete(course)
    db.session.commit()
    flash('You have deleted an item in your Course list!', 'success')
    return redirect(url_for("index"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/calendar", methods=["GET", "POST"])
@login_required
def calendar():
    calendar = Calendar.query.filter_by(user_id=current_user.id)
    if request.method == "POST":
        title = request.json["title"]
        start = request.json["start"]
        end = request.json["end"]
        allDay = request.json["allDay"]
        recurring = request.json["recurring"]
        try:
            delete = request.json["delete"]
        except:
            delete = False
        if delete:
            Calendar.query.filter_by(
                user_id=current_user.id, title=title, start=start, end=end).delete()
            db.session.commit()
        else:
            print("BYEEEE")
            new_event = Calendar(title=title, start=start,
                                 end=end, allDay=allDay, recurring=recurring, user_id=current_user.id)
            db.session.add(new_event)
            db.session.commit()
        redirect(url_for("calendar"))
    return render_template("calendar.html", calendar=calendar)


@app.route("/todoList", methods=["GET", "POST"])
@login_required
def todoList():
    todoList = TodoList.query.filter_by(
        user_id=current_user.id).order_by(TodoList.due_date)
    courses = Courses.query.filter_by(user_id=current_user.id)
    if request.method == "POST":
        course = request.form.get("course")
        name = request.form.get("name")
        weight = request.form.get("weight")
        due_date = request.form.get("date")
        try:
            due_date = datetime.strptime(
                due_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            due_date = ""
        task = request.form.get("task")
        notes = request.form.get("notes")
        user_id = current_user.id
        new_todo = TodoList(is_checked=0, course=course,
                            name=name, weight=weight, due_date=due_date, task=task, notes=notes, user_id=user_id)
        db.session.add(new_todo)
        db.session.commit()
        flash('You have added a new item to your TODO list!', 'success')
        return redirect("/todoList")
    return render_template("todoList.html", todoList=todoList, courses=courses)


@app.route("/todoList/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    item = TodoList.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('You have deleted an item in your TODO list!', 'success')
    return redirect(url_for("todoList"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.delete.data:
        User.query.filter_by(id=current_user.id).delete()
        TodoList.query.filter_by(user_id=current_user.id).delete()
        Courses.query.filter_by(user_id=current_user.id).delete()
        Calendar.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return redirect(url_for('login'))

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)


if __name__ == "__main__":
    app.run(debug=True)
