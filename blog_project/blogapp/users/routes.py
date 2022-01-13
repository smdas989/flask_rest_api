from flask import Blueprint, request, Response, session
from blogapp.models import User, token_required
from flask import jsonify
from .forms import RegistrationForm
from email_validator import validate_email, EmailNotValidError
from blogapp import app, db, bcrypt, mail, celery
import jwt
import datetime
import os
from twilio.rest import Client
import random

users = Blueprint('users', __name__)

@users.route('/add_user', methods=['POST'])
def add_user():
    form = RegistrationForm.from_json(request.json)
    if not form.validate():
        error_message = f"Invalid input params : {form.errors}"
        response = Response(error_message, 201, mimetype='application/json') # missing arguments
        return response
       
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

@users.route('/get_all_user', methods=['GET'])
@token_required
def get_all_user(a):
    return_value = User.get_all_users()
    return jsonify(return_value)
    

@users.route('/get_user/<int:id>', methods=['GET'])
def get_user(id):
    return_value = User.get_user(id)
    return jsonify(return_value)
    

@users.route('/login', methods=['GET', 'POST'])  
def login_user(): 
 
    # auth = request.authorization  

    username = request.json.get('username')
    password = request.json.get('password') 

    if not username or not password:  
        # return jsonify({'message': 'could not verify'})
        
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

    user = User.query.filter_by(username=username).first()   
        
    # if check_password_hash(password, user.password):  
    token = jwt.encode({'public_id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=0.5)}, app.config['SECRET_KEY'])  
    return jsonify({'token' : token.decode('UTF-8')}) 

    
    # return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


@users.route('/list_of_followers/<username>')
@token_required
def followers(current_user, username):
    user = User.query.filter_by(username=username).first_or_404()
    user_followers = user.followers.all()
    response = {
        'status': 'success',
        'message': 'Your followers list is: ' + str(user_followers) + '.'
    } 
    return response



@users.route('/follow/<username>')
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

@users.route('/unfollow/<username>')
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



@users.route('/getotp')
def getOTP():
    account_sid = "AC591c551e52e599dcea44d133aaf2d205"
    auth_token = "5fb6d9734350336a6d78ed569076bdfb"
    otp = random.randrange(100000,999999) #generate OTP
    session['response'] = otp
    client = Client(account_sid, auth_token)
    number = "+917069203949"
    message = client.messages \
                    .create(
                        body="Your OTP is"+str(otp),
                        from_='+19402897509',
                        to=number
                    )

    if message.sid:
        response = Response("OTP sent to "+number, status=200, mimetype='application/json')
        return response
    else:
        response = Response("Error in sending OTP to "+number, status=200, mimetype='application/json')
        return response
    

@users.route('/verifyotp',  methods=['POST'])
def verifyOTP():
    otp = request.json.get('otp')
    if "response" in session:
        s = session['response']
        session.pop('response', None)
        if s == otp:
            response = Response("You are authorise", status=200, mimetype='application/json')
            return response
        else:
            response = Response("You are not authorised", status=200, mimetype='application/json')
            return response
    response = Response("OTP expired or not generated", status=200, mimetype='application/json')
    return response