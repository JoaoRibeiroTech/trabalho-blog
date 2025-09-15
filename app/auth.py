# app/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, login_manager
from app.models import Post, Comment, User

bp = Blueprint('auth', __name__) 


@bp.route('/register', methods=['GET', 'POST'])
def register():
    
    if current_user.is_authenticated:
        return redirect(url_for('routes.index')) 
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username ou Email já em uso.', 'danger') 
            return redirect(url_for('auth.register'))

        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Sua conta foi criada! Agora você pode logar.', 'success') 
        return redirect(url_for('auth.login')) 
        
    return render_template('register.html') 

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember') 

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember) 
            flash('Login bem-sucedido!', 'success')
            
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('routes.index'))
        else:
            flash('Login falhou. Verifique username e senha.', 'danger')
            
    return render_template('login.html') 

@bp.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('routes.index'))


@bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() 
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Campos obrigatórios não fornecidos (username, email, password).'}), 400

    user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
    if user_exists:
        return jsonify({'message': 'Username ou Email já está em uso.'}), 409 

    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    
    return jsonify({
        'message': 'Usuário criado com sucesso!', 
        'user_id': new_user.id,
        'username': new_user.username,
        'email': new_user.email
    }), 201 

@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username e senha são obrigatórios.'}), 400

    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
       
        return jsonify({'message': 'Login bem-sucedido!', 'user_id': user.id})
    else:
        return jsonify({'message': 'Credenciais inválidas.'}), 401 