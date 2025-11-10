import sqlalchemy
import sqlalchemy.orm as orm


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


class ResultModel(ModelWithPK):
    __tablename__ = 'ResultModel'
    type_result: orm.Mapped[str]
    points: orm.Mapped[int]
    user_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('UserModel.id_model'),
    )
    user: orm.Mapped[UserModel] = orm.relationship(
        UserModel.__tablename__,
        back_populates='results',
    )
