import typing

import pydantic


class AnswerScheme(pydantic.BaseModel):
    answer: str = pydantic.Field(
        examples=['совсем не испытываю', 'часто', 'нет'],
        min_length=1,
        title='Ответ на вопрос',
        description='Один из ответов на вопрос, не может быть пустой строкой.',
    )
    points: typing.Literal[0, 1, 2, 3] = pydantic.Field(
        title='Баллы',
        description=(
            'Кол-во баллов, которое даётся за выбор'
            ' текущего ответа. Может только 0, 1, 2, 3.'
        ),
    )


class QuestionSchemes(pydantic.BaseModel):
    type: typing.Literal['тревога', 'депрессия'] = pydantic.Field(
        title='Тип',
        description=(
            'Тип вопроса. Один из двух '
            'вариантов: "тревога", "депрессия".'
        )
    )
    question: str = pydantic.Field(
        examples=[
            'У меня бывает внезапное чувство паники',
            'Я легко могу сесть и расслабиться',
        ],
        min_length=1,
        title='Вопрос',
        description='Текст вопроса. Не может быть пустой строкой.',
    )
    answers: list[AnswerScheme] = pydantic.Field(
        min_length=1,
        title='Ответы',
        description='Список ответов на текущий вопрос.'
    )
