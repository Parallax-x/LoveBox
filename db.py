import sqlalchemy as sq
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import os

password = os.getenv('password')
engine = sq.create_engine(f'postgresql://postgres:{password}@localhost:5432/LoveBox')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    dating_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    age_from = sq.Column(sq.Integer)
    age_to = sq.Column(sq.Integer)
    city = sq.Column(sq.String)
    partners_sex = sq.Column(sq.Integer)
    matchingusers = relationship('MatchingUser', backref='User')
    blacklistedusers = relationship('BlacklistedUser', backref='User')

    def __str__(self):
        return f'User {self.dating_id}: {self.first_name}, {self.last_name}'


class MatchingUser(Base):
    __tablename__ = 'MatchingUser'

    matching_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    id_dater = sq.Column(sq.Integer, sq.ForeignKey('User.dating_id'))
    photos = relationship('Photos', backref='MatchingUser')
    sex = sq.Column(sq.Integer)

    def __str__(self):
        return f'MatchingUser {self.matching_id}: {self.first_name}, {self.last_name}, {self.id_dater}'


class Photos(Base):
    __tablename__ = 'Photos'

    photo_id = sq.Column(sq.Integer, primary_key=True)
    id_matcher = sq.Column(sq.Integer, sq.ForeignKey('MatchingUser.matching_id'))
    photo_link = sq.Column(sq.String)
    likes_count = sq.Column(sq.Integer)

    def __str__(self):
        return f'Photos {self.photo_id}: {self.id_matcher}, {self.photo_link}'


class BlacklistedUser(Base):
    __tablename__ = 'BlacklistedUser'

    blacklisted_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    id_dater = sq.Column(sq.Integer, sq.ForeignKey('User.dating_id'))

    def __str__(self):
        return f'BlacklistedUser {self.blacklisted_id}: {self.first_name}, {self.last_name}'


def create_table(engine_):
    """Функция создает таблицу в базе данных"""
    Base.metadata.create_all(engine_)
    print('Таблицы созданы')


def drop_table(engine_):
    """Функция удаляет все таблицы из базы данных"""
    Base.metadata.drop_all(engine_)
    print('Таблицы удалены')
