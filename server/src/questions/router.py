import random

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_async_session
from database.models import Question
from questions.schemas import QuestionRead, QuestionValidate, QuestionValidationStatus


SUCCESS_STATUSES = [
    'Красава',
    'Молодец',
    'Хорошо',
    'Нормалдаки',
    'Вы прекрасны, уважаемый',
    'Все как у людей',
    'Отлично справляешься',
    'Потрясающе',
    'Так держать!',
    'Победа!',
    'Супер!',
    'Мастерски!',
    'Невероятно!',
    'Великолепно!',
    'Восхитительно!',
    'Наливай! НАЛИВАЙ!!!',
    '5 баллов в диплом',
    'Грандиозный результат'
]

FAIL_STATUSES = [
    'Учись салага...',
    'Плаки-плаки)',
    'Ты че? Соберись, тут же все элементарно',
    'Мда, трэш.',
    'Затролен. Школьник.',
    'Я проанализировал ваш ответ. Вам следует вернуться на кухню.',
    'Было близко',
    'Наводчик контужен',
    'Броня не пробита',
    'Осечка',
    'Игра была ровна, играли два говна...',
    'Штирлиц еще никогда прежде не был так близок к провалу...',
    'Ну, попытка засчитана',
    'Это 2 балла в диплом. Железобетонно.',
]

router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"]
)


# noinspection PyTypeChecker
@router.get("/", response_model=list[QuestionRead])
async def get_questions(
        theme_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    questions = await session.execute(select(Question).where(Question.theme_id == theme_id))
    questions = questions.scalars().all()
    random.shuffle(questions)
    return questions


# noinspection PyTypeChecker
@router.post("/validate", response_model=QuestionValidationStatus)
async def validate_answer(
        user_input: QuestionValidate,
        session: AsyncSession = Depends(get_async_session)
):
    cur_question = await session.execute(select(Question).where(Question.id == user_input.question_id))
    cur_question = cur_question.scalar_one()
    if ''.join(sorted(cur_question.correct_answer.lower())) == ''.join(sorted(user_input.chosen_answer.lower())):
        return QuestionValidationStatus(
            status=True,
            message=random.choice(SUCCESS_STATUSES)
        )
    else:
        return QuestionValidationStatus(
            status=False,
            message=random.choice(FAIL_STATUSES),
            correct_answer=cur_question.correct_answer
        )
