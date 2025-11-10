import aiogram.types

import questions


murkups = [
    aiogram.types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                aiogram.types.InlineKeyboardButton(
                    text=answer.answer,
                    callback_data=f'data_question_{ind}_{answer.points}',
                )
            ]
            for answer in question.answers
        ]
    )
    for ind, question in enumerate(questions.questions)
]
