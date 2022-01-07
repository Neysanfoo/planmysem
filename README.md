# Plan My Sem

## CS50

This is my final project for CS50 - Harvard's Introduction to Computer Science.
It is a web planner for university students.

The website contains 4 main features:

- Course list
- TODO list
- Calendar
- GPA calculator

#### Video Demo: <https://youtu.be/-mPVuynOsuY>

## Languages, Frameworks, Packages

Languages used: Python, HTML, CSS, Javascript, SQL.

Frameworks used: Flask, Bootstrap, AWS.

The calendar is implemented using the FullCalendar package.

## Description of Files

The templates/ directory contains the HTML for all the pages. Each page has the same basic layout which is included in every page using jinja2.

The static/ directory contains all the static components for the website, such as images as well as the CSS file.

The routes.py file contains routes to the different URLs. By including the dectorator: @app.route(), we can bind the URL to a function.
e.g.

```
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html");
```

will bind the route "/" to the function index().

The models.py file contains the classes for our objects that are stored in our database (site.db).

The forms.py file contains the classes for our forms, such as our registration form, login form, etc.

The **init**.py file initializes our flask application, it connects our application with our sqlite3 database. It also configures our gmail account that sends the reset password link.

## Database

All user info, e.g. username, email, password(hashed) is saved to an sqlite3 database. All the data written in the TODO list, course list and calendar is also saved to the same databse.

If users forget their password, they can enter the email they signed up with, and will be sent a email with a link to reset their password. Users can also change their email and username once their account has been created.

There is no complexity requirements for the password, which could be a security issue.

To communicate with our database, we use SQLAlchemy.

## Deployment

The website is deployed using an AWS EC2 instance.
