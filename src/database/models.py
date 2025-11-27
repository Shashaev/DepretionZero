import datetime
import typing

import sqlalchemy
import sqlalchemy.orm as orm
import sqlalchemy.sql


class Base(orm.DeclarativeBase):
    pass


class ModelWithPK(Base):
    __abstract__ = True
    id_model: orm.Mapped[int] = orm.mapped_column(primary_key=True)


class UserModel(ModelWithPK):
    __tablename__ = 'UserModel'
    user_id: orm.Mapped[int] = orm.mapped_column(unique=True)
    username: orm.Mapped[str]
    results: orm.Mapped[list['ResultModel']] = orm.relationship(
        back_populates='user',
    )


Rates = typing.Literal['1', '2', '3', '4', '5']


class ResultModel(ModelWithPK):
    __tablename__ = 'ResultModel'
    user_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('UserModel.id_model'),
    )
    user: orm.Mapped[UserModel] = orm.relationship(
        UserModel.__tablename__,
        back_populates='results',
    )
    answers: orm.Mapped[list['AnswerModel']] = orm.relationship(
        back_populates='result',
    )
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default=sqlalchemy.sql.func.now(),
    )
    points_depression: orm.Mapped[int]
    points_stress: orm.Mapped[int]
    sleep_quality: orm.Mapped[Rates]
    weather_quality: orm.Mapped[Rates] = orm.mapped_column(
        default=5,
    )


class AnswerModel(ModelWithPK):
    __tablename__ = 'AnswerModel'
    type_result: orm.Mapped[str]
    number: orm.Mapped[int]
    points: orm.Mapped[int]
    result_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('ResultModel.id_model'),
    )
    result: orm.Mapped[ResultModel] = orm.relationship(
        ResultModel.__tablename__,
        back_populates='answers',
    )

    def __str__(self) -> str:
        return f'{self.type_result}_{self.number + 1}'
