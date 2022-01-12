from flask import flash, redirect, render_template, url_for, request, json, jsonify, Response, abort, g, make_response
from blogapp import app, db, bcrypt, mail, celery
from flask.views import View
from flask.views import MethodView
from blogapp.models import User, Post, token_required, Comment
import secrets
import os
from datetime import datetime
from sqlalchemy import func
from flask_restplus import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
import jwt
import datetime
from email_validator import validate_email, EmailNotValidError

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    if username is None or password is None:
        response = Response("Enter Username and password", 201, mimetype='application/json') # missing arguments
        return response

    try:
        # Validate.
        validate_email(email)
        
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        response = Response(str(e), 201, mimetype='application/json')
        return response
        
    
    users = User.query.all()
    for user in users:
        if user.email == email:
            response = Response("Email is already taken", 201, mimetype='application/json')
            return response # Unique email id
        if user.username == username:
            response = Response("Username is already taken", 201, mimetype='application/json')
            return response # Unique username id
    
    user = User.add_user(username, email, password)

    
    # user = User(username = username)
    # user.hash_password(password)
    if user:
        db.session.add(user)
        db.session.commit()
    
        response = Response("User added Successfully" + "\n username:" + username + "\n email:" + email, 201, mimetype='application/json')
    
    else:
        response = Response("User registration failed", 404, mimetype='application/json')
    return response

@app.route('/get_all_user', methods=['GET'])
def get_all_user():
    return_value = User.get_all_users()
    return jsonify(return_value)
    

@app.route('/get_user/<int:id>', methods=['GET'])
def get_user(id):
    return_value = User.get_user(id)
    return jsonify(return_value)
    

@app.route('/login', methods=['GET', 'POST'])  
def login_user(): 
 
    # auth = request.authorization  

    username = request.json.get('username')
    password = request.json.get('password') 

    if not username or not password:  
        # return jsonify({'message': 'could not verify'})
        
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

    user = User.query.filter_by(username=username).first()   
        
    # if check_password_hash(password, user.password):  
    token = jwt.encode({'public_id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
    return jsonify({'token' : token.decode('UTF-8')}) 

    
    # return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


# @app.route("/")
@app.route("/home")
@token_required
def home(current_user):
    # posts = Post.query.order_by(Post.date_posted.desc())

    # search_post = request.args.get('search_post')
    # if search_post:
    #     search_post = search_post.strip()

    # sort_by = request.json.get('sort_by')

    return_value = Post.get_all_posts()

    return jsonify({"posts":return_value,
    "sort_by":request.json.get('sort_by')
    }) 

    # if search_post and sort_by:
    #     posts = Post.query.filter(Post.title.ilike('%' + search_post + '%'))

    #     if sort_by == 'oldest':
    #         posts = posts.order_by(Post.date_posted).paginate(page=page, per_page=5)
    #     elif sort_by == 'most_liked':
    #         posts = posts.outerjoin(PostLike).group_by(Post.id).order_by(func.count().desc(), Post.date_posted.desc()).paginate(page=page, per_page=5)
    #     elif sort_by == 'newest':
    #         posts = posts.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
           
    # elif search_post:
    #     posts = Post.query.filter(Post.title.ilike('%' + search_post + '%')).paginate(page, per_page=5)
    
    # if sort_by:
    #     if sort_by == 'oldest':
    #         posts = Post.query.order_by(Post.date_posted)
    #     # elif sort_by == 'most_liked':
    #     #     posts = Post.query.outerjoin(PostLike).group_by(Post.id).order_by(func.count().desc(), Post.date_posted.desc()).paginate(page=page, per_page=5)
    #     elif sort_by == 'newest':
    #         posts = posts = Post.query.order_by(Post.date_posted.desc())
    
    
@app.route("/post/new", methods=['GET', 'POST'])
@token_required
def new_post(current_user):
    title = request.json.get('title')
    content = request.json.get('content') 
    post = Post(title=title, content=content, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    flash('Your post has been created','success')
    return {'title': title,'content':content}

@app.route('/get_post', methods=['POST'])
@token_required
def get_post(current_user):
    id = request.json.get('id')
    return_value = Post.get_post(id)
    return jsonify(return_value)
    

@app.route("/post/update", methods=['GET','POST'])
@token_required
def update_user_post(current_user):
    request_data = request.get_json()
    post = Post.query.get_or_404(request_data['id'])
    
    if post.user_id!= current_user:
        abort(403)

    Post.update_post(request_data['id'], request_data['title'], request_data['content'])    
    response = Response("Post Updated", status=200, mimetype='application/json')
    return response


@app.route("/post/delete", methods=['POST'])
@token_required
def delete_post(current_user):
    request_data = request.get_json()
    post = Post.query.get_or_404(request_data['id'])

    if post.user_id != current_user:
        abort(403)	

    Post.delete_post(request_data['id'])    
    response = Response("Post deleted", status=200, mimetype='application/json')
    return response


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

@app.route('/like/<int:post_id>/<action>')
@token_required
def like_action(current_user, post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    msg=''
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
        msg = "Successfully like the post"
    
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
        msg = "Successfully unlike the post"
    
    return {'msg': msg,
            'user':current_user.username,
            'post':post.title
            }


@app.route('/comment/<int:post_id>', methods=['GET', 'POST'])
@token_required
def comment(current_user, post_id=None):
    post = Post.query.get_or_404(post_id)
    request_data = request.get_json()
    
    comment = Comment(body=request_data['comment'].strip(), post_id=post_id, user_id = current_user.id)
    db.session.add(comment)
    db.session.commit()
    response = Response("Comment Added", status=200, mimetype='application/json')
    return response


@app.route('/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
@token_required
def comment_delete(current_user, comment_id=None, post_id=None):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    response = Response("Comment Deleted", status=200, mimetype='application/json')
    return response


@app.route('/follow/<username>')
@token_required
def follow(current_user, username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        Response('User %s not found.' % username, status=404, mimetype='application/json')
    if user == current_user:
        Response('You can\'t follow yourself!', status=404, mimetype='application/json')

    u = current_user.follow(user)
    if u is None:
        Response('Cannot follow ' + username + '.', status=404, mimetype='application/json')
        
    db.session.add(u)
    db.session.commit()
    response = Response("You are now following "+username, status=200, mimetype='application/json')
    return response

@app.route('/unfollow/<username>')
@token_required
def unfollow(current_user, username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        Response('User %s not found.' % username, status=404, mimetype='application/json')
    if user == current_user:
        Response('You can\'t unfollow yourself!', status=404, mimetype='application/json')
    u = current_user.unfollow(user)
    if u is None:
        Response('Cannot unfollow ' + username + '.', status=404, mimetype='application/json')
    db.session.add(u)
    db.session.commit()
    response = Response("You have successfully unfollowed "+username, status=200, mimetype='application/json')
    return response

# @app.route('/feed')
# @login_required
# def feed():
#     page = request.args.get('page', 1, type=int)
#     posts = current_user.followed_posts().paginate(page=page, per_page=5)
#     return render_template("feed.html", posts=posts)

@app.route('/list_of_followers/<username>')
@token_required
def followers(current_user, username):
    user = User.query.filter_by(username=username).first_or_404()
    user_followers = user.followers.all()
    response = {
        'status': 'success',
        'message': 'Your followers list is: ' + str(user_followers) + '.'
    } 
    return response


# @app.route('/following')
# @token_required
# def following():
#     return render_template("following.html")
