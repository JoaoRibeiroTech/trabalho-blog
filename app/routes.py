from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Post, Comment, User
from datetime import datetime

bp = Blueprint('routes', __name__) 


@bp.route('/')
@bp.route('/index')
def index():
    
    posts = Post.query.order_by(Post.date_published.desc()).all()
    
    return jsonify({
        'message': 'Bem-vindo à API do Blog!', 
        'endpoints': {
            'posts': '/api/posts',
            'users': '/api/users',
            'comments': '/api/posts/<post_id>/comments',
            'auth': '/register, /login, /logout (via formulário) ou /api/register, /api/login (via JSON)'
        }
    })

@bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id) 
    
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.date_commented.asc()).all()
    
    
    return jsonify({
        'post': post.to_dict(),
        'comments': [comment.to_dict() for comment in comments]
    })

@bp.route('/create_post', methods=['GET', 'POST'])
@login_required 
def create_post_page():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        new_post = Post(title=title, content=content, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post criado com sucesso!', 'success')
        return redirect(url_for('routes.index'))
    
    
    return jsonify({'message': 'Rota para criar post via formulário (requer login). Use a API POST /api/posts para criar via JSON.'}), 405

@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required 
def edit_post_page(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        flash('Você não tem permissão para editar este post.', 'danger')
        return redirect(url_for('routes.view_post', post_id=post_id))
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Post atualizado com sucesso!', 'success')
        return redirect(url_for('routes.view_post', post_id=post_id))
    
    
    return jsonify({'message': f'Rota para editar post {post_id} via formulário (requer login e ser autor). Use a API PUT /api/posts/{post_id} para editar via JSON.'}), 405


@bp.route('/api/posts', methods=['GET'])
def api_get_posts():
    posts = Post.query.order_by(Post.date_published.desc()).all()
    posts_list = [post.to_dict() for post in posts] 
    return jsonify(posts_list)

@bp.route('/api/posts', methods=['POST'])
@login_required 
def api_create_post():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'message': 'Título e conteúdo do post são obrigatórios.'}), 400

    new_post = Post(
        title=data['title'],
        content=data['content'],
        user_id=current_user.id 
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201 

@bp.route('/api/posts/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())

@bp.route('/api/posts/<int:post_id>', methods=['PUT'])
@login_required
def api_update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        return jsonify({'message': 'Você não tem permissão para editar este post.'}), 403 

    data = request.get_json()
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    db.session.commit()
    return jsonify(post.to_dict())

@bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def api_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        return jsonify({'message': 'Você não tem permissão para deletar este post.'}), 403

    db.session.delete(post)
    db.session.commit()
    return '', 204 

@bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@login_required 
def api_add_comment_to_post(post_id):
    post = Post.query.get_or_404(post_id) 
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'message': 'Conteúdo do comentário é obrigatório.'}), 400

    new_comment = Comment(
        content=data['content'],
        user_id=current_user.id,
        post_id=post.id
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(new_comment.to_dict()), 201 

@bp.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def api_get_comments_for_post(post_id):
    post = Post.query.get_or_404(post_id) 
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.date_commented.asc()).all()
    comments_list = [comment.to_dict() for comment in comments]
    return jsonify(comments_list)


@bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def api_delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get(comment.post_id) 

    
    if comment.user_id != current_user.id and post.user_id != current_user.id:
        return jsonify({'message': 'Você não tem permissão para deletar este comentário.'}), 403

    db.session.delete(comment)
    db.session.commit()
    return '', 204 
@bp.route('/api/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    user = User.query.get_or_404(user_id)
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email, 
        'post_count': len(user.posts),
        'comment_count': len(user.comments)
    }
    return jsonify(user_data)