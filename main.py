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


# ----------------------------------- TABLES ----------------------------------
class Comment(db.Model):
    # Comment class, represents the comment structure and it`s form of storage in the DB.
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('usernames.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))


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
    parent_id = db.Column(db.Integer, db.ForeignKey('usernames.id'))
    children_comments = relationship(Comment)


class User(db.Model, UserMixin):
    # User class, represents the users registred to the blog and it's form of storage in the DB.
    __tablename__ = "usernames"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    children_posts = relationship(BlogPost)
    children_comments = relationship(Comment)


# Table Creation, run only once
# db.create_all()


# --------------------------------- FUNCTIONS ---------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def admin_only(f):
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
            flash("Username already exists! Please login instead!")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    # Login routing, for when the user decides to connect to its blog account.

    form = LoginForm()

    if form.validate_on_submit():
        login_mail = form.email.data

        selected_user = db.session.query(User).filter_by(email=login_mail).first()
        print(selected_user)
        if selected_user is None:
            # If the email does not exist:
            flash("Username not found", "error")
            return render_template("login.html", form=form)
        else:
            print("Login! But let's check that password first")
            password_check = check_password_hash(selected_user.password, form.password.data)
            print(f"Password Status: {password_check}")
            if password_check:
                print("Login Success!")
                login_user(selected_user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Bad password!", "error")
                return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    # Logout routing, for when the user decides to disconnect its account from the blog.
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)

    # TODO - Update the code in post.html to display all the comments associated with the blog post.
    #  HINT 1: Don't worry about the commenter image just yet.
    #  HINT 2: comments is a property of each blog post, you can treat it like a List.
    #  HINT 3: The text of each comment is created from the CKEditor just like the body
    #  of each blog post so it will be saved in HTML format.

    # TODO - Implement https://pythonhosted.org/Flask-Gravatar/

    form = CommentForm()

    if form.validate_on_submit():
        comment = form.comment.data
        print(comment)

        if current_user.is_authenticated:
            print("Top!")
            # TODO - Salvar no DB, Redirecionar ao Post de novo
        else:
            print("Precisa Logar")
            flash("Please Login or Register to Comment!")
            return redirect(url_for("login"))

    return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    # About routing, a simple description about the blog.
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.name,
            date=date.today().strftime("%B %d, %Y"),
            parent_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
@admin_only
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
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# ---------------------------------- ROUTING ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
