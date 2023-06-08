import uuid

from flask_marshmallow import Marshmallow

from . import db

ma = Marshmallow()


class User(db.Model):
    """Таблица пользователей.
        username: Имя пользователя.
        token: Уникальный токен пользователя.
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(250), nullable=False)

    def __init__(self, username):
        self.username = username
        self.token = str(uuid.uuid4())

    def __repr__(self):
        return f"<id:{self.id} - username:{self.username}>"


class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ('id', 'username', 'token')


class Audiofile(db.Model):
    """Таблица пользователей.
        name: Имя файла.
        user_id: ID пользователя.
    """
    __tablename__ = 'audiofile'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __repr__(self):
        return f"<id:{self.id} - user:{self.user_id} - path: {self.name} >"


class AudiofileSchema(ma.Schema):
    class Meta:
        model = Audiofile
        fields = ('id', 'name', 'user_id')
