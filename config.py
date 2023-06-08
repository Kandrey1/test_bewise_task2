import os
from pathlib import Path

from dotenv import load_dotenv

basedir = Path(".")

load_dotenv()


class ConfigDevelopment(object):
    DEBUG = True
    TRAP_HTTP_EXCEPTIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DB_URL = 'postgresql+psycopg2://{user}:{psw}@{url}/{db}'.format(
        user=os.environ.get('POSTGRES_USER'),
        psw=os.environ.get('POSTGRES_PASSWORD'),
        url=f"{os.environ.get('POSTGRES_HOSTNAME')}:"
            f"{os.environ.get('POSTGRES_PORT')}",
        db=os.environ.get('POSTGRES_DB'))

    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # путь сохранения файлов
    UPLOAD_FOLDER = basedir / 'data' / 'audio'
    UPLOAD_FOLDER_TMP = basedir / 'data'/'audio'/'tmp'

    # разрешенные расширения для загрузки
    ALLOWED_EXTENSIONS = {'wav'}
    # максимальный размер файла для загрузки
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
