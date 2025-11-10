import typing

import sqlalchemy
import sqlalchemy.orm as orm

import settings
import database.models as models


engin = sqlalchemy.create_engine(settings.CONNECTION_STRING)
models.Base.metadata.create_all(engin)
Session = orm.sessionmaker(engin)


def db_connection[T, **P](
    fun: typing.Callable[P, T],
) -> typing.Callable[P, T]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        with Session() as session:
            kwargs['_session'] = session
            return fun(*args, **kwargs)

    return inner


def drop_db():
    models.Base.metadata.drop_all(engin)
