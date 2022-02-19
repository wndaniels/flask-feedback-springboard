
from sqlite3 import IntegrityError
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import DeleteForm, RegisterUserForm, UserLoginForm, FeedbackForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "yupp1234"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def register_page():
    """ Show form for register/create user. """

    if 'username' in session:
        return redirect('/users/{username}')

    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append(
                "Username is not available, please pick another.")
            return render_template('/user/register.html', form=form)
        
        session['username'] = new_user.username
        # Flash welcome, and redirect user to the secret page.
        flash(f"Welcome {new_user.username}, your account has been created")
        return redirect(f'/users/{username}')
    else:
        return render_template('/user/register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_page():
    """ Show form for user login. """

    form = UserLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user: 
            session['username'] = user.username
            flash(f"Welcome back {user.username}!")
            return redirect(f'/users/{user.username}')

        else:
            form.username.errors = ['Invalide Username and/or Password']
            form.password.errors = ['Invalide Username and/or Password']
    return render_template('/user/login.html', form=form)



@app.route('/users/<username>')
def user_details(username):
    """ Render secret page. """

    if "username" not in session:
        flash("Please log-in first.")
        return redirect('/login')
    
    user = User.query.get_or_404(username)
    form = FeedbackForm()

    return render_template('/user/show_user.html', user=user, form=form)


@app.route('/logout')
def logout_user():
    """ Clear information from session and redirect to '/' """

    session.pop('username')
    flash("Goodbye!")

    return redirect('/')



@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user and redirect to login."""

    if "username" not in session or username != session['username']:
        flash("You must be logged in to perform this action.")
        return redirect('/')

    user = User.query.get(username)

    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/")


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """Show form to allow user to add new feedback to their account. """

    user = User.query.get_or_404(username)

    if "username" not in session or username != session['username']:
        flash("You must be logged in to perform this action.")
        return redirect('/')

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = session['username']
        new_feedback = Feedback.add_feedback(title, content, username)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/users/{user.username}')

    return render_template('/feedback/add.html', user=user, form=form)


@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """ Show form for user to update feedback. """
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        flash("You must be logged in to perform this action.")
        return redirect('/login')

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()

        return redirect(f'/users/{feedback.username}')
    
    return render_template('/feedback/update.html', form=form, feedback=feedback)


@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """ Allows user to delete specific feedback. """

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        flash("You must be logged in to perform this action.")
        return redirect('/login')

    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    
    return redirect(f'/users/{feedback.username}')
