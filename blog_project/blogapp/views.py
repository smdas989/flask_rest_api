from flask import flash, redirect, render_template, url_for, request, json, jsonify, Response
from blogapp import app, db, bcrypt, mail, celery, api
from flask.views import View
from flask.views import MethodView
# from .forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm,  RequestResetForm, ResetPasswordForm, CommentForm
from blogapp.models import User
# from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
# from PIL import Image
# from flask_paginate import Pagination, get_page_parameter
# from flask_mail import Message
from datetime import datetime
from sqlalchemy import func
from flask_restplus import Resource, Api

name_space = api.namespace('main', description='Main APIs')

@name_space.route("/")
class User(Resource):
    def get(self):
        return_value = User.get_user(id)
        return jsonify(return_value)
    
	def post(self):
		request_data = request.get_json()  # getting data from client
		User.add_user(request_data["username"], request_data["email"],
						request_data["password"])
		response = Response("User added", 201, mimetype='application/json')
		return response




# @api.route('/hello')
# class HelloWorld(Resource):
#     def get(self):
#         return {'hello': 'world'}

# @app.route("/")
# @app.route("/home")
# def home():
#     page = request.args.get('page', 1, type=int)
#     posts = posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

#     search_post = request.args.get('search_post')
#     if search_post:
#         search_post = search_post.strip()

#     sort_by = request.args.get('sort_by')
    
#     if search_post and sort_by:
#         posts = Post.query.filter(Post.title.ilike('%' + search_post + '%'))

#         if sort_by == 'oldest':
#             posts = posts.order_by(Post.date_posted).paginate(page=page, per_page=5)
#         elif sort_by == 'most_liked':
#             posts = posts.outerjoin(PostLike).group_by(Post.id).order_by(func.count().desc(), Post.date_posted.desc()).paginate(page=page, per_page=5)
#         elif sort_by == 'newest':
#             posts = posts.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
           
#     elif search_post:
#         posts = Post.query.filter(Post.title.ilike('%' + search_post + '%')).paginate(page, per_page=5)
    
#     elif sort_by:
#         if sort_by == 'oldest':
#             posts = Post.query.order_by(Post.date_posted).paginate(page=page, per_page=5)
#         elif sort_by == 'most_liked':
#             posts = Post.query.outerjoin(PostLike).group_by(Post.id).order_by(func.count().desc(), Post.date_posted.desc()).paginate(page=page, per_page=5)
#         elif sort_by == 'newest':
#             posts = posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
#     return render_template('home.html', posts=posts, sort_by=sort_by, search_post=search_post)


# @app.route("/about")
# def about():
#     return render_template('about.html', title='About')


# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#         flash('Your account has been created! You are now able to log in', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user, remember=form.remember.data)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('home'))
#         else:
#             flash('Login Unsuccessful. Please check email and password', 'danger')
#     return render_template('login.html', title='Login', form=form)


# @app.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for('home'))

# def save_picture(form_picture):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_hex + f_ext
#     picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
#     form_picture.save(picture_path)
#     output_size = (125, 125)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)
#     return picture_fn

# @app.route("/account", methods=['GET', 'POST'] )
# @login_required
# def account():
#     form = UpdateAccountForm()
#     if form.validate_on_submit():
#         if form.picture.data:
#             picture_file = save_picture(form.picture.data)
#             current_user.image_file = picture_file
#         current_user.username = form.username.data
#         current_user.email = form.email.data
#         db.session.commit()
#         flash('Your account has been updated','success')
#         return redirect(url_for('account'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.email.data = current_user.email
#     image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
#     return render_template('account.html', title='Account', image_file=image_file, form=form)


# @app.route("/post/new", methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()
#     if form.validate_on_submit():
#         post = Post(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created','success')
#         return redirect(url_for('home'))
#     return render_template('create_post.html', title='New Post', form=form,  legend='New Post')

# @app.route("/post/<int:post_id>", methods=['GET','POST'])
# def post(post_id):
#     form = CommentForm()
#     post = Post.query.get_or_404(post_id)
#     comments = Comment.query.filter_by(post_id=post_id).all()
#     if len(comments) == 0:
#         comments=None
#     return render_template('post.html', title=post.title, post=post, comments=comments, form=form)

# @app.route("/post/<int:post_id>/update", methods=['GET','POST'])
# @login_required
# def update_post(post_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author!= current_user:
#         abort(403)
#     form = PostForm()
#     if form.validate_on_submit():
#         post.title = form.title.data
#         post.content = form.content.data
#         post.date_updated = datetime.now()
#         db.session.commit()
#         flash('Your post has been updated','success')
#         return redirect(url_for('post',post_id=post.id))
#     elif request.method == 'GET':
#         form.title.data = post.title
#         form.content.data = post.content
#     return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


# @app.route("/post/<int:post_id>/delete", methods=['POST'])
# @login_required
# def delete_post(post_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author != current_user:
#         abort(403)
#     db.session.delete(post)
#     db.session.commit()
#     flash('Your post has been deleted!', 'success')
#     return redirect(url_for('home'))

# @app.route("/user/<string:username>")
# def user_posts(username):
#     page = request.args.get('page', 1, type=int)
#     user = User.query.filter_by(username=username).first_or_404()
#     posts = Post.query.filter_by(author=user)\
#         .order_by(Post.date_posted.desc())\
#         .paginate(page=page, per_page=5)
#     return render_template('user_posts.html', posts=posts, user=user)

# @app.route("/process/<name>", methods=['GET', 'POST'])
# def process(name):
#     reverse.delay(name)
#     return "ASYNC"

# @celery.task
# def reverse(string):
#     print("New")
#     return string[::-1]


# @celery.task
# def send_reset_email(email):
#     with app.app_context():
#         user = User.query.filter_by(email=email).first()
#         token = user.get_reset_token()

#         msg = Message("Password Reset Request!",
#                     sender="smdas989@gmail.com",
#                     recipients=[user.email])
#         msg.body = f'''To reset your password, visit the following link:
#         {url_for('reset_token', token=token, _external=True)}
#         If you did not make this request then simply ignore this email and no changes will be made.
#         '''
#         mail.send(msg)
    

# @app.route("/reset_password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         email = user.email
#         send_reset_email.delay(email)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('login'))
#     return render_template('reset_request.html', title='Reset Password', form=form)


# @app.route("/reset_password/<token>", methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     user = User.verify_reset_token(token)
#     if user is None:
#         flash('That is an invalid or expired token', 'warning')
#         return redirect(url_for('reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()
#         flash('Your password has been updated! You are now able to log in', 'success')
#         return redirect(url_for('login'))
#     return render_template('reset_token.html', title='Reset Password', form=form)

# @app.route('/like/<int:post_id>/<action>')
# @login_required
# def like_action(post_id, action):
#     post = Post.query.filter_by(id=post_id).first_or_404()
    
#     if action == 'like':
#         current_user.like_post(post)
#         db.session.commit()
#     if action == 'unlike':
#         current_user.unlike_post(post)
#         db.session.commit()
#     return redirect(request.referrer)


# @app.route('/comment/<int:post_id>', methods=['GET', 'POST'])
# @login_required
# def comment(post_id=None):
#     post = Post.query.get_or_404(post_id)
#     form = CommentForm()
#     if form.validate_on_submit():
#         comment = Comment(body=form.content.data.strip(), post_id=post_id, user_id = current_user.id)
#         db.session.add(comment)
#         db.session.commit()
#         return redirect(url_for('post', post_id=post.id))
#     return render_template("post.html", post=post, form=form)

# @app.route('/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
# @login_required
# def comment_delete(comment_id=None, post_id=None):
#     comment = Comment.query.get_or_404(comment_id)
#     db.session.delete(comment)
#     db.session.commit()
#     flash('Your comment has been deleted!', 'success')
#     return redirect(request.referrer)


# @app.route('/profile/<int:user_id>', methods=['GET'])
# @login_required
# def user_profile(user_id=None):
#     user = User.query.get_or_404(user_id)
#     return render_template("profile.html", user=user)

# @app.route('/follow/<username>')
# @login_required
# def follow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User %s not found.' % username)
#         return redirect(url_for('home'))
#     if user == current_user:
#         flash('You can\'t follow yourself!')
#         return redirect(url_for('user_profile', user_id=user.id))
#     u = current_user.follow(user)
#     if u is None:
#         flash('Cannot follow ' + username + '.')
#         return redirect(url_for('user', user_id=user.id))
#     db.session.add(u)
#     db.session.commit()
#     flash('You are now following ' + username + '!',  'success')
#     return redirect(url_for('user_profile', user_id=user.id))

# @app.route('/unfollow/<username>')
# @login_required
# def unfollow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User %s not found.' % username)
#         return redirect(url_for('home'))
#     if user == current_user:
#         flash('You can\'t unfollow yourself!')
#         return redirect(url_for('user_profile', user_id=user.id))
#     u = current_user.unfollow(user)
#     if u is None:
#         flash('Cannot unfollow ' + username + '.')
#         return redirect(url_for('user_profile', user_id=user.id))
#     db.session.add(u)
#     db.session.commit()
#     flash('You have stopped following ' + username + '.', 'danger')
#     return redirect(url_for('user_profile', user_id=user.id))


# @app.route('/feed')
# @login_required
# def feed():
#     page = request.args.get('page', 1, type=int)
#     posts = current_user.followed_posts().paginate(page=page, per_page=5)
#     return render_template("feed.html", posts=posts)

# @app.route('/followers')
# @login_required
# def followers():
#     return render_template("followers.html")


# @app.route('/following')
# @login_required
# def following():
#     return render_template("following.html")

# class HelloWorld(Resource):
#     def get(self):
#         return {'hello': 'world'}

# api.add_resource(HelloWorld, '/api')