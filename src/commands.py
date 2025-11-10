import aiogram.types


commands = [
    aiogram.types.BotCommand(
        command='/start_test',
        description='Начать тест',
    ),
    aiogram.types.BotCommand(
        command='/my_data',
        description='Получить всю информации о прохождении тестов',
    )
]
