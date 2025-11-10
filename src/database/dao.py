import typing

import sqlalchemy.orm as orm

import database.models as models
import database.connection as connection


_session = object()


class BaseDAO:
    def __init__(
        self: typing.Self,
        model: type[models.Base],
    ) -> None:
        self.model = model

    @connection.db_connection
    def create(
        self: typing.Self,
        *args: typing.Any,
        _session: orm.Session = _session,
        **kwargs,
    ) -> None:
        new_model = self.model(*args, **kwargs)
        _session.add(new_model)
        _session.commit()

    @connection.db_connection
    def select(
        self: typing.Self,
        pk: int,
        _session: orm.Session = _session,
    ) -> models.Base | None:
        return _session.get(self.model, pk)

    @connection.db_connection
    def select_all(
        self: typing.Self,
        _session: orm.Session = _session,
    ) -> list[models.Base]:
        return _session.query(self.model).all()

    @connection.db_connection
    def update(
        self: typing.Self,
        pk: int,
        _session: orm.Session = _session,
        **kwargs,
    ) -> None:
        model = self.select(pk)
        if model is None:
            return

        for key in kwargs:
            setattr(model, key, kwargs[key])

        _session.add(model)
        _session.commit()

    @connection.db_connection
    def delete(
        self: typing.Self,
        pk: int,
        _session: orm.Session = _session,
    ) -> None:
        _session.delete(self.select(pk))
        _session.commit()

    @connection.db_connection
    def delete_all(
        self: typing.Self,
        _session: orm.Session = _session,
    ) -> None:
        _session.query(self.model).delete()
        _session.commit()


class UserDAO(BaseDAO):
    model = models.UserModel

    @connection.db_connection
    def is_user_exist(
        self: typing.Self,
        user_id: int,
        _session: orm.Session = _session,
    ) -> bool:
        user = (
            _session.query(self.model)
            .filter(models.UserModel.user_id == user_id)
        )
        return bool(list(user))

    @connection.db_connection
    def get_user_by_user_id(
        self: typing.Self,
        user_id: int,
        _session: orm.Session = _session,
    ) -> models.UserModel:
        user = (
            _session.query(models.UserModel)
            .filter(models.UserModel.user_id == user_id)
            .first()
        )
        if user is None:
            raise ValueError

        return user

    @connection.db_connection
    def get_results(
        self: typing.Self,
        user_id: int,
        _session: orm.Session = _session,
    ) -> list[models.ResultModel]:
        user = (
            _session.query(models.UserModel)
            .filter(models.UserModel.user_id == user_id)
            .first()
        )
        if user is None:
            return []

        return user.results

    def __init__(self):
        super().__init__(self.model)


class ResultDAO(BaseDAO):
    model = models.ResultModel

    def __init__(self):
        super().__init__(self.model)
