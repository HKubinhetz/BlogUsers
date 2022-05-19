from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class UserForm(FlaskForm):
    email = StringField("Your email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Your name", validators=[DataRequired()])
    submit = SubmitField("Create User")


class LoginForm(FlaskForm):
    email = StringField("Your email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Enter")


# TODO - Create a Comment Form
class CommentForm(FlaskForm):
    comment = CKEditorField("Your email", validators=[DataRequired()])
    submit = SubmitField("Post Comment")
