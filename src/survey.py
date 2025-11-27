import aiogram.types

import questions

labels_survey: list[str] = []
markups_survey: list[aiogram.types.InlineKeyboardMarkup] = []


def _add_question(
    label: str,
    murkup: aiogram.types.InlineKeyboardMarkup,
) -> None:
    labels_survey.append(f'# Вопрос {len(labels_survey) + 1}\n{label}')
    markups_survey.append(murkup)


for ind, question in enumerate(questions.questions):
    _markup = aiogram.types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                aiogram.types.InlineKeyboardButton(
                    text=answer.answer,
                    callback_data=f'data_question_{question.type}_{ind}_{answer.points}',
                )
            ]
            for answer in question.answers
        ],
    )
    _add_question(question.question, _markup)


def _get_markup_rate(
    prefix_callback_data: str,
    max_rate: int = 5,
    min_rate: int = 1,
) -> aiogram.types.InlineKeyboardMarkup:
    ind = len(labels_survey)
    return aiogram.types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                aiogram.types.InlineKeyboardButton(
                    text=f'{i}',
                    callback_data=f'{prefix_callback_data}_{ind}_{i}',
                )
            ]
            for i in range(min_rate, max_rate + 1)
        ],
    )


_add_question(
    'Оцените качество сна',
    _get_markup_rate('sleep_quality'),
)
_add_question(
    'Оцените качество погоды',
    _get_markup_rate('weather_quality'),
)
