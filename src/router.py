import collections
import csv
import typing
import io

import aiogram
import aiogram.types
import aiogram.fsm.context as context
import aiogram.filters.command as command
import aiogram.utils.markdown as markdown
import aiogram

import database.dao as dao
import database.models as models
import survey


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
        user = models.UserModel(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )
        user_dao.create(user)

    await message.answer(TEXT_START_MESSAGE)


@router.message(command.Command('my_data'))
async def get_data(message: aiogram.types.Message) -> None:
    if message.from_user is None:
        await message.answer('Пользователь скрыт. Пожалуста вскройте пользователя.')
        return 

    user_dao = dao.UserDAO()
    result_dao = dao.ResultDAO()
    results: list[models.ResultModel] = user_dao.get_results(message.from_user.id)
    data = collections.defaultdict(list)
    for result in results:
        data['created_at'].append(result.created_at.date())
        data['points_depression'].append(result.points_depression)
        data['points_stress'].append(result.points_stress)
        data['sleep_quality'].append(result.sleep_quality)
        data['weather_quality'].append(result.weather_quality)
        for answer in result_dao.get_answers(result):
            data[str(answer)].append(answer.points)

    await message.answer('Отправляем данные...')
    with io.StringIO() as csvfile:
        spamwriter = csv.writer(
            csvfile,
            quoting=csv.QUOTE_MINIMAL,
        )
        spamwriter.writerow(list(data.keys()))
        for i in range(len(data['created_at'])):
            spamwriter.writerow([data[key][i] for key in data])

        csv_content = csvfile.getvalue().encode('utf-8')

    await message.answer_document(
        aiogram.types.input_file.BufferedInputFile(
            csv_content,
            f'Data_{message.from_user.first_name}.csv',
        ),
    )


@router.message(command.Command('start_test'))
async def start_test(
    message: aiogram.types.Message,
    state: context.FSMContext,
) -> None:
    ind: int | None = await state.get_value('ind')
    if ind is not None:
        await message.answer('Прогресс прошлого прохождения теста был сброшен ☺')

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

    answer_ind, _ = map(int, call.data.split('_')[-2:])
    if ind != answer_ind:
        await call.message.answer(
            'Вы уже отвечали на этот вопрос. '
            'Пожалуйства следуйте тесту в правильном порядке',
        )
        return

    ind += 1
    data: list[str] = await state.get_value('data', [])
    data.append(call.data)
    result: models.ResultModel | None = None
    if ind == len(survey.labels_survey):
        result = survey_processing(data, call.from_user.id)
        await state.clear()
    else:
        await state.update_data(
            {
                'data': data,
                'ind': ind,
            },
        )

    await send_question(call.message, ind, result)


def survey_processing(data: list[str], id_user: int) -> models.ResultModel:
    user = dao.UserDAO().get_user_by_user_id(id_user)
    result_dao = dao.ResultDAO()
    answer_dao = dao.AnswerDAO()
    result_model = models.ResultModel(
        user_id=user.id_model,
        points_depression=0,
        points_stress=0,
        sleep_quality='0',
        weather_quality='0',
    )
    answers: list[models.AnswerModel] = []
    for el in data:
        if el.startswith('data_question'):
            type_question, answer_ind, points = el.split('_')[-3:]
            answer_ind, points = int(answer_ind), int(points)
            if type_question == 'депрессия':
                result_model.points_depression += points
            else:
                result_model.points_stress += points

            answers.append(
                models.AnswerModel(
                    type_result=type_question,
                    number=answer_ind,
                    points=points,
                    result_id=0,
                ),
            )
        elif el.startswith('sleep_quality'):
            result_model.sleep_quality = el.split('_')[-1]
        else:
            result_model.weather_quality = el.split('_')[-1]

    result_model = result_dao.create(result_model)
    for answer in answers:
        answer.result_id = result_model.id_model
        answer_dao.create(answer)

    return result_model


async def send_question(
    message: aiogram.types.Message,
    ind: int,
    result: models.ResultModel | None = None,
) -> bool:
    if ind >= len(survey.labels_survey):
        await message.answer(
            f'Тест пройдён. Результаты:\n'
            f'{create_description_results(result)}',
            parse_mode='HTML',
        )
        return False

    await message.answer(
        survey.labels_survey[ind],
        reply_markup=survey.markups_survey[ind],
    )
    return True


def _score_to_name(score: int) -> str:
    if score <= 7:
        return 'Норма'
    elif score <= 10:
        return 'Субклиническая выраженность'

    return 'Клиническая выраженность'


def create_description_results(result: models.ResultModel) -> str:
    return '\n'.join(
        f'{name}: {points} бал. — <b>{_score_to_name(points)}</b>'
        for name, points in [
            ('Депрессия', result.points_depression),
            ('Тревога', result.points_stress),
        ]
    )
