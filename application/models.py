from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from application import db, login_manager, application as app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    todoList = db.relationship("TodoList", backref="author", lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_checked = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(20))
    name = db.Column(db.String(20))
    weight = db.Column(db.String(20))
    due_date = db.Column(db.String(20))
    task = db.Column(db.String(20))
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"TodoList('{self.is_checked}', '{self.course}', '{self.name}','{self.weight}','{self.due_date}','{self.task}', '{self.notes}')"


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(30))
    course_code = db.Column(db.String(20))
    syllabus = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Courses('{self.course}')"


class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    start = db.Column(db.String(30))
    end = db.Column(db.String(30))
    recurring = db.Column(db.Integer)
    allDay = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Calendar('{self.title}','{self.start}','{self.end}','{self.allDay}')"
