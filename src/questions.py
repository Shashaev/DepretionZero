import pydantic

import settings
import schemes


_raw_text = settings.PATH_TO_QUESTION.read_text(encoding='UTF-8')
_questions_adapter = pydantic.TypeAdapter(list[schemes.QuestionSchemes])
questions = _questions_adapter.validate_json(_raw_text)
