import os

class Config:
    # Параметры подключения к PostgreSQL
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'your_database_name')
    DB_USER = os.environ.get('DB_USER', 'your_username')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_password')
    
    # Для psycopg3 используем postgresql+psycopg
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
