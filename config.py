class Config:
    SECRET_KEY = 'your-secret-key-here'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # CELERY_BROKER_URL = 'redis://redis'  # In case of using docker
    # CELERY_RESULT_BACKEND = 'redis://redis' # In case of using docker

    DB_HOST = 'localhost'
    # DB_HOST = 'mariadb' # In case of using docker
    DB_USER = 'app'
    DB_PASSWORD = 'password123'
    DB_NAME = 'companies'
    DB_PORT = 3306