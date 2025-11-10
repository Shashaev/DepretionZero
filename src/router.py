import collections
import csv
import typing
import io

import aiogram
import aiogram.types
import aiogram.fsm.context as context
import aiogram.filters.command as command

import database.dao as dao
import questions
import markups
import database.models as models


router = aiogram.Router(name='main')


TEXT_START_MESSAGE: typing.Final[str] = '''
Привет! Я бот, который поможет тебе вести контроль за своими эмоциями. 

Доступные команды:
- /start_test: начните тест для измерения уровня тревоги и депрессии
- /my_data: отправляет всю собранную статистику в виде .csv файлов 
'''


@router.message(command.Command('start'))
async def cmd_start(message: aiogram.types.Message) -> None:
    if message.from_user is None:
        await message.answer('Пользователь скрыт. Пожалуста вскройте пользователя.')
        return 

    user_dao = dao.UserDAO()
    if not user_dao.is_user_exist(message.from_user.id):
        user_dao.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )

    await message.answer(TEXT_START_MESSAGE)


@router.message(command.Command('my_data'))
async def get_data(message: aiogram.types.Message) -> None:
    if message.from_user is None:
        await message.answer('Пользователь скрыт. Пожалуста вскройте пользователя.')
        return 

    user_dao = dao.UserDAO()
    # if not user_dao.is_user_exist(message.from_user.id):
    #     await message.answer('Пройденных тестов не обнаружено')
    #     return

    results: list[models.ResultModel] = user_dao.get_results(message.from_user.id)
    data = collections.defaultdict(list)
    for result in results:
        data[result.type_result].append(result.points)

    await message.answer('Отправляем данные...')
    for type_question in data:
        with io.StringIO() as csvfile:
            spamwriter = csv.writer(
                csvfile,
                quoting=csv.QUOTE_MINIMAL,
            )
            spamwriter.writerow([type_question])
            spamwriter.writerows([[el] for el in data[type_question]])
            csv_content = csvfile.getvalue().encode('utf-8')

        await message.answer_document(
            aiogram.types.input_file.BufferedInputFile(
                csv_content,
                f'{type_question.capitalize()}.csv',
            ),
        )


@router.message(command.Command('start_test'))
async def test(
    message: aiogram.types.Message,
    state: context.FSMContext,
) -> None:
    ind: int | None = await state.get_value('ind')
    if ind is not None:
        await message.answer('Прогресс прошлого прохождения теста был сброшен ☺')
    else:
        ind = 0

    await state.update_data(
        {
            'ind': ind,
        }
    )
    await message.answer('Тест начался!')
    await send_question(message, ind)


@router.callback_query()
async def get_callback_answer(
    call: aiogram.types.CallbackQuery,
    state: context.FSMContext,
) -> None:
    ind: int | None = await state.get_value('ind')
    if not isinstance(call.message, aiogram.types.Message):
        raise ValueError

    if (
        call.data is None
        or not call.message.from_user
    ):
        await call.message.answer(
            'Данные пользователя скрыты или другие проблемы. Сообщение не обработано.'
        )
        return

    if ind is None:
        await call.message.answer(
            'Тест еще не запущен. '
            'Для его запуска используйте команду /start_test.',
        )
        return

    type_question = questions.questions[ind].type
    answer_ind, points = map(int, call.data.split('_')[-2:])
    if ind != answer_ind:
        await call.message.answer(
            'Вы уже отвечали на этот вопрос. '
            'Пожалуйства следуйте тесту в правильном порядке',
        )
        return

    if (ind + 1) == len(questions.questions):
        data: dict[str, typing.Any] = await state.get_data()
        data[type_question] += points
        data = {
            type_question: data[type_question]
            for type_question in data
            if type_question != 'ind'
        }
        result_dao = dao.ResultDAO()
        user_dao = dao.UserDAO()
        user = user_dao.get_user_by_user_id(call.from_user.id)
        for type_question in data:
            result_dao.create(
                type_result=type_question,
                points=data[type_question],
                user_id=user.id_model,
            )

        await state.clear()
        await call.message.answer(
            f'Тест пройдён. Результаты:\n'
            f'{create_description_results(data)}')

        return

    ind += 1
    await state.update_data(
        {
            type_question: await state.get_value(type_question, 0) + points,
            'ind': ind,
        }
    )
    await send_question(call.message, ind)


async def send_question(
    message: aiogram.types.Message,
    ind: int,
) -> None:
    await message.answer(
        f'# Вопрос {ind + 1}\n'
        f'{questions.questions[ind].question}',
        reply_markup=markups.murkups[ind],
    )


def create_description_results(result: dict[str, int]) -> str:
    return '\n'.join(
        f'{key.capitalize()}: {result[key]} бал.'
        for key in result
    )
