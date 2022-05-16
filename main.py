# ---------------------------------- IMPORTS ----------------------------------
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, UserForm, LoginForm
from flask_gravatar import Gravatar


# -------------------------------- APP CONFIG ---------------------------------
app = Flask(__name__)                                                   # Flask App
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'           # Secret Key example
ckeditor = CKEditor(app)                                                # CKE Editor
Bootstrap(app)                                                          # Implementing Bootstrap


# ---------------------------------- DATABASE ---------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'             # SQL Database Path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False                    # Disabling outdated configs
db = SQLAlchemy(app)                                                    # App creation


# ----------------------------------- TABLES ----------------------------------
class BlogPost(db.Model):
    # BlogPost class, represents the post structure and it`s form of storage in the DB.
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class User(db.Model):
    # User class, represents the users registred to the blog and it's form of storage in the DB.
    __tablename__ = "usernames"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)


# Table Creation, run only once
# db.create_all()


# ---------------------------------- ROUTING ----------------------------------
@app.route('/')
def get_all_posts():

    # TODO - Figure out how to update the navbar so that when a user is not logged in it shows:
    #  HOME LOGIN REGISTER ABOUT CONTACT
    #  But if the user is logged in / authenticated after registering, then the navbar should show:
    #  HOME LOGOUT ABOUT CONTACT

    # Default routing, for when the user first accesses the Blog.
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():

    form = UserForm()

    if form.validate_on_submit():
        # If form is submitting (POST method), creates a new User object and appends it to the DB.

        # User Creation
        new_user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data, salt_length=8),
            name=form.name.data
        )

        db.session.add(new_user)        # Adding the new user to the DB
        db.session.commit()             # Commiting the change

        # TODO -  2. Add 1 line of code in the /register route so that when users successfully
        #  register they are taken back to the home page and are logged in with Flask-Login.

        # TODO - In the in the /register route, if a user is trying to register with an email
        #  that already exists in the database then they should be redirected to the /login
        #  route and a flash message used to tell them to log in with that email instead.

        return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=form)


@app.route('/login')
def login():
    # Logout routing, for when the user decides to connect to its blog account.

    form = LoginForm()
    # TODO - 1. Users who have been successfully registered (added to the user table in the database)
    #  should be able to go to the /login route to use their credentials to log in. You will need to
    #  review the Flask-Login docs and the lessons from yesterday to be able to do this.

    # TODO - In the /login route, if a user's email does not exist in the database or if their password
    #  does not match the one stored using check_password() then they should be redirected back to /login
    #  and a flash message should let them know what they issue was and ask them to try again.

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    # Logout routing, for when the user decides to disconnect its account from the blog.

    # TODO -  Code up the /logout route so that when the user clicks on the LOG OUT button,
    #  it logs them out and takes them back to the home page.

    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    # About routing, a simple description about the blog.
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post")
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# ---------------------------------- ROUTING ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
