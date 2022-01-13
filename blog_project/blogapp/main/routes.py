from flask import Blueprint
from blogapp.models import Post, token_required
from flask import jsonify

main = Blueprint('main', __name__)

@main.route("/home")
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
    