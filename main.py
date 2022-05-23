# ---------------------------------- IMPORTS ----------------------------------
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, UserForm, LoginForm, CommentForm
from sqlalchemy.exc import IntegrityError
from functools import wraps
from flask_gravatar import Gravatar


# -------------------------------- APP CONFIG ---------------------------------
app = Flask(__name__)                                                   # Flask App
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'           # Secret Key example
ckeditor = CKEditor(app)                                                # CKE Editor
Bootstrap(app)                                                          # Implementing Bootstrap
login_manager = LoginManager()                                          # Creating Login Object
login_manager.init_app(app)                                             # Initializing Login Object


# ---------------------------------- DATABASE ---------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'             # SQL Database Path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False                    # Disabling outdated configs
db = SQLAlchemy(app)                                                    # App creation


# ---------------------------------- GRAVATAR ---------------------------------
# This is the section dedicated on building the gravatar app, responsible for user' profile pictures.
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# ----------------------------------- TABLES ----------------------------------
class User(UserMixin, db.Model):
    # User class, for manipulating users and saving those to the Database.
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    # BlogPost class, for building the main content of the blog and storing.
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    # Comment class, for comments and relationship to authors.
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


# Table Creation, run only once
# db.create_all()


# --------------------------------- FUNCTIONS ---------------------------------
@login_manager.user_loader
def load_user(user_id):
    # This is a default function used in flask login.
    return User.query.get(user_id)


def admin_only(f):
    # This function is used to restrict access to admin-only pages.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() != str(1):
            abort(403)
        else:
            return f(*args, **kwargs)
    return decorated_function


# ---------------------------------- ROUTING ----------------------------------
@app.route('/')
def get_all_posts():
    # Default routing, for when the user first accesses the Blog.
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    # Register routing, for when a new user wishes to join the website.
    form = UserForm()

    if form.validate_on_submit():
        # If form is submitting (POST method), creates a new User object and appends it to the DB.

        # User Creation
        new_user = User()
        new_user.email = form.email.data
        new_user.password = generate_password_hash(form.password.data, salt_length=8)
        new_user.name = form.name.data

        try:
            db.session.add(new_user)        # Adding the new user to the DB
            db.session.commit()             # Commiting the change

            login_user(new_user)
            return redirect(url_for("get_all_posts"))

        except IntegrityError:
            # If IntegrityError happens, the username already exists.
            # In that case, the user is redirected to the login page.
            flash("Username already exists! Please login instead!")
            return redirect(url_for("login"))

    # If the page is loading (GET method), the register form is loaded.
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    # Login routing, for when the user decides to connect to its blog account.

    form = LoginForm()

    if form.validate_on_submit():
        # If form is submitting (POST method), the server tries to perform a login operation.
        login_mail = form.email.data

        selected_user = db.session.query(User).filter_by(email=login_mail).first()
        print(selected_user)

        if selected_user is None:
            # If the email does not exist, the server returns an error to the user.
            flash("Username not found", "error")
            return render_template("login.html", form=form)

        else:
            # If the e-mail exists, it is time to check for password matching.
            password_check = check_password_hash(selected_user.password, form.password.data)

            if password_check:
                # If the password checks out, the server logs the user in.
                login_user(selected_user)
                return redirect(url_for("get_all_posts"))
            else:
                # If the password is wrong, the server returns an error to the user.
                flash("Bad password!", "error")
                return render_template("login.html", form=form)

    # If the page is loading (GET method), the login form is loaded.
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    # Logout routing, for when the user decides to disconnect its account from the blog.
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    # Show post routing, for when the user clicks on a post.
    # It consists of showing the selected post and all its comments.

    # Fetching post and its comments.
    requested_post = BlogPost.query.get(post_id)
    post_comments = db.session.query(Comment).filter_by(post_id=post_id).all()

    # Comment form for new comments
    form = CommentForm()

    if form.validate_on_submit():
        # If form is submitting (POST method), the server tries to save a new comment.
        comment = form.comment.data

        if current_user.is_authenticated:
            # The comment is posted only if the current user is authenticated.

            # Building a Comment object
            new_comment = Comment(
                text=comment,
                parent_post=requested_post,
                comment_author=current_user
            )

            db.session.add(new_comment)     # Adding the new comment to the Database
            db.session.commit()             # Saving the changes

            # Fetching all comments for that specific post again to include the new comment
            # and refresh the page.
            post_comments = db.session.query(Comment).filter_by(post_id=post_id).all()
            return render_template("post.html", post=requested_post, form=form, comments=post_comments)

        else:
            # If the user isnt' authenticated, it is directed to the login page.
            flash("Please Login or Register to Comment!")
            return redirect(url_for("login"))

    # If the page is loading (GET method), the post is loaded.
    return render_template("post.html", post=requested_post, form=form, comments=post_comments)


@app.route("/about")
def about():
    # About routing, a simple description about the blog.
    return render_template("about.html")


@app.route("/contact")
def contact():
    # Contact routing, a simple page with contact information.
    return render_template("contact.html")


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    # Add new post routing, for when a user with admin privileges
    # decides to post new content.

    # Loading form
    form = CreatePostForm()

    if form.validate_on_submit():
        # If form is submitting (POST method), the server tries to save a new post.

        # Creation of a BlogPost object
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
            author_id=current_user.id
        )

        db.session.add(new_post)                        # Adding the new post to the database
        db.session.commit()                             # Commiting the change
        return redirect(url_for("get_all_posts"))       # Redirecting the user to the homepage

    # If the page is loading (GET method), the create post page is loaded.
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
@admin_only
def edit_post(post_id):
    # Edit Post routing, for when a user with admin privileges wishes to
    # change any of the post information (except its original posting date).

    # Fetching the existing post from the database.
    post = BlogPost.query.get(post_id)

    # Creating the post object with existing information from the DB.
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )

    if edit_form.validate_on_submit():
        # If form is submitting (POST method), the server saves the edited post.
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data

        # Saving the edited post in the database.
        db.session.commit()

        # Redirecting the user for the edited post page as a reader.
        return redirect(url_for("show_post", post_id=post.id))

    # If the page is loading (GET method), the edit post page is loaded.
    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    # Delete post routing, for when a user with admin privileges
    # decides to delete a post.

    post_to_delete = BlogPost.query.get(post_id)        # Selecting post to delete
    db.session.delete(post_to_delete)                   # Deleting the post
    db.session.commit()                                 # Commiting the change
    return redirect(url_for('get_all_posts'))           # Redirecting the user to the homepage


# ---------------------------------- ROUTING ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
