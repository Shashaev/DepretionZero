import os
import pathlib

import dotenv


dotenv.load_dotenv()

TOKEN = os.getenv('TG_TOKEN', '')
PATH_TO_QUESTION = pathlib.Path(
    os.getenv(
        'TG_PATH_TO_QUESTION',
        'question.json',
    ),
)
DB_USER = os.getenv('TG_DB_USER')
DB_PASSWORD = os.getenv('TG_DB_PASSWORD')
DB_HOST = os.getenv('TG_DB_HOST')
DB_PORT = os.getenv('TG_DB_PORT')
DB_NAME = os.getenv('TG_DB_NAME')
if DB_USER:
    CONNECTION_STRING = (
        f'postgresql+asyncpg://{DB_USER}:'
        f'{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
else:
    PATH_DB = pathlib.Path(__file__).parent / "database.db"
    CONNECTION_STRING = f'sqlite:///{str(PATH_DB)}'
