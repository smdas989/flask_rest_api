# from flask import flash, redirect, render_template, url_for, request, json, jsonify, Response, abort, g, make_response
# from blogapp import app, db, bcrypt, mail, celery
# from flask.views import View
# from flask.views import MethodView
# from blogapp.models import User, Post, token_required, Comment
# import secrets
# import os
# from datetime import datetime
# from sqlalchemy import func
# from flask_restplus import Resource, Api
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_httpauth import HTTPBasicAuth
# import jwt
# import datetime
# from email_validator import validate_email, EmailNotValidError






# @app.route("/post/<int:post_id>", methods=['GET','POST'])
# def post(post_id):
#     form = CommentForm()
#     post = Post.query.get_or_404(post_id)
#     comments = Comment.query.filter_by(post_id=post_id).all()
#     if len(comments) == 0:
#         comments=None
#     return render_template('post.html', title=post.title, post=post, comments=comments, form=form)



# @app.route("/user/<string:username>")
# def user_posts(username):
#     page = request.args.get('page', 1, type=int)
#     user = User.query.filter_by(username=username).first_or_404()
#     posts = Post.query.filter_by(author=user)\
#         .order_by(Post.date_posted.desc())\
#         .paginate(page=page, per_page=5)
#     return render_template('user_posts.html', posts=posts, user=user)



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



# @app.route('/feed')
# @login_required
# def feed():
#     page = request.args.get('page', 1, type=int)
#     posts = current_user.followed_posts().paginate(page=page, per_page=5)
#     return render_template("feed.html", posts=posts)



# @app.route('/following')
# @token_required
# def following():
#     return render_template("following.html")
