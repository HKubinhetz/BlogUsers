# ---------------------------------- IMPORTS ----------------------------------
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm
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


# Table Creation, run only once
# db.create_all()


# ---------------------------------- ROUTING ----------------------------------
@app.route('/')
def get_all_posts():
    # Default routing, for when the user first accesses the Blog.
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register')
def register():

    # TODO - Use what you've learnt yesterday to allow users to go to the /register route
    #  to sign up to your blog website. You should create a WTForm in forms.py called
    #  RegisterForm and use Flask-Bootstrap to render a wtf quick_form.
    #
    # TODO - The data the user entered should be used to create a new entry in your blog.db in a User table.
    #
    # TODO - HINT 1: You don't need to change anything in register.html
    #
    # TODO - HINT 2: Don't worry about Flask-Login yet, you are just creating a
    #  new user in the database. We'll log them in in the next step.

    return render_template("register.html")


@app.route('/login')
def login():
    # Logout routing, for when the user decides to connect to its blog account.
    return render_template("login.html")


@app.route('/logout')
def logout():
    # Logout routing, for when the user decides to disconnect its account from the blog.
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
