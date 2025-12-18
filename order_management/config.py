import os

class Config:
    # Выбор узла базы данных в зависимости от переменной окружения
    NODE = os.getenv('NODE', 'shop1')
    
    # Настройки подключения для разных узлов
    DATABASE_CONFIGS = {
        'administration': {
            'host': 'localhost',
            'port': 5000,
            'user': 'admin',
            'password': 'pass',
            'database': 'vinlab'
        },
        'shop1': {
            'host': 'localhost',
            'port': 5001,
            'user': 'shop1',
            'password': 'pass',
            'database': 'vinlab'
        },
        'shop2': {
            'host': 'localhost',
            'port': 5002,
            'user': 'shop2',
            'password': 'pass',
            'database': 'vinlab'
        },
        'warehouse1': {
            'host': 'localhost',
            'port': 5011,
            'user': 'warehouse1',
            'password': 'pass',
            'database': 'vinlab'
        },
        'warehouse2': {
            'host': 'localhost',
            'port': 5012,
            'user': 'warehouse2',
            'password': 'pass',
            'database': 'vinlab'
        }
    }
    
    # Формирование строки подключения
    db_config = DATABASE_CONFIGS[NODE]
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-here-change-in-production'
