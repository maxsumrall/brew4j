from .models import User, get_todays_recent_reviews, all_styles
from flask import Flask, request, session, redirect, url_for, render_template, flash, make_response
from avatar_generator import Avatar

app = Flask(__name__)


@app.route('/')
def index():
    reviews = get_todays_recent_reviews()
    return render_template('index.html', reviews=reviews)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            flash('Your username must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif not User(username).register(password):
            flash('A user with that username already exists.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))


@app.route('/add_review', methods=['POST'])
def add_review():
    title = request.form['title']
    text = request.form['text']
    beerId = request.form['beerId']

    if not text or not beerId:
        if not text:
            flash('You must give your review a text body.')
        if not beerId:
            flash('You must specify a beer to review')
    else:
        User(session['username']).add_review(text, beerId)

    return redirect(url_for('index'))


@app.route('/like_beer/<beer_id>')
def like_beer(beer_id):
    username = session.get('username')

    if not username:
        flash('You must be logged in to like a beer.')
        return redirect(url_for('login'))

    User(username).like_beer(beer_id)

    flash('Liked beer.')
    return redirect(request.referrer)

@app.route("/avatar/<username>")
def avatar(username):
    avatar = Avatar.generate(128, username)
    headers = { 'Content-Type': 'image/png' }
    return make_response(avatar, 200, headers)

@app.route('/friends/<username>')
def friends(username):
    logged_in_username = session.get('username')
    user_being_viewed = User(username)
    friends = user_being_viewed.get_friends()

    return render_template(
        'friends.html',
        username=username,
        friends=friends,
    )

@app.route('/styles')
def styles():
    styles = all_styles()

    return render_template(
        'styles.html',
        styles=styles,
    )


@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = User(user_being_viewed_username)
    reviews = user_being_viewed.get_recent_reviews()

    similar = []
    common = []

    if logged_in_username:
        logged_in_user = User(logged_in_username)

        if logged_in_user.username == user_being_viewed.username:
            similar = logged_in_user.get_similar_users()
        else:
            common = logged_in_user.get_commonality_of_user(user_being_viewed)

    return render_template(
        'profile.html',
        username=username,
        reviews=reviews,
        similar=similar,
        common=common
    )
