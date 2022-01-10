from datetime import datetime
from blogapp import db, login_manager, app
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context
from functools import wraps
from flask import request, jsonify
import jwt
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    liked = db.relationship(
        'PostLike',
        foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')

    comment = db.relationship(
        'Comment',
        foreign_keys='Comment.user_id',
        backref='user', lazy='dynamic')

    
    followed = db.relationship('User', 
                               secondary=followers, 
                               primaryjoin=(followers.c.follower_id == id), 
                               secondaryjoin=(followers.c.followed_id == id), 
                               backref=db.backref('followers', lazy='dynamic'), 
                               lazy='dynamic')

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.date_posted.desc())

    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')

    # @staticmethod
    # def verify_reset_token(token):
    #     s = Serializer(app.config['SECRET_KEY'])
    #     try:
    #         user_id = s.loads(token)['user_id']
    #     except:
    #         return None
    #     return User.query.get(user_id)

    def json(self):
        return {'id': self.id, 'username': self.username,
                'email': self.email}

    
    def add_user(_username, _email, _password):
        '''function to add movie to database using _title, _year, _genre
        as parameters'''
        # creating an instance of our Movie constructor
        # if User.query.filter_by(username = _username).first() is not None:
		#     abort(400) # existing user
        user = User(username = _username, email = _email, password = _password)
        return user

    def get_all_users():
        '''function to get all movies in our database'''
        return [User.json(user) for user in User.query.all()]

    def get_user(_id):
        '''function to get movie using the id of the movie as parameter'''
        return [User.json(User.query.filter_by(id=_id).first())]

    # def update_user(_id, _title, _content):
    #     '''function to update the details of a movie using the id, title,
    #     year and genre as parameters'''
    #     user_to_update = User.query.filter_by(id=_id).first()
    #     user_to_update.title = _title
    #     user_to_update.content = _content
    #     db.session.commit()


    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user
    
    

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
        
class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    

    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='title', lazy='dynamic')

    def get_comments(self):
        return Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc())
    def json(self):
        return {'id': self.id, 'title': self.title,
                'content': self.content}

    def get_all_posts():
        return [Post.json(post) for post in Post.query.all()]


    def get_post(_id):
        return [Post.json(Post.query.filter_by(id=_id).first())]
    
    def update_post(_id, _title, _content):
        post_to_update = Post.query.filter_by(id=_id).first()
        post_to_update.title = _title
        post_to_update.content = _content
        db.session.commit()
    
    def delete_post(_id):
        post_to_update = Post.query.filter_by(id=_id).delete()
        db.session.commit()

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    body = db.Column(db.Text)
    
    def __repr__(self):
        return f"Comment('{self.body}')"

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator