import datetime
from blogsite import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
    blog = db.relationship('Blog', backref='author', lazy=True)

    def __repr__(self):
        return f"""
                Fullname: {self.name}\n
                Email: {self.email}\n
                Profile Pic: {self.profile_pic}
                """


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.date.today())
    content = db.Column(db.Text, nullable=False)
    audio = db.Column(db.String(20))
    video = db.Column(db.String(20))
    image = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"""
                Title: {self.title}\n
                Date: {self.date_posted}\n
                Content: {self.content}
                """