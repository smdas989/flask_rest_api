from flask import Blueprint
from blogapp.models import Post, token_required
from flask import jsonify

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
@token_required
def new_post(current_user):
    title = request.json.get('title')
    content = request.json.get('content') 
    post = Post(title=title, content=content, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    flash('Your post has been created','success')
    return {'title': title,'content':content}

@posts.route('/get_post', methods=['POST'])
@token_required
def get_post(current_user):
    id = request.json.get('id')
    return_value = Post.get_post(id)
    return jsonify(return_value)
    

@posts.route("/post/update", methods=['GET','POST'])
@token_required
def update_user_post(current_user):
    request_data = request.get_json()
    post = Post.query.get_or_404(request_data['id'])
    
    if post.user_id!= current_user:
        abort(403)

    Post.update_post(request_data['id'], request_data['title'], request_data['content'])    
    response = Response("Post Updated", status=200, mimetype='application/json')
    return response


@posts.route("/post/delete", methods=['POST'])
@token_required
def delete_post(current_user):
    request_data = request.get_json()
    post = Post.query.get_or_404(request_data['id'])

    if post.user_id != current_user:
        abort(403)	

    Post.delete_post(request_data['id'])    
    response = Response("Post deleted", status=200, mimetype='application/json')
    return response


@posts.route('/like/<int:post_id>/<action>')
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


@posts.route('/comment/<int:post_id>', methods=['GET', 'POST'])
@token_required
def comment(current_user, post_id=None):
    post = Post.query.get_or_404(post_id)
    request_data = request.get_json()
    
    comment = Comment(body=request_data['comment'].strip(), post_id=post_id, user_id = current_user.id)
    db.session.add(comment)
    db.session.commit()
    response = Response("Comment Added", status=200, mimetype='application/json')
    return response


@posts.route('/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
@token_required
def comment_delete(current_user, comment_id=None, post_id=None):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    response = Response("Comment Deleted", status=200, mimetype='application/json')
    return response

