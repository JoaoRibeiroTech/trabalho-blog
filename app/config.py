# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-bem-difícil-de-adivinhar-e-nunca-use-essa-em-produção'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'blog.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False