from pathlib import Path

from flask import jsonify, request, send_file

from app import create_app, db
from app.models import User, Audiofile
from app.utils import check_username, check_user, get_user_data, \
    FileAudio, allowed_file, create_directory_data
from config import ConfigDevelopment


app = create_app()

create_directory_data()


@app.before_first_request
def create_table():
    db.create_all()


@app.route('/', methods=['GET'])
async def home():
    return jsonify({'page': 'home convertor'})


@app.route('/api/v1.0/user/', methods=['POST'])
async def create_user():
    """
    Добавляет пользователя.
    json в формате {"username": str}
    """
    try:
        new_username = request.json.get('username')
        # проверка имени добавляемого пользователя в запросе
        if not new_username:
            raise Exception('Not username new user')
        # проверка существует ли уже такой пользователь
        if await check_username(new_username):
            raise Exception('User already exists')
        # создание нового пользователя
        new_user = User(username=new_username)
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        return {'Error': f'{e}'}

    return jsonify({'id_user': new_user.id,
                    'token': new_user.token})


@app.route('/api/v1.0/audiofile/', methods=['POST'])
async def add_audiofile():
    """
    Добавляет аудиофайл.

    В заголовке 'Authorization' необходимо передать данные пользователя
    в формате строки  " {"user_id": str,"token": str} "

    """
    try:
        data_authorization = request.headers.get('Authorization')
        user_id, token = await get_user_data(data_authorization)

        user = await check_user(user_id, token)
        if not user:
            raise Exception('User Not registered')

        # проверим, передается ли в запросе файл
        if 'audiofile' not in request.files:
            raise Exception('Not file')

        file = request.files['audiofile']

        if file and await allowed_file(file.filename):
            file_audio = FileAudio(file=file, user_id=user_id)
            await file_audio.load_and_convert()

            link = (f"localhost:5000/"
                    f"record?id={file_audio.filename}&user={user_id}")

            return jsonify({"link_file": link})

    except Exception as e:
        return jsonify({'Error': f'{e}'})


@app.route('/record', methods=['GET'])
async def upload_audiofile():
    """
    Скачивает аудиофайл.
    В строке необходимо передать id записи, user_id пользователя.

    " ?id=id_записи&user=id_пользователя "

    """
    try:
        name = request.args.get('id')
        user_id = request.args.get('user')

        if not name or not user_id:
            return jsonify({'Error': 'Not need data in request'})
        filename = name + '.mp3'
        file = Audiofile.query.filter_by(name=filename,
                                         user_id=user_id).first()
        if not file:
            return jsonify({'Error': 'Such an audio file does not exist'})

        return send_file(Path('..') / ConfigDevelopment.UPLOAD_FOLDER / filename)

    except Exception as e:
        print(e)
        return jsonify({'Error': f'Upload file {e}'})


@app.errorhandler(405)
def method_not_allowed(e):
    """
    Метод для страницы запрещен.
    """
    return jsonify({'Error': f'Method <{request.method}> not allowed'}), 405


@app.errorhandler(404)
def page_not_found(e):
    """
    Страница не найдена.
    """
    return jsonify({'Error': 'Page NOT found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
