from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from blogsite.models import User
from blogsite import bcrypt


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me!")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message='Password did not match')])
    submit = SubmitField("Register")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered!')


class UpdateNameForm(FlaskForm):
    name = StringField("New Full Name", validators=[DataRequired(), Length(min=2, max=15)])
    submit = SubmitField("Update Name")

    def validate_name(self, name):
        if current_user.name == name.data:
            raise ValidationError(f" \"{name.data}\" is already selected ")


class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Update Password")

    def validate_old_password(self, old_password):
        invalid_pass_check = bcrypt.check_password_hash(current_user.password, old_password.data)
        if not invalid_pass_check:
            raise ValidationError("Old Password didn't match")

    def validate_new_password(self, new_password):
        same_pass_check = bcrypt.check_password_hash(current_user.password, new_password.data)
        if same_pass_check:
            raise ValidationError("New Password is same is Old Password")


class UpdatePictureForm(FlaskForm):
    picture = FileField("Update Profile Pic", validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update Profile")


class BlogForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    image = FileField('Title Image', validators=[FileAllowed(['jpg', 'png'])])
    audio = FileField('Audio Blog', validators=[FileAllowed(['mp3', 'wav'])])
    video = FileField('Video Blog', validators=[FileAllowed(['mp4', 'wmv'])])
    submit = SubmitField("Publish Blog")