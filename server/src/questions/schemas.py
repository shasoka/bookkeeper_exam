from schemas_config import MyBaseModel


class QuestionRead(MyBaseModel):
    id: int
    title: str
    answers: list[str]


class QuestionValidate(MyBaseModel):
    question_id: int
    chosen_answer: str


class QuestionValidationStatus(MyBaseModel):
    status: bool
    message: str
    correct_answer: str = None
