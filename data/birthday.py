import sqlalchemy

from .db_session import SqlAlchemyBase


class Birthday(SqlAlchemyBase):
    __tablename__ = 'birthday'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    dt = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fio = sqlalchemy.Column(sqlalchemy.String, nullable=True)
