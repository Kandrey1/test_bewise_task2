import json
import os
from pathlib import Path

from uuid import uuid4
from pydub import AudioSegment
from werkzeug.datastructures.file_storage import FileStorage

from config import ConfigDevelopment
from . import db
from .models import User, Audiofile


def create_directory_data():
    """ Создает папку для сохранения файлов. """
    directory = Path('./data/audio/tmp/')
    if not os.path.exists(directory):
        os.makedirs(directory)


async def check_username(username: str) -> bool:
    """
    Проверяет существует ли пользователь с таким username.

    :param username: Имя пользователя для проверки.
    """
    try:
        user = User.query.filter_by(username=username).first()
    except Exception:
        raise Exception('Error DB')

    return True if user else False


async def check_user(user_id: int, token: str) -> bool:
    """
    Проверяет существует ли пользователь с таким user_id и token.

    :param user_id: ID пользователя.
    :param token: Токен пользователя.
    """
    try:
        user = User.query.filter_by(id=user_id, token=token).first()

    except Exception:
        raise Exception('Error DB')

    return user if user else None


async def get_user_data(auth_string: str) -> tuple[int, str]:
    """
    Преобразует строку данных авторизации в словарь с данными.
    Проверяет наличие необходимых полей: user_id и token.

    :param auth_string: Строка в заголовке 'Authorization'

    Возвращает user_id и token
    """
    try:
        dct = json.loads(auth_string[1:-1].strip())

        user_id = dct.get('user_id')
        token = dct.get('token')

        if not user_id or not token:
            raise

    except Exception:
        raise Exception('Error data Authorization'
                        'correct data: "{"user_id": str,"token": str}"')

    return user_id, token


async def allowed_file(filename: str) -> bool:
    """
    Функция проверки расширения файла для сохранения.

    :param filename: имя файла.
    """
    allowed_extensions = ConfigDevelopment.ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


class FileAudio:
    def __init__(self, file: FileStorage, user_id: int):
        self.file_tmp = file
        self.filename = str(uuid4().hex)
        self.filename_wav = self.filename + '.wav'
        self.filename_mp3 = self.filename + '.mp3'
        self.folder = ConfigDevelopment.UPLOAD_FOLDER
        self.folder_tmp = ConfigDevelopment.UPLOAD_FOLDER_TMP

        self.user_id = user_id

    async def load_and_convert(self):
        """ Загружает 'wav' файл и конвертирует в 'mp3' """
        try:
            await self._save_tmp()
            await self._convert()
            await self._del_tmp_file()
        except Exception:
            raise

    async def _save_tmp(self):
        """ Сохраняет файл во временное хранилище. """
        try:
            self.file_tmp.save(self.folder_tmp / self.filename_wav)
        except Exception as e:
            raise Exception(f'Error save temp file {e}')

        return True

    async def _convert(self) -> bool:
        """ Конвертирует файл из формата wav в mp3. """
        try:
            f_wav = self.folder_tmp / self.filename_wav
            f_mp3 = self.folder / self.filename_mp3

            sound = AudioSegment.from_mp3(f_wav)
            sound.export(f_mp3, format="wav")

            await self._save_in_db()

        except Exception:
            return False

        return True

    async def _save_in_db(self):
        """ Сохраняет информацию в БД. """
        try:
            audiofile = Audiofile(name=self.filename_mp3,
                                  user_id=self.user_id)

            db.session.add(audiofile)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise Exception('Error DB')

    async def _del_tmp_file(self) -> bool:
        """ Удаляет из временного хранилища успешно конвертированный файл. """
        try:
            path_del = self.folder_tmp / self.filename_wav

            if os.path.isfile(path_del):
                os.remove(path_del)
            else:
                raise

        except Exception:
            raise Exception('Error delete temp file')

        return True
